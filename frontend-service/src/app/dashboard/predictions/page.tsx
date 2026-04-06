'use client';

import PageContainer from '@/components/layout/page-container';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Upload } from 'lucide-react';
import Image from 'next/image';

export default function PredictionsPage() {
  return (
    <PageContainer>
      <div className='flex flex-col gap-8'>
      {/* Hero */}
      <div className='relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#0a2e3e] via-[#0d3a4c] to-[#104a5e] p-10 text-white'>
        <div className='absolute right-0 top-0 h-full w-1/3 opacity-10'>
          <Image
            src='https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&q=80'
            alt='AI Predictions'
            fill
            className='object-cover'
            unoptimized
          />
        </div>
        <div className='relative z-10'>
          <h1 className='text-3xl font-bold tracking-tight mb-2'>Predictions</h1>
          <p className='text-white/70 text-lg max-w-xl'>
            Upload scans and run DR grading predictions — AI-assisted retinal analysis
          </p>
        </div>
      </div>

      <Card className='border-dashed'>
        <CardHeader>
          <CardTitle>Upload Scans</CardTitle>
        </CardHeader>
        <CardContent className='flex flex-col items-center justify-center py-12'>
          <Upload className='h-16 w-16 text-muted-foreground mb-4' />
          <p className='text-muted-foreground mb-4'>
            Drag and drop fundus or OCT images here
          </p>
          <Button>Choose Files</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recent Predictions</CardTitle>
        </CardHeader>
        <CardContent>
          <p className='text-muted-foreground text-center py-8'>
            No predictions yet. Upload scans to get started.
          </p>
        </CardContent>
      </Card>
    </div>
    </PageContainer>
  );
}
