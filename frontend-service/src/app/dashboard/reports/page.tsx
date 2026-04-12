'use client';

import { useEffect, useState } from 'react';
import { motion, useReducedMotion } from 'motion/react';
import {
  getPatients,
  getPatient,
  listAllReports,
  getReport,
  getRagStatus,
  triggerRagReindex,
  checkLlmoopsHealth,
  getOperationStatus,
  type OperationStatus
} from '@/lib/api';
import PageContainer from '@/components/layout/page-container';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  FileText,
  Loader2,
  RefreshCw,
  Search,
  Eye,
  AlertCircle,
  CheckCircle2,
  Database,
  Sparkles,
  WifiOff,
  Bot,
  Calendar,
  FileCheck,
  Clock,
  AlertTriangle
} from 'lucide-react';
import { toast } from 'sonner';
import type { Report, ReportStatus } from '@/types';
import { fadeInUp, slideInUp, staggerItemFast, buttonTap, statusPulse } from '@/lib/animations';
import { ReportCard } from '@/components/reports/ReportCard';
import { ReportFilters } from '@/components/reports/ReportFilters';
import { StatsCard } from '@/components/ui/stats-card';
import Image from 'next/image';
import { useWebSocket } from '@/hooks/use-websocket';

type FilterStatus = 'all' | 'completed' | 'pending' | 'running' | 'failed';

const STATUS_COLORS: Record<ReportStatus, string> = {
  pending: 'bg-yellow-500',
  running: 'bg-blue-500',
  completed: 'bg-green-500',
  failed: 'bg-red-500'
};

