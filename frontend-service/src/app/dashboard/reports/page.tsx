'use client';

import { useEffect, useState, useRef } from 'react';
import {
  getPatients,
  getPatient,
  listAllReports,
  getReport,
  getRagStatus,
  triggerRagReindex
} from '@/lib/api';
import PageContainer from '@/components/layout/page-container';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription
} from '@/components/ui/dialog';
import {
  FileText,
  Loader2,
  RefreshCw,
  Eye,
  AlertCircle,
  CheckCircle2,
  Database,
  Sparkles
} from 'lucide-react';
import { toast } from 'sonner';
import type { Report, ReportStatus } from '@/types';

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
  const [detailOpen, setDetailOpen] = useState(false);
  const [patientNames, setPatientNames] = useState<Record<string, string>>({});
  
  // RAG state
  const [ragStatus, setRagStatus] = useState<{
    status: string;
    schema_version?: string;
    run_id?: string;
    artifact_count: number;
  } | null>(null);
  const [ragLoading, setRagLoading] = useState(false);
  const [reindexing, setReindexing] = useState(false);

  useEffect(() => {
    loadReports();
    loadRagStatus();
  }, []);

  const loadRagStatus = async () => {
    try {
      setRagLoading(true);
      const status = await getRagStatus();
      setRagStatus(status);
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

  const viewReportDetails = async (report: Report) => {
    try {
      const fullReport = await getReport(report.id);
      setSelectedReport(fullReport);
      setDetailOpen(true);
    } catch (err) {
      console.error('Failed to load report details:', err);
      toast.error('Failed to load report details');
    }
  };

  const formatContent = (content: string | null): string => {
    if (!content) return '';
    return content;
  };

  return (
    <PageContainer>
      <div className="flex flex-col gap-8">
        {/* Hero */}
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#0a2e3e] via-[#0d3a4c] to-[#104a5e] p-10 text-white">
          <div className="absolute right-0 top-0 h-full w-1/3 opacity-10">
            <div className="h-full w-full bg-gradient-to-br from-white/20 to-transparent" />
          </div>
          <div className="relative z-10">
            <h1 className="mb-2 text-3xl font-bold tracking-tight">Reports</h1>
            <p className="max-w-xl text-lg text-white/70">
              LLM-generated clinical reports and summaries powered by AI
            </p>
          </div>
        </div>

        {/* RAG Status Card */}
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

        {/* Reports List */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Clinical Reports</CardTitle>
              <CardDescription>
                View and manage AI-generated clinical reports
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={loadReports}>
                <RefreshCw className="mr-2 h-4 w-4" />
                Refresh
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {reportsLoading ? (
              <div className="py-8 text-center">
                <Loader2 className="mx-auto h-8 w-8 animate-spin text-muted-foreground" />
                <p className="mt-2 text-muted-foreground">Loading reports...</p>
              </div>
            ) : reports.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12">
                <FileText className="mb-4 h-16 w-16 text-muted-foreground" />
                <p className="text-muted-foreground">
                  No reports generated yet. Generate reports from completed predictions.
                </p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Patient</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>LLM Model</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {reports.map((report) => (
                    <TableRow key={report.id}>
                      <TableCell className="font-medium">
                        {patientNames[report.patient_id] || 'Loading...'}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant="outline"
                          className={`${STATUS_COLORS[report.status]} text-white`}
                        >
                          {STATUS_LABELS[report.status]}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-muted-foreground">
                          {report.llm_model || '—'}
                        </span>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {new Date(report.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => viewReportDetails(report)}
                          disabled={report.status !== 'completed'}
                        >
                          <Eye className="mr-2 h-4 w-4" />
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Report Detail Dialog */}
        <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
          <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Clinical Report
              </DialogTitle>
              <DialogDescription>
                {selectedReport && (
                  <>
                    Patient: {patientNames[selectedReport.patient_id] || 'Unknown'} | 
                    Generated: {new Date(selectedReport.created_at).toLocaleString()}
                  </>
                )}
              </DialogDescription>
            </DialogHeader>
            {selectedReport && (
              <div className="space-y-4 overflow-y-auto max-h-[60vh]">
                {/* Status */}
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">Status:</span>
                  <Badge
                    variant="outline"
                    className={`${STATUS_COLORS[selectedReport.status]} text-white`}
                  >
                    {STATUS_LABELS[selectedReport.status]}
                  </Badge>
                </div>

                {/* Summary Card */}
                {selectedReport.summary && (
                  <Card className="bg-muted/50">
                    <CardHeader>
                      <CardTitle className="text-sm">Summary</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm">{selectedReport.summary}</p>
                    </CardContent>
                  </Card>
                )}

                {/* Report Content */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Detailed Report</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {selectedReport.content ? (
                      <div className="text-sm whitespace-pre-wrap">
                        {formatContent(selectedReport.content)}
                      </div>
                    ) : (
                      <p className="text-muted-foreground">No content available</p>
                    )}
                  </CardContent>
                </Card>

                {/* Metadata */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Metadata</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Report ID:</span>
                        <code className="rounded bg-muted px-1">{selectedReport.id}</code>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Prediction ID:</span>
                        <code className="rounded bg-muted px-1">{selectedReport.prediction_id}</code>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">LLM Model:</span>
                        <span>{selectedReport.llm_model || '—'}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </PageContainer>
  );
}
