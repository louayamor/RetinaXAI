'use client';

import { useEffect, useState, type ChangeEvent } from 'react';
import { createPatient, deletePatient, getPatients, searchPatients, updatePatient } from '@/lib/api';
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
import type { Patient } from '@/types';

type PatientFormState = {
  first_name: string;
  last_name: string;
  age: string;
  gender: 'M' | 'F';
  medical_record_number: string;
  phone: string;
  address: string;
  ocr_patient_id: string;
};

const emptyForm: PatientFormState = {
  first_name: '',
  last_name: '',
  age: '',
  gender: 'M',
  medical_record_number: '',
  phone: '',
  address: '',
  ocr_patient_id: ''
};

export default function PatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [search, setSearch] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<PatientFormState>(emptyForm);

  const loadPatients = async (query = '') => {
    setLoading(true);
    try {
      const data = query.trim() ? await searchPatients(query.trim()) : await getPatients();
      setPatients(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to fetch patients:', err);
      setPatients([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadPatients();
  }, []);

  useEffect(() => {
    const t = setTimeout(() => {
      void loadPatients(search);
    }, 300);
    return () => clearTimeout(t);
  }, [search]);

  const onChange =
    (key: keyof PatientFormState) =>
    (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      setForm((prev) => ({ ...prev, [key]: e.target.value }));
    };

  const resetForm = () => {
    setForm(emptyForm);
    setEditingId(null);
  };

  const onSubmit = async () => {
    if (!form.first_name || !form.last_name || !form.medical_record_number || !form.age) return;
    setSaving(true);
    try {
      if (editingId) {
        await updatePatient(editingId, {
          first_name: form.first_name,
          last_name: form.last_name,
          age: Number(form.age),
          gender: form.gender,
          medical_record_number: form.medical_record_number,
          phone: form.phone || null,
          address: form.address || null,
          ocr_patient_id: form.ocr_patient_id || null
        });
      } else {
        await createPatient({
          first_name: form.first_name,
          last_name: form.last_name,
          age: Number(form.age),
          gender: form.gender,
          medical_record_number: form.medical_record_number,
          phone: form.phone || null,
          address: form.address || null,
          ocr_patient_id: form.ocr_patient_id || null
        });
      }
      resetForm();
      await loadPatients(search);
    } catch (err) {
      console.error('Failed to save patient:', err);
    } finally {
      setSaving(false);
    }
  };

  const onEdit = (p: Patient) => {
    setEditingId(p.id);
    setForm({
      first_name: p.first_name,
      last_name: p.last_name,
      age: String(p.age),
      gender: p.gender,
      medical_record_number: p.medical_record_number,
      phone: p.phone ?? '',
      address: p.address ?? '',
      ocr_patient_id: p.ocr_patient_id ?? ''
    });
  };

  const onDelete = async (id: string) => {
    if (!window.confirm('Delete this patient? This cannot be undone.')) return;
    try {
      await deletePatient(id);
      await loadPatients(search);
    } catch (err) {
      console.error('Failed to delete patient:', err);
    }
  };

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
            <h1 className='mb-2 text-3xl font-bold tracking-tight'>Patients</h1>
            <p className='max-w-xl text-lg text-white/70'>
              Manage patients and their OCT reports.
            </p>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>{editingId ? 'Update Patient' : 'Add Patient'}</CardTitle>
          </CardHeader>
          <CardContent className='grid gap-3 md:grid-cols-4'>
            <Input placeholder='First name' value={form.first_name} onChange={onChange('first_name')} />
            <Input placeholder='Last name' value={form.last_name} onChange={onChange('last_name')} />
            <Input placeholder='Age' type='number' min={0} value={form.age} onChange={onChange('age')} />
            <select
              className='border-input bg-background h-9 rounded-md border px-3 text-sm'
              value={form.gender}
              onChange={onChange('gender')}
            >
              <option value='M'>Male</option>
              <option value='F'>Female</option>
            </select>
            <Input
              placeholder='Medical record number'
              value={form.medical_record_number}
              onChange={onChange('medical_record_number')}
            />
            <Input placeholder='Phone' value={form.phone} onChange={onChange('phone')} />
            <Input placeholder='Address' value={form.address} onChange={onChange('address')} />
            <Input placeholder='OCR patient id' value={form.ocr_patient_id} onChange={onChange('ocr_patient_id')} />
            <div className='md:col-span-4 flex gap-2'>
              <Button onClick={onSubmit} disabled={saving}>
                {editingId ? 'Update Patient' : 'Add Patient'}
              </Button>
              {editingId ? (
                <Button variant='outline' onClick={resetForm}>
                  Cancel
                </Button>
              ) : null}
            </div>
          </CardContent>
        </Card>

        <div className='flex items-center gap-4'>
          <Input
            placeholder='Search by name, MRN, OCR ID...'
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className='max-w-sm'
          />
        </div>

        <Card>
          <CardHeader>
            <CardTitle>{patients.length} Patients</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p className='text-muted-foreground py-8 text-center'>Loading...</p>
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
                    <TableHead className='text-right'>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {patients.map((p) => (
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
                      <TableCell className='text-right'>
                        <div className='flex justify-end gap-2'>
                          <Button variant='outline' size='sm' onClick={() => onEdit(p)}>
                            Edit
                          </Button>
                          <Button variant='destructive' size='sm' onClick={() => onDelete(p.id)}>
                            Delete
                          </Button>
                        </div>
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
