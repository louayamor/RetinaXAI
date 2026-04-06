'use client';

import { useEffect, useState } from 'react';
import { apiFetch } from '@/lib/auth';
import PageContainer from '@/components/layout/page-container';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import Image from 'next/image';

interface Patient {
  id: string;
  first_name: string;
  last_name: string;
  age: number;
  gender: string;
  medical_record_number: string;
  ocr_patient_id: string | null;
  created_at: string;
}

export default function PatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    apiFetch<Patient[]>('/api/v1/patients/')
      .then((data) => {
        if (Array.isArray(data)) {
          setPatients(data);
        } else {
          setPatients([]);
        }
      })
      .catch((err) => {
        if (err?.status === 401) {
          window.location.href = '/auth/login';
        } else {
          console.error('Failed to fetch patients:', err);
        }
        setPatients([]);
      })
      .finally(() => setLoading(false));
  }, []);

  const filtered = patients.filter(
    (p) =>
      p.first_name.toLowerCase().includes(search.toLowerCase()) ||
      p.last_name.toLowerCase().includes(search.toLowerCase()) ||
      p.medical_record_number.toLowerCase().includes(search.toLowerCase()) ||
      (p.ocr_patient_id || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <PageContainer>
      <div className='flex flex-col gap-8'>
      {/* Hero */}
      <div className='relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#0a2e3e] via-[#0d3a4c] to-[#104a5e] p-10 text-white'>
        <div className='absolute right-0 top-0 h-full w-1/3 opacity-10'>
          <Image
            src='https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=800&q=80'
            alt='Patient Care'
            fill
            className='object-cover'
            unoptimized
          />
        </div>
        <div className='relative z-10'>
          <h1 className='text-3xl font-bold tracking-tight mb-2'>Patients</h1>
          <p className='text-white/70 text-lg max-w-xl'>
            Manage patients and their OCT reports.
          </p>
        </div>
      </div>

      <div className='flex items-center justify-between'>
        <div>
          <h1 className='text-3xl font-bold tracking-tight'>Patients</h1>
          <p className='text-muted-foreground'>
            Manage patients and their OCT reports
          </p>
        </div>
        <Button>Add Patient</Button>
      </div>

      <div className='flex items-center gap-4'>
        <Input
          placeholder='Search patients...'
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className='max-w-sm'
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{filtered.length} Patients</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className='text-muted-foreground text-center py-8'>Loading...</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Age</TableHead>
                  <TableHead>Gender</TableHead>
                  <TableHead>MRN</TableHead>
                  <TableHead>OCR ID</TableHead>
                  <TableHead>Added</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtered.map((p) => (
                  <TableRow key={p.id}>
                    <TableCell className='font-medium'>
                      {p.first_name} {p.last_name}
                    </TableCell>
                    <TableCell>{p.age}</TableCell>
                    <TableCell>
                      <Badge variant='outline'>{p.gender}</Badge>
                    </TableCell>
                    <TableCell className='font-mono text-sm'>
                      {p.medical_record_number}
                    </TableCell>
                    <TableCell className='font-mono text-sm text-muted-foreground'>
                      {p.ocr_patient_id || '—'}
                    </TableCell>
                    <TableCell className='text-sm text-muted-foreground'>
                      {new Date(p.created_at).toLocaleDateString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
    </PageContainer>
  );
}
