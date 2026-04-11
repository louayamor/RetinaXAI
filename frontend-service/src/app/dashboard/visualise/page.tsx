'use client';

import { useEffect, useState } from 'react';
import { motion, useReducedMotion } from 'motion/react';
import { apiFetch } from '@/lib/auth';
import PageContainer from '@/components/layout/page-container';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
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
} from 'recharts';
import { fadeInUp, slideInUp, staggerItem } from '@/lib/animations';

const COLORS = ['#20bdbe', '#c8a951', '#e74c3c', '#3498db', '#9b59b6', '#2ecc71'];
const GRADE_COLORS: Record<string, string> = {
  no_dr: '#2ecc71',
  mild: '#20bdbe',
  moderate: '#c8a951',
  severe: '#e67e22',
  proliferative: '#e74c3c',
};

interface OCTStats {
  total_reports: number;
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
  avg_reports_per_patient: number;
}

export default function VisualisePage() {
  const [stats, setStats] = useState<OCTStats | null>(null);
  const [loading, setLoading] = useState(true);
  const shouldReduceMotion = useReducedMotion();

  useEffect(() => {
    apiFetch<OCTStats>('/api/v1/oct-stats/stats')
      .then(setStats)
      .catch((err) => {
        if (err?.status === 401) {
          window.location.href = '/auth/login';
        } else {
          console.error('Failed to fetch OCT stats:', err);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className='flex h-full items-center justify-center'>
        <p className='text-muted-foreground'>Loading visualisations...</p>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className='flex h-full items-center justify-center'>
        <p className='text-muted-foreground'>No data available</p>
      </div>
    );
  }

  const gradeData = Object.entries(stats.grade_distribution).map(([grade, count]) => ({
    name: grade.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
    value: count,
    fill: GRADE_COLORS[grade] || '#20bdbe',
  }));

  const eyeData = Object.entries(stats.eye_distribution).map(([eye, count]) => ({
    name: eye === 'OD' ? 'Right Eye (OD)' : 'Left Eye (OS)',
    value: count,
  }));

  const edemaData = [
    { name: 'Present', value: stats.edema.present },
    { name: 'Absent', value: stats.edema.absent },
  ];

  const thicknessData = [
    { name: 'Center Fovea', value: stats.thickness_averages.center_fovea || 0 },
    { name: 'Average', value: stats.thickness_averages.average_thickness || 0 },
    { name: 'Total Volume', value: stats.thickness_averages.total_volume_mm3 || 0 },
  ];

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
        <div className="absolute right-0 top-0 h-full w-1/3 opacity-10">
          <Image
            src="https://images.unsplash.com/photo-1551076805-e1869033e561?w=800&q=80"
            alt="Data Visualization"
            fill
            className="object-cover"
            unoptimized
          />
        </div>
        <div className="relative z-10">
          <h1 className="text-3xl font-bold tracking-tight mb-2">Visualise</h1>
          <p className="text-white/70 text-lg max-w-xl">
            Clinical insights from {stats.total_reports} OCT reports — powered by AI
          </p>
        </div>
      </motion.div>

      {/* Summary Cards */}
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
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Reports</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stats.total_reports}</div>
            </CardContent>
          </Card>
        </motion.div>
        <motion.div variants={shouldReduceMotion ? {} : staggerItem}>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Reports / Patient</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stats.avg_reports_per_patient}</div>
            </CardContent>
          </Card>
        </motion.div>
        <motion.div variants={shouldReduceMotion ? {} : staggerItem}>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Edema Rate</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {stats.edema.present + stats.edema.absent > 0
                  ? `${((stats.edema.present / (stats.edema.present + stats.edema.absent)) * 100).toFixed(1)}%`
                  : 'N/A'}
              </div>
            </CardContent>
          </Card>
        </motion.div>
        <motion.div variants={shouldReduceMotion ? {} : staggerItem}>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Image Quality</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {stats.avg_image_quality ?? 'N/A'}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>

      {/* Charts Row 1 */}
      <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
        {/* DR Grade Distribution */}
        <Card className='col-span-2'>
          <CardHeader>
            <CardTitle>DR Grade Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width='100%' height={300}>
              <BarChart data={gradeData}>
                <CartesianGrid strokeDasharray='3 3' />
                <XAxis dataKey='name' />
                <YAxis />
                <Tooltip />
                <Bar dataKey='value' radius={[4, 4, 0, 0]}>
                  {gradeData.map((entry, index) => (
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
            <ResponsiveContainer width='100%' height={300}>
              <PieChart>
                <Pie
                  data={eyeData}
                  cx='50%'
                  cy='50%'
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill='#8884d8'
                  dataKey='value'
                >
                  {eyeData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 2 */}
      <div className='grid gap-4 md:grid-cols-2'>
        {/* Edema */}
        <Card>
          <CardHeader>
            <CardTitle>Macular Edema</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width='100%' height={300}>
              <PieChart>
                <Pie
                  data={edemaData}
                  cx='50%'
                  cy='50%'
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill='#8884d8'
                  dataKey='value'
                >
                  <Cell fill='#e74c3c' />
                  <Cell fill='#2ecc71' />
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Thickness Radar */}
        <Card>
          <CardHeader>
            <CardTitle>Retinal Thickness Averages</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width='100%' height={300}>
              <RadarChart data={thicknessData}>
                <PolarGrid />
                <PolarAngleAxis dataKey='name' />
                <PolarRadiusAxis />
                <Radar
                  name='Thickness'
                  dataKey='value'
                  stroke='#20bdbe'
                  fill='#20bdbe'
                  fillOpacity={0.4}
                />
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
      </motion.div>
    </PageContainer>
  );
}
