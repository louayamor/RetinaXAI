import PageContainer from '@/components/layout/page-container';
import { Badge } from '@/components/ui/badge';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { IconTrendingDown, IconTrendingUp, IconEye, IconUsers, IconActivity, IconBrain } from '@tabler/icons-react';
import React from 'react';

export default function OverViewLayout({
  pie_stats,
  bar_stats,
  area_stats
}: {
  pie_stats: React.ReactNode;
  bar_stats: React.ReactNode;
  area_stats: React.ReactNode;
}) {
  return (
    <PageContainer>
      <div className='flex flex-1 flex-col gap-8'>
        {/* Hero Section */}
        <div className='relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#0a2e3e] via-[#0d3a4c] to-[#104a5e] p-10 text-white'>
          <div className='absolute right-0 top-0 h-full w-1/3 opacity-10'>
            <img
              src='https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=800&q=80'
              alt='Medical Technology'
              className='h-full w-full object-cover'
            />
          </div>
          <div className='relative z-10'>
            <div className='flex items-center gap-3 mb-4'>
              <img
                src='https://www.samayahospital.ae/home/images/logo.png'
                alt='Samaya Logo'
                className='h-8 w-auto brightness-0 invert'
              />
              <span className='text-lg font-medium text-[#20bdbe]'>|</span>
              <span className='text-lg font-medium'>RetinaXAI</span>
            </div>
            <h1 className='text-3xl font-bold mb-2'>
              Welcome to RetinaXAI
            </h1>
            <p className='text-white/70 max-w-xl text-lg'>
              AI-assisted diabetic retinopathy detection powered by Samaya Specialized Center.
              Love your Eyes. Love your Future.
            </p>
          </div>
        </div>

        {/* Stats Cards */}
        <div className='grid gap-6 md:grid-cols-2 lg:grid-cols-4'>
          <Card className='shadow-md'>
            <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-4'>
              <CardTitle className='text-base font-medium'>Total OCT Reports</CardTitle>
              <IconEye className='h-5 w-5 text-[#20bdbe]' />
            </CardHeader>
            <CardContent>
              <div className='text-3xl font-bold'>119</div>
              <p className='text-muted-foreground text-sm mt-1'>
                From 104 unique patients
              </p>
            </CardContent>
          </Card>
          <Card className='shadow-md'>
            <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-4'>
              <CardTitle className='text-base font-medium'>DR Detected</CardTitle>
              <IconActivity className='h-5 w-5 text-[#c8a951]' />
            </CardHeader>
            <CardContent>
              <div className='text-3xl font-bold'>82</div>
              <p className='text-muted-foreground text-sm mt-1'>
                68.9% of reports have a grade
              </p>
            </CardContent>
          </Card>
          <Card className='shadow-md'>
            <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-4'>
              <CardTitle className='text-base font-medium'>Active Patients</CardTitle>
              <IconUsers className='h-5 w-5 text-[#20bdbe]' />
            </CardHeader>
            <CardContent>
              <div className='text-3xl font-bold'>104</div>
              <p className='text-muted-foreground text-sm mt-1'>
                Registered in the system
              </p>
            </CardContent>
          </Card>
          <Card className='shadow-md'>
            <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-4'>
              <CardTitle className='text-base font-medium'>Model Accuracy</CardTitle>
              <IconBrain className='h-5 w-5 text-[#20bdbe]' />
            </CardHeader>
            <CardContent>
              <div className='text-3xl font-bold'>94.7%</div>
              <p className='text-muted-foreground text-sm mt-1'>
                EfficientNet-B3 on EyePACS
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Grade Distribution */}
        <Card className='shadow-md'>
          <CardHeader>
            <CardTitle>DR Grade Distribution</CardTitle>
            <CardDescription>
              Breakdown of detected diabetic retinopathy severity levels
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-5'>
              {[
                { grade: 'No DR', count: 0, color: 'bg-green-500', pct: '0%' },
                { grade: 'Mild', count: 8, color: 'bg-[#20bdbe]', pct: '9.8%' },
                { grade: 'Moderate', count: 29, color: 'bg-[#c8a951]', pct: '35.4%' },
                { grade: 'Severe', count: 9, color: 'bg-orange-500', pct: '11.0%' },
                { grade: 'Proliferative', count: 36, color: 'bg-red-500', pct: '43.9%' },
              ].map((item) => (
                <div key={item.grade} className='flex flex-col items-center gap-2 rounded-xl border p-4'>
                  <div className={`h-3 w-full rounded-full ${item.color}`} style={{ opacity: 0.8 }} />
                  <div className='text-center'>
                    <p className='text-2xl font-bold'>{item.count}</p>
                    <p className='text-sm text-muted-foreground'>{item.grade}</p>
                    <Badge variant='secondary' className='mt-1'>{item.pct}</Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Charts */}
        <div className='grid gap-6 md:grid-cols-2 lg:grid-cols-7'>
          <div className='col-span-4'>{bar_stats}</div>
          <div className='col-span-4 md:col-span-3'>{pie_stats}</div>
          <div className='col-span-4 lg:col-span-7'>{area_stats}</div>
        </div>

        {/* Samaya Info */}
        <div className='grid gap-6 md:grid-cols-2'>
          <Card className='shadow-md'>
            <CardHeader>
              <CardTitle>About Samaya Specialized Center</CardTitle>
            </CardHeader>
            <CardContent className='space-y-4'>
              <p className='text-muted-foreground'>
                Samaya Specialized Center is a leading ophthalmology hospital in Abu Dhabi,
                providing expert eye care with advanced technology and compassionate treatment.
              </p>
              <div className='grid gap-3 sm:grid-cols-2'>
                <div className='rounded-lg bg-secondary p-4'>
                  <p className='text-sm font-medium'>Al Bateen Branch</p>
                  <p className='text-xs text-muted-foreground'>St. No. 6, Opp. Indonesian Embassy</p>
                  <p className='text-xs text-muted-foreground'>+971 2 885 3888</p>
                </div>
                <div className='rounded-lg bg-secondary p-4'>
                  <p className='text-sm font-medium'>Khalifa City Branch</p>
                  <p className='text-xs text-muted-foreground'>Al Asayil Street, Khalifa City A</p>
                  <p className='text-xs text-muted-foreground'>+971 2 885 3888</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className='shadow-md'>
            <CardHeader>
              <CardTitle>Services</CardTitle>
            </CardHeader>
            <CardContent>
              <div className='grid gap-3 sm:grid-cols-2'>
                {['Contoura LASIK', 'Cataract', 'Keratoconus', 'Glaucoma', 'Diabetic Retinopathy', 'Dry Eyes'].map((s) => (
                  <div key={s} className='flex items-center gap-2 rounded-lg border p-3'>
                    <div className='h-2 w-2 rounded-full bg-[#20bdbe]' />
                    <span className='text-sm'>{s}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageContainer>
  );
}
