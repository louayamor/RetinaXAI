'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { motion, useReducedMotion } from 'motion/react';
import PageContainer from '@/components/layout/page-container';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { 
  ArrowLeft, 
  User, 
  Phone, 
  MapPin, 
  Calendar,
  Scan,
  FileText,
  Activity,
  Eye,
  AlertCircle,
  CheckCircle,
  XCircle,
  Loader
} from 'lucide-react';
import { getPatient, getPatientScans, getPatientOctReports, listPatientPredictions, listPatientReports } from '@/lib/api';
import type { Patient, MRIScan, OCTReport, Prediction, Report, PaginatedResponse } from '@/types';
import { fadeInUp, slideInUp, staggerItem } from '@/lib/animations';
import Image from 'next/image';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000').replace(/\/$/, '');
const GRADE_LABELS = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative'];
const GRADE_COLORS: Record<string, string> = {
  no_dr: 'bg-emerald-500',
  mild: 'bg-cyan-500', 
  moderate: 'bg-amber-500',
  severe: 'bg-orange-500',
  proliferative: 'bg-rose-500',
};

export default function PatientProfilePage() {
  const params = useParams();
  const router = useRouter();
  const patientId = params.id as string;
  const shouldReduceMotion = useReducedMotion();

  const [patient, setPatient] = useState<Patient | null>(null);
  const [scans, setScans] = useState<MRIScan[]>([]);
  const [octReports, setOctReports] = useState<OCTReport[]>([]);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);

  useEffect(() => {
    loadPatientData();
  }, [patientId]);

  const loadPatientData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [patientData, scansData, octData, predsData, repsData] = await Promise.all([
        getPatient(patientId),
        getPatientScans(patientId),
        getPatientOctReports(patientId),
        listPatientPredictions(patientId, 1, 100),
        listPatientReports(patientId, 1, 100),
      ]);

      setPatient(patientData);
      setScans(scansData);
      setOctReports(octData);
      setPredictions((predsData as PaginatedResponse<Prediction>).items);
      setReports((repsData as PaginatedResponse<Report>).items);
    } catch (err) {
      console.error('Failed to load patient data:', err);
      setError('Failed to load patient data');
    } finally {
      setLoading(false);
    }
  };

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName[0]}${lastName[0]}`.toUpperCase();
  };

  const getGenderColor = (gender: string) => {
    return gender === 'M' ? 'from-blue-500 to-blue-700' : 'from-pink-500 to-pink-700';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-emerald-500" />;
      case 'pending':
      case 'running':
      case 'generating':
        return <Loader className="h-4 w-4 text-amber-500 animate-spin" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-rose-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const EmptyState = ({ icon: Icon, title, description }: { icon: typeof Scan; title: string; description: string }) => (
    <div className="flex flex-col items-center justify-center py-12 bg-muted/30 rounded-lg">
      <Icon className="h-12 w-12 mb-3 opacity-50 text-muted-foreground" />
      <p className="text-muted-foreground font-medium">{title}</p>
      <p className="text-sm text-muted-foreground/70">{description}</p>
    </div>
  );

  if (loading) {
    return (
      <PageContainer>
        <div className="flex h-96 items-center justify-center">
          <Loader className="h-8 w-8 animate-spin text-[#20bdbe]" />
        </div>
      </PageContainer>
    );
  }

  if (error || !patient) {
    return (
      <PageContainer>
        <div className="flex flex-col items-center justify-center py-12">
          <AlertCircle className="h-12 w-12 mb-3 text-rose-500" />
          <p className="text-rose-500 font-medium">{error || 'Patient not found'}</p>
          <Button variant="outline" className="mt-4" onClick={() => router.push('/dashboard/patients')}>
            Back to Patients
          </Button>
        </div>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <motion.div
        variants={shouldReduceMotion ? {} : fadeInUp}
        initial="hidden"
        animate="visible"
        className="flex flex-col gap-6"
      >
        {/* Header */}
        <motion.div variants={shouldReduceMotion ? {} : slideInUp} className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => router.push('/dashboard/patients')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <h1 className="text-2xl font-bold">Patient Profile</h1>
        </motion.div>

        {/* Patient Info Card */}
        <motion.div variants={shouldReduceMotion ? {} : staggerItem}>
          <Card>
            <CardHeader className="bg-gradient-to-r from-muted/30 to-transparent">
              <div className="flex items-center gap-4">
                <Avatar className="h-16 w-16">
                  <AvatarFallback className={`text-xl bg-gradient-to-br ${getGenderColor(patient.gender)} text-white`}>
                    {getInitials(patient.first_name, patient.last_name)}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <CardTitle className="text-2xl">
                    {patient.first_name} {patient.last_name}
                  </CardTitle>
                  <div className="flex items-center gap-3 mt-1">
                    <Badge variant="outline">{patient.gender === 'M' ? 'Male' : 'Female'}</Badge>
                    <span className="text-muted-foreground">{patient.age} years old</span>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <div className="bg-muted/50 rounded-lg p-3">
                <p className="text-xs text-muted-foreground">Medical Record #</p>
                <p className="font-mono font-medium">{patient.medical_record_number}</p>
              </div>
              <div className="bg-muted/50 rounded-lg p-3">
                <p className="text-xs text-muted-foreground">Phone</p>
                <p className="font-medium">{patient.phone || 'Not Available'}</p>
              </div>
              <div className="bg-muted/50 rounded-lg p-3">
                <p className="text-xs text-muted-foreground">Registered</p>
                <p className="font-medium flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  {new Date(patient.created_at).toLocaleDateString()}
                </p>
              </div>
              {patient.address && (
                <div className="bg-muted/50 rounded-lg p-3 md:col-span-2">
                  <p className="text-xs text-muted-foreground">Address</p>
                  <p className="font-medium">{patient.address}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <motion.div variants={shouldReduceMotion ? {} : staggerItem}>
            <Card className="border-l-4 border-l-[#20bdbe]">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">MRI Scans</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold">{scans.length}</p>
              </CardContent>
            </Card>
          </motion.div>
          <motion.div variants={shouldReduceMotion ? {} : staggerItem}>
            <Card className="border-l-4 border-l-amber-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Predictions</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold">{predictions.length}</p>
              </CardContent>
            </Card>
          </motion.div>
          <motion.div variants={shouldReduceMotion ? {} : staggerItem}>
            <Card className="border-l-4 border-l-blue-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Reports</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold">{reports.length}</p>
              </CardContent>
            </Card>
          </motion.div>
          <motion.div variants={shouldReduceMotion ? {} : staggerItem}>
            <Card className="border-l-4 border-l-purple-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">OCT Scans</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold">{octReports.length}</p>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="scans" className="w-full">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="scans">Scans ({scans.length})</TabsTrigger>
            <TabsTrigger value="predictions">Predictions ({predictions.length})</TabsTrigger>
            <TabsTrigger value="reports">Reports ({reports.length})</TabsTrigger>
            <TabsTrigger value="oct">OCT ({octReports.length})</TabsTrigger>
            <TabsTrigger value="overview">Overview</TabsTrigger>
          </TabsList>

          {/* MRI Scans Tab */}
          <TabsContent value="scans">
            {scans.length === 0 ? (
              <EmptyState icon={Scan} title="No MRI Scans Available" description="Add scans to see them here" />
            ) : (
              <div className="grid gap-4 md:grid-cols-2">
                {scans.map((scan) => (
                  <Card key={scan.id}>
                    <CardHeader>
                      <CardTitle className="text-sm flex items-center gap-2">
                        <Scan className="h-4 w-4 text-[#20bdbe]" />
                        Scan {scan.id.slice(0, 8)}
                      </CardTitle>
                      <CardDescription>
                        {new Date(scan.uploaded_at).toLocaleString()}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="grid grid-cols-2 gap-2">
                      <div className="relative aspect-square rounded-lg bg-muted overflow-hidden">
                        {scan.left_scan_path ? (
                          <Image src={`${API_BASE}/` + scan.left_scan_path} alt="Left eye" fill className="object-cover" unoptimized />
                        ) : (
                          <div className="flex items-center justify-center h-full text-muted-foreground">No image</div>
                        )}
                        <span className="absolute bottom-2 left-2 bg-black/50 text-white text-xs px-2 py-1 rounded">Left</span>
                      </div>
                      <div className="relative aspect-square rounded-lg bg-muted overflow-hidden">
                        {scan.right_scan_path ? (
                          <Image src={`${API_BASE}/` + scan.right_scan_path} alt="Right eye" fill className="object-cover" unoptimized />
                        ) : (
                          <div className="flex items-center justify-center h-full text-muted-foreground">No image</div>
                        )}
                        <span className="absolute bottom-2 right-2 bg-black/50 text-white text-xs px-2 py-1 rounded">Right</span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Predictions Tab */}
          <TabsContent value="predictions">
            {predictions.length === 0 ? (
              <EmptyState icon={FileText} title="No Predictions Available" description="Run predictions to see them here" />
            ) : (
              <div className="space-y-3">
                {predictions.map((pred) => {
                  const grade = pred.output_payload?.combined_grade as number | undefined;
                  const gradeLabel = grade !== undefined ? GRADE_LABELS[grade] : null;
                  return (
                  <Card key={pred.id}>
                    <CardContent className="py-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-3">
                          {getStatusIcon(pred.status)}
                          <div>
                            <p className="font-medium">{pred.model_name}</p>
                            <p className="text-sm text-muted-foreground">
                              {new Date(pred.created_at).toLocaleString()}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">
                            {pred.confidence_score ? `${(pred.confidence_score * 100).toFixed(1)}%` : 'N/A'}
                          </p>
                          <Badge variant={pred.status === 'success' ? 'default' : 'secondary'}>
                            {pred.status}
                          </Badge>
                        </div>
                      </div>
                      <div className="flex items-center justify-between mt-2 pt-2 border-t">
                        <div className="flex items-center gap-2">
                          {gradeLabel && (
                            <>
                              <span className="text-sm text-muted-foreground">DR Grade:</span>
                              <Badge className={GRADE_COLORS[String(grade)] || 'bg-muted'}>
                                {gradeLabel}
                              </Badge>
                            </>
                          )}
                        </div>
                        {pred.status === 'success' && (
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => router.push(`/dashboard/predictions/${pred.id}/gradcam`)}
                          >
                            <Eye className="h-4 w-4 mr-1" />
                            View GradCAM
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                )})}
              </div>
            )}
          </TabsContent>

          {/* Reports Tab */}
          <TabsContent value="reports">
            {reports.length === 0 ? (
              <EmptyState icon={FileText} title="No Reports Available" description="Generate reports to see them here" />
            ) : (
              <div className="space-y-3">
                {reports.map((report) => (
                  <Dialog key={report.id}>
                    <DialogTrigger asChild>
                      <Card className="cursor-pointer hover:shadow-md transition-shadow">
                        <CardContent className="flex items-center justify-between py-4">
                          <div className="flex items-center gap-3">
                            {getStatusIcon(report.status)}
                            <div>
                              <p className="font-medium">{report.llm_model}</p>
                              <p className="text-sm text-muted-foreground">
                                {new Date(report.created_at).toLocaleString()}
                              </p>
                            </div>
                          </div>
                          <Badge variant={report.status === 'completed' ? 'default' : 'secondary'}>
                            {report.status}
                          </Badge>
                        </CardContent>
                      </Card>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                      <DialogHeader>
                        <DialogTitle>Clinical Report</DialogTitle>
                        <DialogDescription>
                          Generated by {report.llm_model} on {new Date(report.created_at).toLocaleString()}
                        </DialogDescription>
                      </DialogHeader>
                      <div className="mt-4 space-y-4">
                        {report.summary && (
                          <div>
                            <h4 className="font-semibold mb-2">Summary</h4>
                            <p className="text-sm">{report.summary}</p>
                          </div>
                        )}
                        {report.content && (
                          <div>
                            <h4 className="font-semibold mb-2">Full Report</h4>
                            <div className="text-sm whitespace-pre-wrap">{report.content}</div>
                          </div>
                        )}
                        {!report.content && !report.summary && (
                          <p className="text-muted-foreground">No report content available</p>
                        )}
                      </div>
                    </DialogContent>
                  </Dialog>
                ))}
              </div>
            )}
          </TabsContent>

          {/* OCT Reports Tab */}
          <TabsContent value="oct">
            {octReports.length === 0 ? (
              <EmptyState icon={Activity} title="No OCT Reports Available" description="Process OCT scans to see them here" />
            ) : (
              <Card>
                <CardContent className="p-0">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-3">Eye</th>
                        <th className="text-left p-3">DR Grade</th>
                        <th className="text-left p-3">Edema</th>
                        <th className="text-left p-3">ERM</th>
                        <th className="text-left p-3">Quality</th>
                        <th className="text-left p-3">Center Fovea (μm)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {octReports.map((oct) => (
                        <tr key={oct.id} className="border-b">
                          <td className="p-3">{oct.eye}</td>
                          <td className="p-3">
                            <Badge className={GRADE_COLORS[oct.dr_grade || ''] || 'bg-muted'}>
                              {oct.dr_grade || 'N/A'}
                            </Badge>
                          </td>
                          <td className="p-3">{oct.edema ? 'Yes' : 'No'}</td>
                          <td className="p-3">{oct.erm_status || 'N/A'}</td>
                          <td className="p-3">{oct.image_quality ? `${oct.image_quality}%` : 'N/A'}</td>
                          <td className="p-3">{oct.thickness_center_fovea || 'N/A'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Overview Tab */}
          <TabsContent value="overview">
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Patient Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex items-center gap-2">
                    <User className="h-4 w-4 text-muted-foreground" />
                    <span>{patient.first_name} {patient.last_name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span>{patient.age} years old • {patient.gender === 'M' ? 'Male' : 'Female'}</span>
                  </div>
                  {patient.phone && (
                    <div className="flex items-center gap-2">
                      <Phone className="h-4 w-4 text-muted-foreground" />
                      <span>{patient.phone}</span>
                    </div>
                  )}
                  {patient.address && (
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-muted-foreground" />
                      <span>{patient.address}</span>
                    </div>
                  )}
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <p><strong>MRN:</strong> {patient.medical_record_number}</p>
                  <p><strong>Registered:</strong> {new Date(patient.created_at).toLocaleDateString()}</p>
                  <p><strong>Total Scans:</strong> {scans.length}</p>
                  <p><strong>Total Predictions:</strong> {predictions.length}</p>
                  <p><strong>Total Reports:</strong> {reports.length}</p>
                  <p><strong>OCT Reports:</strong> {octReports.length}</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </motion.div>
    </PageContainer>
  );
}