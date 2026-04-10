'use client';

import * as React from 'react';
import { IconTrendingUp, IconUsers } from '@tabler/icons-react';
import { Label, Pie, PieChart } from 'recharts';

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

interface PieGraphProps {
  data?: Record<string, number>;
  loading?: boolean;
}

const genderLabels: Record<string, string> = {
  M: 'Male',
  F: 'Female',
  O: 'Other'
};

const chartConfig = {
  count: {
    label: 'Patients'
  },
  M: {
    label: 'Male',
    color: 'var(--primary)'
  },
  F: {
    label: 'Female',
    color: 'var(--primary-light)'
  },
  O: {
    label: 'Other',
    color: 'var(--primary-lighter)'
  }
} satisfies ChartConfig;

export function PieGraph({ data, loading = false }: PieGraphProps) {
  const chartData = React.useMemo(() => {
    if (!data || Object.keys(data).length === 0) {
      return [
        { gender: 'Male', count: 0, key: 'M', fill: 'var(--primary)' },
        { gender: 'Female', count: 0, key: 'F', fill: 'var(--primary-light)' }
      ];
    }

    const colors = ['var(--primary)', 'var(--primary-light)', 'var(--primary-lighter)'];
    return Object.entries(data)
      .map(([key, count], index) => ({
        gender: genderLabels[key] || key,
        count: count || 0,
        key,
        fill: colors[index % colors.length]
      }))
      .filter(item => item.count > 0);
  }, [data]);

  const totalPatients = React.useMemo(
    () => chartData.reduce((acc, curr) => acc + curr.count, 0),
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
          <Skeleton className="mx-auto aspect-square h-[250px]" />
        </CardContent>
        <CardFooter className="flex-col gap-2">
          <Skeleton className="h-4 w-48" />
          <Skeleton className="h-4 w-32" />
        </CardFooter>
      </Card>
    );
  }

  // If no data, show empty state
  if (totalPatients === 0) {
    return (
      <Card className="@container/card">
        <CardHeader>
          <CardTitle>Patient Demographics</CardTitle>
          <CardDescription>
            Gender distribution of registered patients
          </CardDescription>
        </CardHeader>
        <CardContent className="px-2 pt-4 sm:px-6 sm:pt-6">
          <div className="mx-auto flex aspect-square h-[250px] flex-col items-center justify-center text-center">
            <IconUsers className="mb-4 h-12 w-12 text-muted-foreground/50" />
            <p className="text-muted-foreground">No patients registered yet</p>
            <p className="text-muted-foreground text-sm">
              Add patients to see demographics
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const largestSegment = chartData.reduce((max, item) =>
    item.count > max.count ? item : max, chartData[0]);

  return (
    <Card className="@container/card">
      <CardHeader>
        <CardTitle>Patient Demographics</CardTitle>
        <CardDescription>
          <span className="hidden @[540px]/card:block">
            Gender distribution of registered patients
          </span>
          <span className="@[540px]/card:hidden">Gender distribution</span>
        </CardDescription>
      </CardHeader>
      <CardContent className="px-2 pt-4 sm:px-6 sm:pt-6">
        <ChartContainer
          config={chartConfig}
          className="mx-auto aspect-square h-[250px]"
        >
          <PieChart>
            <defs>
              {chartData.map((item, index) => (
                <linearGradient
                  key={item.key}
                  id={`fill${item.key}`}
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop
                    offset="0%"
                    stopColor={item.fill}
                    stopOpacity={1 - index * 0.2}
                  />
                  <stop
                    offset="100%"
                    stopColor={item.fill}
                    stopOpacity={0.8 - index * 0.2}
                  />
                </linearGradient>
              ))}
            </defs>
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent hideLabel />}
            />
            <Pie
              data={chartData.map((item) => ({
                ...item,
                fill: `url(#fill${item.key})`
              }))}
              dataKey="count"
              nameKey="gender"
              innerRadius={60}
              strokeWidth={2}
              stroke="var(--background)"
            >
              <Label
                content={({ viewBox }) => {
                  if (viewBox && 'cx' in viewBox && 'cy' in viewBox) {
                    return (
                      <text
                        x={viewBox.cx}
                        y={viewBox.cy}
                        textAnchor="middle"
                        dominantBaseline="middle"
                      >
                        <tspan
                          x={viewBox.cx}
                          y={viewBox.cy}
                          className="fill-foreground text-3xl font-bold"
                        >
                          {totalPatients.toLocaleString()}
                        </tspan>
                        <tspan
                          x={viewBox.cx}
                          y={(viewBox.cy || 0) + 24}
                          className="fill-muted-foreground text-sm"
                        >
                          Total Patients
                        </tspan>
                      </text>
                    );
                  }
                }}
              />
            </Pie>
          </PieChart>
        </ChartContainer>
      </CardContent>
      <CardFooter className="flex-col gap-2 text-sm">
        <div className="flex items-center gap-2 leading-none font-medium">
          {largestSegment.gender} leads with{' '}
          {((largestSegment.count / totalPatients) * 100).toFixed(1)}%
          <IconTrendingUp className="h-4 w-4" />
        </div>
        <div className="text-muted-foreground leading-none">
          Based on {totalPatients} registered patients
        </div>
      </CardFooter>
    </Card>
  );
}
