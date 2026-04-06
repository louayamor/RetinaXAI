'use client';

import PageContainer from '@/components/layout/page-container';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FileText } from 'lucide-react';
import Image from 'next/image';

export default function ReportsPage() {
  return (
    <PageContainer>
      <div className='flex flex-col gap-8'>
      {/* Hero */}
      <div className='relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#0a2e3e] via-[#0d3a4c] to-[#104a5e] p-10 text-white'>
        <div className='absolute right-0 top-0 h-full w-1/3 opacity-10'>
          <Image
            src='https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&q=80'
            alt='Clinical Reports'
            fill
            className='object-cover'
            unoptimized
          />
        </div>
        <div className='relative z-10'>
          <h1 className='text-3xl font-bold tracking-tight mb-2'>Reports</h1>
          <p className='text-white/70 text-lg max-w-xl'>
            LLM-generated clinical reports and summaries — powered by Samaya expertise
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Reports</CardTitle>
        </CardHeader>
        <CardContent className='flex flex-col items-center justify-center py-12'>
          <FileText className='h-16 w-16 text-muted-foreground mb-4' />
          <p className='text-muted-foreground'>
            No reports generated yet. Run a prediction first.
          </p>
        </CardContent>
      </Card>
    </div>
    </PageContainer>
  );
}
