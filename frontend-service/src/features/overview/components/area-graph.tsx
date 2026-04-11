'use client';

import * as React from 'react';
import { IconTrendingUp } from '@tabler/icons-react';
import { Area, AreaChart, CartesianGrid, XAxis } from 'recharts';

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle
} from '@/components/ui/card';
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent
} from '@/components/ui/chart';
import { Skeleton } from '@/components/ui/skeleton';

interface AreaGraphProps {
  data?: Record<number, number>;
  loading?: boolean;
}

const severityLabels: Record<number, string> = {
  0: 'No DR',
  1: 'Mild',
  2: 'Moderate',
  3: 'Severe',
  4: 'Proliferative'
};

const chartConfig = {
  count: {
    label: 'Predictions',
    color: 'var(--primary)'
  }
} satisfies ChartConfig;

export function AreaGraph({ data, loading = false }: AreaGraphProps) {
  // Transform severity data for the chart
  const chartData = React.useMemo(() => {
    if (!data || Object.keys(data).length === 0) {
      return null;
    }

    return Object.entries(data)
      .map(([level, count]) => ({
        severity: severityLabels[parseInt(level)] || `Level ${level}`,
        count: count || 0,
        level: parseInt(level)
      }))
      .sort((a, b) => a.level - b.level);
  }, [data]);

  const total = React.useMemo(
    () => chartData ? chartData.reduce((acc, curr) => acc + curr.count, 0) : 0,
    [chartData]
  );

  const [isClient, setIsClient] = React.useState(false);

  React.useEffect(() => {
    setIsClient(true);
  }, []);

  if (!isClient) {
    return null;
  }

  if (loading) {
    return (
      <Card className="@container/card">
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-32" />
        </CardHeader>
        <CardContent className="px-2 pt-4 sm:px-6 sm:pt-6">
          <Skeleton className="h-[250px] w-full" />
        </CardContent>
        <CardFooter>
          <Skeleton className="h-4 w-full" />
        </CardFooter>
      </Card>
    );
  }

  // Empty state
  if (!chartData || total === 0) {
    return (
      <Card className="@container/card">
        <CardHeader>
          <CardTitle>DR Severity Distribution</CardTitle>
          <CardDescription>Predictions by diabetic retinopathy severity level</CardDescription>
        </CardHeader>
        <CardContent className="flex h-[250px] items-center justify-center">
          <div className="text-center">
            <IconTrendingUp className="mx-auto h-12 w-12 text-muted-foreground/30" />
            <p className="mt-2 text-sm text-muted-foreground">No severity data</p>
            <p className="text-xs text-muted-foreground/70">Run predictions to see severity distribution</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="@container/card">
      <CardHeader>
        <CardTitle>DR Severity Distribution</CardTitle>
        <CardDescription>
          Predictions by diabetic retinopathy severity level
        </CardDescription>
      </CardHeader>
      <CardContent className="px-2 pt-4 sm:px-6 sm:pt-6">
        <ChartContainer
          config={chartConfig}
          className="aspect-auto h-[250px] w-full"
        >
          <AreaChart
            data={chartData}
            margin={{
              left: 12,
              right: 12
            }}
          >
            <defs>
              <linearGradient id="fillSeverity" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--primary)"
                  stopOpacity={1.0}
                />
                <stop
                  offset="95%"
                  stopColor="var(--primary)"
                  stopOpacity={0.1}
                />
              </linearGradient>
            </defs>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="severity"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              minTickGap={32}
            />
            <ChartTooltip
              cursor={false}
              content={
                <ChartTooltipContent
                  indicator="dot"
                  labelKey="severity"
                />
              }
            />
            <Area
              dataKey="count"
              type="natural"
              fill="url(#fillSeverity)"
              stroke="var(--primary)"
            />
          </AreaChart>
        </ChartContainer>
      </CardContent>
      <CardFooter>
        <div className="flex w-full items-start gap-2 text-sm">
          <div className="grid gap-2">
            <div className="flex items-center gap-2 leading-none font-medium">
              {total > 0 ? (
                <>
                  {chartData[0]?.count || 0} No DR cases{' '}
                  <IconTrendingUp className="h-4 w-4" />
                </>
              ) : (
                'No predictions yet'
              )}
            </div>
            <div className="text-muted-foreground flex items-center gap-2 leading-none">
              {total > 0 ? `${total} total predictions` : 'Start by creating predictions'}
            </div>
          </div>
        </div>
      </CardFooter>
    </Card>
  );
}
