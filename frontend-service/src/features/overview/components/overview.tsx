'use client';

import { useEffect, useState } from 'react';
import { motion, useReducedMotion } from 'motion/react';
import PageContainer from '@/components/layout/page-container';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
  CardAction
} from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AreaGraph } from './area-graph';
import { BarGraph } from './bar-graph';
import { PieGraph } from './pie-graph';
import { IconTrendingUp, IconTrendingDown, IconUsers, IconScan, IconChartBar, IconFileText, IconActivity } from '@tabler/icons-react';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { getDashboardStats, DashboardStats } from '@/lib/api';
import { toast } from 'sonner';
import { fadeInUp, staggerContainer, staggerItem, buttonTap, slideInUp } from '@/lib/animations';
import Image from 'next/image';

const severityLabels: Record<number, string> = {
  0: 'No DR',
  1: 'Mild',
  2: 'Moderate',
  3: 'Severe',
  4: 'Proliferative'
};

export default function OverViewPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const shouldReduceMotion = useReducedMotion();

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await getDashboardStats();
      setStats(data);
    } catch (error) {
      toast.error('Failed to load dashboard stats');
      console.error('Dashboard stats error:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateTrend = (recent: number, total: number) => {
    if (total === 0) return 0;
    return Math.round((recent / total) * 100);
  };

  const StatCard = ({
    title,
    value,
    icon: Icon,
    trend,
    trendLabel,
    footer
  }: {
    title: string;
    value: number;
    icon: React.ElementType;
    trend: number;
    trendLabel: string;
    footer: string;
  }) => (
    <Card className="@container/card">
      <CardHeader>
        <CardDescription>{title}</CardDescription>
        <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
          {loading ? <Skeleton className="h-8 w-20" /> : value.toLocaleString()}
        </CardTitle>
        <CardAction>
          {loading ? (
            <Skeleton className="h-6 w-16" />
          ) : (
            <Badge variant={trend > 0 ? 'outline' : 'secondary'}>
              {trend > 0 ? <IconTrendingUp className="size-4" /> : <IconTrendingDown className="size-4" />}
              {trend > 0 ? '+' : ''}{trend}%
            </Badge>
          )}
        </CardAction>
      </CardHeader>
      <CardFooter className="flex-col items-start gap-1.5 text-sm">
        <div className="line-clamp-1 flex gap-2 font-medium">
          {trendLabel}
          {trend > 0 ? <IconTrendingUp className="size-4" /> : <IconTrendingDown className="size-4" />}
        </div>
        <div className="text-muted-foreground">{footer}</div>
      </CardFooter>
    </Card>
  );

  const predictionsTrend = stats ? calculateTrend(stats.recent_activity.new_predictions, stats.totals.predictions) : 0;
  const reportsTrend = stats ? calculateTrend(stats.recent_activity.new_reports, stats.totals.reports) : 0;
  const patientsTrend = stats ? calculateTrend(stats.recent_activity.new_patients, stats.totals.patients) : 0;
  const confidenceTrend = stats?.avg_confidence ? Math.round(stats.avg_confidence * 100) : 0;

  return (
    <PageContainer>
      <motion.div
        variants={shouldReduceMotion ? {} : fadeInUp}
        initial="hidden"
        animate="visible"
        className="flex flex-1 flex-col space-y-2"
      >
        <div className="flex items-center justify-between space-y-2">
          <h2 className="text-2xl font-bold tracking-tight">
            Clinical Dashboard
          </h2>
          <div className="hidden items-center space-x-2 md:flex">
            <motion.div variants={shouldReduceMotion ? {} : buttonTap}>
              <Button onClick={loadStats} disabled={loading}>
                {loading ? 'Loading...' : 'Refresh'}
              </Button>
            </motion.div>
          </div>
        </div>
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsContent value="overview" className="space-y-4">
            <motion.div
              variants={shouldReduceMotion ? {} : staggerContainer}
              initial="hidden"
              animate="visible"
              className="*:data-[slot=card]:from-primary/5 *:data-[slot=card]:to-card dark:*:data-[slot=card]:bg-card grid grid-cols-1 gap-4 px-4 *:data-[slot=card]:bg-gradient-to-t *:data-[slot=card]:shadow-xs lg:px-6 @xl/main:grid-cols-2 @5xl/main:grid-cols-4"
            >
              <motion.div variants={shouldReduceMotion ? {} : staggerItem}>
                <StatCard
                  title="Total Patients"
                  value={stats?.totals.patients ?? 0}
                  icon={IconUsers}
                  trend={patientsTrend}
                  trendLabel={`${stats?.recent_activity.new_patients ?? 0} new this week`}
                  footer="Active patients in system"
                />
              </motion.div>
              <motion.div variants={shouldReduceMotion ? {} : staggerItem}>
                <StatCard
                  title="Total Predictions"
                  value={stats?.totals.predictions ?? 0}
                  icon={IconScan}
                  trend={predictionsTrend}
                  trendLabel={`${stats?.recent_activity.new_predictions ?? 0} this week`}
                  footer="AI predictions processed"
                />
              </motion.div>
              <motion.div variants={shouldReduceMotion ? {} : staggerItem}>
                <StatCard
                  title="Reports Generated"
                  value={stats?.totals.reports ?? 0}
                  icon={IconFileText}
                  trend={reportsTrend}
                  trendLabel={`${stats?.recent_activity.new_reports ?? 0} this week`}
                  footer="Clinical reports created"
                />
              </motion.div>
              <motion.div variants={shouldReduceMotion ? {} : staggerItem}>
                <StatCard
                  title="Avg Confidence"
                  value={confidenceTrend}
                  icon={IconChartBar}
                  trend={confidenceTrend > 80 ? 5 : confidenceTrend > 60 ? 0 : -5}
                  trendLabel={confidenceTrend > 80 ? 'High accuracy' : confidenceTrend > 60 ? 'Moderate accuracy' : 'Review needed'}
                  footer="Model prediction confidence"
                />
              </motion.div>
            </motion.div>
            
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <IconActivity className="h-5 w-5 text-[#20bdbe]" />
                <h3 className="text-lg font-semibold">Analytics</h3>
              </div>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <motion.div variants={shouldReduceMotion ? {} : slideInUp}>
                  <BarGraph data={stats?.predictions_timeline} loading={loading} />
                </motion.div>
                <motion.div variants={shouldReduceMotion ? {} : slideInUp}>
                  <AreaGraph data={stats?.severity_distribution} loading={loading} />
                </motion.div>
                <motion.div variants={shouldReduceMotion ? {} : slideInUp} className="md:col-span-2 lg:col-span-1">
                  <PieGraph data={stats?.gender_distribution} loading={loading} />
                </motion.div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </motion.div>
    </PageContainer>
  );
}
