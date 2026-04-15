'use client';

import { useEffect, useState } from 'react';
import { motion, useReducedMotion } from 'motion/react';
import { apiFetch } from '@/lib/auth';
import PageContainer from '@/components/layout/page-container';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Image from 'next/image';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  AreaChart,
  Area,
} from 'recharts';
import { fadeInUp, slideInUp, staggerItem } from '@/lib/animations';
import { 
  RefreshCw, 
  Users, 
  FileText, 
  Scan, 
  Activity, 
  TrendingUp,
  TrendingDown,
  Calendar,
  BarChart3,
  PieChart as PieChartIcon,
  Activity as ActivityIcon
} from 'lucide-react';

const COLORS = ['var(--brand-teal)', 'var(--brand-gold)', '#e74c3c', '#3498db', '#9b59b6', '#2ecc71'];
const GRADE_COLORS: Record<string, string> = {
  no_dr: '#2ecc71',
  mild: 'var(--brand-teal)',
  moderate: 'var(--brand-gold)',
  severe: '#e67e22',
  proliferative: '#e74c3c',
  0: '#2ecc71',
  1: 'var(--brand-teal)',
  2: 'var(--brand-gold)',
  3: '#e67e22',
  4: '#e74c3c',
};

interface CombinedStats {
  summary: {
    total_patients: number;
    total_oct_reports: number;
    total_clinical_reports: number;
    total_predictions: number;
  };
  recent_activity: {
    patients_7d: number;
    patients_30d: number;
    predictions_7d: number;
    reports_7d: number;
  };
  patient_demographics: {
    gender: Record<string, number>;
    age_groups: Record<string, number>;
  };
  clinical_reports: {
    total: number;
    status: Record<string, number>;
  };
  predictions: {
    total: number;
    status: Record<string, number>;
    severity_distribution: Record<number, number>;
  };
  oct_reports: {
    total: number;
    grade_distribution: Record<string, number>;
    eye_distribution: Record<string, number>;
    edema: { present: number; absent: number };
    erm_distribution: Record<string, number>;
    thickness_averages: {
      center_fovea: number | null;
      average_thickness: number | null;
      total_volume_mm3: number | null;
    };
    avg_image_quality: number | null;
  };
}