const STATUS_LABELS: Record<ReportStatus, string> = {
  pending: 'Pending',
  running: 'Generating',
  completed: 'Completed',
  failed: 'Failed'
};

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [reportsLoading, setReportsLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [patientNames, setPatientNames] = useState<Record<string, string>>({});
  const [expandedReportId, setExpandedReportId] = useState<string | null>(null);
  const shouldReduceMotion = useReducedMotion();
  
  // Filter states
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<FilterStatus>('all');
  
  // RAG state
  const [ragStatus, setRagStatus] = useState<{
    status: string;
    schema_version?: string;
    run_id?: string;
    artifact_count: number;
  } | null>(null);
  const [ragLoading, setRagLoading] = useState(false);
  const [reindexing, setReindexing] = useState(false);
  const [llmopsDown, setLlmopsDown] = useState(false);
  const [operation, setOperation] = useState<OperationStatus | null>(null);

  const { connected, subscribe } = useWebSocket();

  // WebSocket subscription for operation status
  useEffect(() => {
    const unsub = subscribe('llmops_event', (data) => {
      const event = data as { event: string; data: { status: string; progress: number; message: string; details?: Record<string, unknown> } };
      const { status, progress, message, details } = event.data;
      
      // Update operation state from WebSocket
      if (details?.state) {
        setOperation({
          state: details.state as string,
          message: message,
          progress: progress,
          started_at: new Date().toISOString(),
        });
      }

      // Show toast notifications
      if (status === 'completed') {
        toast.success(message || 'Operation completed');
      } else if (status === 'failed') {
        toast.error(message || 'Operation failed');
      } else if (status === 'running') {
        toast(message || 'Processing...', { icon: '🔄' });
      }
    });

    return () => {
      unsub();
    };
  }, [subscribe]);

  // Initial load
  useEffect(() => {
    loadReports();
    loadRagStatus();
  }, []);

  const loadRagStatus = async () => {
    try {
      setRagLoading(true);
      setLlmopsDown(false);
      
      try {
        await checkLlmoopsHealth();
      } catch {
        setLlmopsDown(true);
        return;
      }
      
      const status = await getRagStatus();
      setRagStatus(status);
      
      try {
        const op = await getOperationStatus();
        setOperation(op);
      } catch {
        setOperation(null);
      }
    } catch (err) {
      console.error('Failed to load RAG status:', err);
      setRagStatus({ status: 'error', artifact_count: 0 });
    } finally {
      setRagLoading(false);
    }
  };

  const handleReindex = async () => {
    try {
      setReindexing(true);
      await triggerRagReindex();
      toast.success('RAG reindexing started');
      await loadRagStatus();
    } catch (err) {
      console.error('Failed to trigger reindex:', err);
      toast.error(err instanceof Error ? err.message : 'Failed to trigger reindex');
    } finally {
      setReindexing(false);
    }
  };

  const loadReports = async () => {
    try {
      setReportsLoading(true);
      const response = await listAllReports(1, 50);
      setReports(response.items);
      
      const patientIds = [...new Set(response.items.map((r) => r.patient_id))];
      const names: Record<string, string> = { ...patientNames };
      
      for (const pid of patientIds) {
        if (!names[pid]) {
          try {
            const patient = await getPatient(pid);
            names[pid] = `${patient.first_name} ${patient.last_name}`;
          } catch {
            names[pid] = 'Unknown';
          }
        }
      }
      setPatientNames(names);
    } catch (err) {
      console.error('Failed to load reports:', err);
      toast.error('Failed to load reports');
    } finally {
      setReportsLoading(false);
    }
  };

  const toggleReportExpand = async (report: Report) => {
    if (expandedReportId === report.id) {
      setExpandedReportId(null);
    } else {
      if (!selectedReport || selectedReport.id !== report.id) {
        try {
          const fullReport = await getReport(report.id);
          setSelectedReport(fullReport);
        } catch (err) {
          console.error('Failed to load report details:', err);
          toast.error('Failed to load report details');
        }
      }
      setExpandedReportId(report.id);
    }
  };

  // Filter reports based on search and status
  const filteredReports = reports.filter((report) => {
    const matchesSearch = !search || 
      patientNames[report.patient_id]?.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'all' || report.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  // Calculate stats
  const totalReports = reports.length;
  const completedReports = reports.filter(r => r.status === 'completed').length;
  const pendingReports = reports.filter(r => r.status === 'pending' || r.status === 'running').length;
  const failedReports = reports.filter(r => r.status === 'failed').length;
  const successRate = totalReports > 0 ? Math.round((completedReports / totalReports) * 100) : 0;

  return (
    <PageContainer>
      <motion.div
        variants={shouldReduceMotion ? {} : fadeInUp}
        initial="hidden"
        animate="visible"
        className="flex flex-col gap-8"
      >
        {/* Hero with Medical Image */}
        <motion.div
          variants={shouldReduceMotion ? {} : slideInUp}
          className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#0a2e3e] via-[#0d3a4c] to-[#104a5e] p-10 text-white"
        >
          <div className="absolute right-0 top-0 h-full w-1/3 opacity-20">
            <Image
              src="https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=800&q=80"
              alt="Medical Technology"
              fill
              className="object-cover"
              unoptimized
            />
          </div>
          {/* Decorative accent shapes */}
          <div className="absolute -bottom-20 -left-20 h-40 w-40 rounded-full bg-[#20bdbe]/10 blur-3xl" />
          <div className="absolute top-10 right-20 h-24 w-24 rounded-full bg-[#c8a951]/10 blur-2xl" />
          
          <div className="relative z-10">
            <h1 className="mb-2 text-3xl font-bold tracking-tight">Clinical Reports</h1>
            <p className="max-w-xl text-lg text-white/70">
              AI-generated clinical reports powered by LLM with retrieval-augmented generation
            </p>
          </div>
        </motion.div>

        {/* Stats Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatsCard
            title="Total Reports"
            value={totalReports}
            icon={FileText}
            subtitle="All time"
          />
          <StatsCard
            title="Completed"
            value={completedReports}
            icon={FileCheck}
            color="#22c55e"
          />
          <StatsCard
            title="In Progress"
            value={pendingReports}
            icon={Clock}
            color="#3b82f6"
          />
          <StatsCard
            title="Success Rate"
            value={`${successRate}%`}
            icon={CheckCircle2}
            color={successRate >= 80 ? '#22c55e' : successRate >= 50 ? '#eab308' : '#ef4444'}
          />
        </div>

        {/* Operation Status Card */}
        {operation && operation.state !== 'idle' && (
          <motion.div variants={shouldReduceMotion ? {} : slideInUp}>
            <Card className={operation.state === 'error' ? 'border-destructive bg-red-50' : 'border-primary'}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {operation.state === 'indexing' && <motion.div variants={shouldReduceMotion ? {} : statusPulse}><Database className="h-5 w-5" /></motion.div>}
                  {operation.state === 'retrieving' && <motion.div variants={shouldReduceMotion ? {} : statusPulse}><Search className="h-5 w-5" /></motion.div>}
                  {operation.state === 'generating' && <motion.div variants={shouldReduceMotion ? {} : statusPulse}><Sparkles className="h-5 w-5" /></motion.div>}
                  {operation.state === 'error' && <AlertCircle className="h-5 w-5 text-destructive" />}
                  {operation.state === 'indexing' && 'Indexing RAG'}
                  {operation.state === 'retrieving' && 'Retrieving Context'}
                  {operation.state === 'generating' && 'Generating Report'}
                  {operation.state === 'error' && 'Error'}
                </CardTitle>
                <CardDescription className={operation.state === 'error' ? 'text-destructive font-medium' : ''}>
                  {operation.message}
                </CardDescription>
              </CardHeader>
            </Card>
          </motion.div>
        )}

        {/* RAG Status Card - Service Down */}
        {llmopsDown ? (
          <motion.div variants={shouldReduceMotion ? {} : slideInUp}>
            <Card className="border-destructive">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-destructive">
                  <WifiOff className="h-5 w-5" />
                  LLMOps Service Unavailable
                </CardTitle>
                <CardDescription>
                  The LLMOps service is currently down or unreachable.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-4">
                  <div className="h-2 w-2 animate-pulse rounded-full bg-destructive" />
                  <span className="text-sm text-muted-foreground">
                    Attempting to reconnect...
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={loadRagStatus}
                    disabled={ragLoading}
                  >
                    <RefreshCw className={`mr-2 h-4 w-4 ${ragLoading ? 'animate-spin' : ''}`} />
                    Retry
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ) : (
          <motion.div variants={shouldReduceMotion ? {} : slideInUp}>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="h-5 w-5" />
                    RAG Index
                  </CardTitle>
                  <CardDescription>
                    Current state of the Retrieval-Augmented Generation index
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={loadRagStatus}
                    disabled={ragLoading}
                  >
                    <RefreshCw className={`mr-2 h-4 w-4 ${ragLoading ? 'animate-spin' : ''}`} />
                    Refresh
                  </Button>
                  <Button
                    variant="default"
                    size="sm"
                    onClick={handleReindex}
                    disabled={reindexing}
                  >
                    {reindexing ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <Sparkles className="mr-2 h-4 w-4" />
                    )}
                    Reindex
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
            {ragLoading && !ragStatus ? (
              <div className="py-4 text-center">
                <Loader2 className="mx-auto h-6 w-6 animate-spin text-muted-foreground" />
              </div>
            ) : ragStatus ? (
              <div className="grid gap-4 md:grid-cols-4">
                <div>
                  <p className="text-sm text-muted-foreground">Status</p>
                  <Badge
                    variant="outline"
                    className={
                      ragStatus.status === 'ok'
                        ? 'bg-green-500 text-white'
                        : ragStatus.status === 'idle'
                        ? 'bg-yellow-500 text-white'
                        : 'bg-red-500 text-white'
                    }
                  >
                    {ragStatus.status}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Artifacts</p>
                  <p className="text-2xl font-bold">{ragStatus.artifact_count}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Schema Version</p>
                  <p className="font-mono text-sm">{ragStatus.schema_version || '—'}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Run ID</p>
                  <p className="font-mono text-sm truncate">{ragStatus.run_id || '—'}</p>
                </div>
              </div>
            ) : (
              <p className="text-muted-foreground">Unable to load RAG status</p>
            )}
          </CardContent>
        </Card>
        </motion.div>
        )}

        {/* Reports List with Filters */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-4">
            <div>
              <CardTitle>Clinical Reports</CardTitle>
              <CardDescription>
                {filteredReports.length} of {reports.length} reports
              </CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={loadReports}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh
            </Button>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Filters */}
            <ReportFilters
              search={search}
              onSearchChange={setSearch}
              status={statusFilter}
              onStatusChange={setStatusFilter}
            />

            {/* Reports Grid */}
            {reportsLoading ? (
              <div className="py-8 text-center">
                <Loader2 className="mx-auto h-8 w-8 animate-spin text-muted-foreground" />
                <p className="mt-2 text-muted-foreground">Loading reports...</p>
              </div>
            ) : filteredReports.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12">
                <div className="relative mb-4">
                  <FileText className="h-16 w-16 text-muted-foreground/30" />
                  <div className="absolute -top-2 -right-2 h-8 w-8 rounded-full bg-[#20bdbe]/20 flex items-center justify-center">
                    <Search className="h-4 w-4 text-[#20bdbe]" />
                  </div>
                </div>
                <p className="text-muted-foreground text-center">
                  {search || statusFilter !== 'all' 
                    ? 'No reports match your filters'
                    : 'No reports generated yet'
                  }
                </p>
                <p className="text-sm text-muted-foreground/70 mt-1">
                  {search || statusFilter !== 'all' 
                    ? 'Try adjusting your search or filters'
                    : 'Generate reports from completed predictions'
                  }
                </p>
              </div>
            ) : (
              <div className="grid gap-4">
                {filteredReports.map((report) => (
                  <ReportCard
                    key={report.id}
                    report={report}
                    patientName={patientNames[report.patient_id] || 'Loading...'}
                    expanded={expandedReportId === report.id}
                    onExpand={() => toggleReportExpand(report)}
                  />
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </PageContainer>
  );
}