export default function VisualisePage() {
  const [stats, setStats] = useState<CombinedStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const shouldReduceMotion = useReducedMotion();

  const loadStats = async () => {
    try {
      setLoading(true);
      console.log('[Visualise] Fetching data...');
      const data = await apiFetch<CombinedStats>('/api/v1/oct-stats/stats');
      console.log('[Visualise] Received data:', JSON.stringify(data, null, 2));
      setStats(data);
      setLastUpdated(new Date());
    } catch (err: unknown) {
      const error = err as { status?: number };
      if (error.status === 401) {
        window.location.href = '/auth/login';
      } else {
        console.error('[Visualise] Failed to fetch stats:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  if (loading) {
    return (
      <div className='flex h-full items-center justify-center'>
        <p className='text-muted-foreground'>Loading analytics...</p>
      </div>
    );
  }

  if (!stats) {
    return (
      <PageContainer>
        <div className="flex h-96 items-center justify-center">
          <div className="text-center">
            <p className="text-muted-foreground mb-4">No data available</p>
            <Button onClick={loadStats} variant="outline">
              <RefreshCw className="mr-2 h-4 w-4" />
              Load Data
            </Button>
          </div>
        </div>
      </PageContainer>
    );
  }

  console.log('[Visualise] Rendering with stats:', stats);

  const { summary, recent_activity, patient_demographics, clinical_reports, predictions, oct_reports } = stats;

  // Transform data for charts
  const genderData = Object.entries(patient_demographics.gender).map(([key, val]) => ({
    name: key === 'M' ? 'Male' : key === 'F' ? 'Female' : 'Other',
    value: val,
  }));

  const ageData = Object.entries(patient_demographics.age_groups).map(([key, val]) => ({
    name: key,
    value: val,
  }));

  const severityData = Object.entries(predictions.severity_distribution).map(([key, val]) => ({
    name: ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative'][parseInt(key)] || key,
    value: val,
    fill: GRADE_COLORS[key] || 'var(--brand-teal)',
  }));

  const octGradeData = Object.entries(oct_reports.grade_distribution).map(([grade, count]) => ({
    name: grade.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
    value: count,
    fill: GRADE_COLORS[grade] || 'var(--brand-teal)',
  }));

  const eyeData = Object.entries(oct_reports.eye_distribution).map(([eye, count]) => ({
    name: eye === 'OD' ? 'Right Eye (OD)' : 'Left Eye (OS)',
    value: count,
  }));

  const edemaData = [
    { name: 'Present', value: oct_reports.edema.present },
    { name: 'Absent', value: oct_reports.edema.absent },
  ];

  const reportStatusData = Object.entries(clinical_reports.status).map(([key, val]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    value: val,
  }));

  const predStatusData = Object.entries(predictions.status).map(([key, val]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    value: val,
  }));

  const thicknessData = [
    { name: 'Center Fovea', value: oct_reports.thickness_averages.center_fovea || 0 },
    { name: 'Average', value: oct_reports.thickness_averages.average_thickness || 0 },
    { name: 'Total Volume', value: oct_reports.thickness_averages.total_volume_mm3 || 0 },
  ];

  const getSeverityColor = (level: number) => {
    const colors = ['#2ecc71', 'var(--brand-teal)', 'var(--brand-gold)', '#e67e22', '#e74c3c'];
    return colors[level] || 'var(--brand-teal)';
  };

  return (
    <PageContainer>
      <motion.div
        variants={shouldReduceMotion ? {} : fadeInUp}
        initial="hidden"
        animate="visible"
        className="flex flex-col gap-8"
      >
        {/* Hero */}
        <motion.div
          variants={shouldReduceMotion ? {} : slideInUp}
          className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#0a2e3e] via-[#0d3a4c] to-[#104a5e] p-10 text-white"
        >
          <div className="absolute right-0 top-0 h-full w-1/3 opacity-15">
            <Image
              src="https://images.unsplash.com/photo-1551076805-e1869033e561?w=800&q=80"
              alt="Analytics"
              fill
              className="object-cover"
              unoptimized
            />
          </div>
          <div className="absolute -bottom-10 -left-10 h-32 w-32 rounded-full bg-[var(--brand-teal)]/10 blur-3xl" />
          <div className="absolute top-10 right-20 h-24 w-24 rounded-full bg-[var(--brand-gold)]/10 blur-2xl" />
          
          <div className="relative z-10 flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight mb-2">Analytics Dashboard</h1>
              <p className="text-white/70 text-lg max-w-xl">
                Comprehensive insights: {summary.total_patients} patients, {summary.total_predictions} predictions, {summary.total_clinical_reports} reports
              </p>
              {lastUpdated && (
                <p className="text-white/50 text-sm mt-2">
                  Last updated: {lastUpdated.toLocaleTimeString()}
                </p>
              )}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={loadStats}
              disabled={loading}
              className="bg-white/10 text-white hover:bg-white/20 border-white/20"
            >
              <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </motion.div>

        {/* Summary Stats Row */}
        <motion.div
          variants={shouldReduceMotion ? {} : {
            hidden: { opacity: 0 },
            visible: { opacity: 1, transition: { staggerChildren: 0.08 } }
          }}
          initial="hidden"
          animate="visible"
          className="grid gap-4 md:grid-cols-2 lg:grid-cols-4"
        >
          <motion.div variants={shouldReduceMotion ? {} : staggerItem}>
            <Card className="hover:shadow-lg transition-shadow border-l-4 border-l-[var(--brand-teal)]">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Patients</CardTitle>
                <Users className="h-4 w-4 text-[var(--brand-teal)]" />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{summary.total_patients}</div>
                <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                  <TrendingUp className="h-3 w-3 text-green-500" />
                  +{recent_activity.patients_7d} this week
                </p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={shouldReduceMotion ? {} : staggerItem}>
            <Card className="hover:shadow-lg transition-shadow border-l-4 border-l-[var(--brand-gold)]">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">DR Predictions</CardTitle>
                <Scan className="h-4 w-4 text-[var(--brand-gold)]" />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{summary.total_predictions}</div>
                <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                  <TrendingUp className="h-3 w-3 text-green-500" />
                  +{recent_activity.predictions_7d} this week
                </p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={shouldReduceMotion ? {} : staggerItem}>
            <Card className="hover:shadow-lg transition-shadow border-l-4 border-l-blue-500">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Clinical Reports</CardTitle>
                <FileText className="h-4 w-4 text-blue-500" />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{summary.total_clinical_reports}</div>
                <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                  <TrendingUp className="h-3 w-3 text-green-500" />
                  +{recent_activity.reports_7d} this week
                </p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={shouldReduceMotion ? {} : staggerItem}>
            <Card className="hover:shadow-lg transition-shadow border-l-4 border-l-purple-500">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">OCT Scans</CardTitle>
                <ActivityIcon className="h-4 w-4 text-purple-500" />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{oct_reports.total}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  {oct_reports.avg_image_quality ? `Avg quality: ${oct_reports.avg_image_quality}%` : 'No scans'}
                </p>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>

        {/* Row 1: Patient Demographics & Predictions Severity */}
        <div className="grid gap-4 md:grid-cols-2">
          {/* Gender Distribution */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5 text-[var(--brand-teal)]" />
                Patient Gender Distribution
              </CardTitle>
              <CardDescription>Demographics of registered patients</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={genderData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    dataKey="value"
                  >
                    {genderData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* DR Severity Distribution */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-[var(--brand-teal)]" />
                DR Severity Distribution
              </CardTitle>
              <CardDescription>Predictions by diabetic retinopathy grade</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={severityData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                    {severityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Row 2: Age Groups & Report Status */}
        <div className="grid gap-4 md:grid-cols-2">
          {/* Age Groups */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5 text-[var(--brand-gold)]" />
                Patient Age Distribution
              </CardTitle>
              <CardDescription>Age groups of registered patients</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={ageData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="var(--brand-gold)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Report Status */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-blue-500" />
                Clinical Reports Status
              </CardTitle>
              <CardDescription>Status breakdown of generated reports</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={reportStatusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    dataKey="value"
                  >
                    {reportStatusData.map((entry, index) => {
                      const colors: Record<string, string> = {
                        completed: '#22c55e',
                        pending: '#eab308',
                        running: '#3b82f6',
                        failed: '#ef4444',
                      };
                      return <Cell key={`cell-${index}`} fill={colors[entry.name.toLowerCase()] || COLORS[index]} />;
                    })}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Row 3: OCT Reports - keep existing charts */}
        <div className="space-y-4">
          <h3 className="text-xl font-semibold flex items-center gap-2">
            <Scan className="h-5 w-5 text-[var(--brand-teal)]" />
            OCT Scan Analytics
          </h3>
          
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {/* OCT Grade Distribution */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>DR Grade Distribution (OCT)</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={octGradeData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                      {octGradeData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Eye Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Eye Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie
                      data={eyeData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      dataKey="value"
                    >
                      {eyeData.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            {/* Edema */}
            <Card>
              <CardHeader>
                <CardTitle>Macular Edema</CardTitle>
                <CardDescription>Presence of macular edema</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={edemaData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={60}
                      dataKey="value"
                    >
                      <Cell fill="#e74c3c" />
                      <Cell fill="#2ecc71" />
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* ERM Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Epiretinal Membrane</CardTitle>
                <CardDescription>ERM status distribution</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={Object.entries(oct_reports.erm_distribution).map(([k, v]) => ({ name: k || 'Unknown', value: v }))}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${(percent * 100).toFixed(0)}%`}
                      outerRadius={60}
                      dataKey="value"
                    >
                      {Object.keys(oct_reports.erm_distribution).map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Thickness Radar */}
            <Card>
              <CardHeader>
                <CardTitle>Retinal Thickness</CardTitle>
                <CardDescription>Average measurements (μm)</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={200}>
                  <RadarChart data={thicknessData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="name" tick={{ fontSize: 10 }} />
                    <PolarRadiusAxis />
                    <Radar
                      name="Thickness"
                      dataKey="value"
                      stroke="var(--brand-teal)"
                      fill="var(--brand-teal)"
                      fillOpacity={0.4}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </div>
      </motion.div>
    </PageContainer>
  );
}