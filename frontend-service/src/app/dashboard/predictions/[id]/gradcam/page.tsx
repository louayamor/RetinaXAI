'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { motion, useReducedMotion } from 'motion/react';
import { getPrediction, getPatient, listAllPredictions } from '@/lib/api';
import PageContainer from '@/components/layout/page-container';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, ArrowRight, Eye, ImageIcon, Loader } from 'lucide-react';
import type { Prediction, Patient } from '@/types';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000').replace(/\/$/, '');
const GRADE_LABELS = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative'];
const GRADE_COLORS: Record<number, string> = {
  0: 'bg-emerald-500',
  1: 'bg-cyan-500',
  2: 'bg-amber-500',
  3: 'bg-orange-500',
  4: 'bg-rose-500',
};

const GRADE_COLORS_FALLBACK: Record<string, string> = {
  0: 'bg-emerald-500',
  1: 'bg-cyan-500',
  2: 'bg-amber-500',
  3: 'bg-orange-500',
  4: 'bg-rose-500',
};

interface Props {
  showOverlay: boolean;
  onToggle: () => void;
  title: string;
  gradcamBase64?: string;
}

function GradCAMImageCard({ showOverlay, onToggle, title, gradcamBase64 }: Props) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg">{title}</CardTitle>
        <Button variant="outline" size="sm" onClick={onToggle}>
          <Eye className="mr-2 h-4 w-4" />
          {showOverlay ? 'Show Original' : 'Show Overlay'}
        </Button>
      </CardHeader>
      <CardContent>
        {gradcamBase64 ? (
          <div className="relative aspect-square rounded-lg overflow-hidden bg-black">
            <img
              src={`data:image/png;base64,${gradcamBase64}`}
              alt={title}
              className="w-full h-full object-contain"
            />
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center aspect-square bg-muted rounded-lg">
            <ImageIcon className="h-12 w-12 text-muted-foreground" />
            <p className="mt-2 text-sm text-muted-foreground">No GradCAM available</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function GradCAMPage() {
  const params = useParams();
  const router = useRouter();
  const shouldReduceMotion = useReducedMotion();

  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [patient, setPatient] = useState<Patient | null>(null);
  const [showOverlay, setShowOverlay] = useState(true);
  const [allPredictions, setAllPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [params.id]);

  const loadData = async () => {
    try {
      setLoading(true);
      const pred = await getPrediction(params.id as string);
      setPrediction(pred);

      const patientData = await getPatient(pred.patient_id);
      setPatient(patientData);

      const response = await listAllPredictions(1, 100);
      setAllPredictions(response.items);
    } catch (err) {
      console.error('Failed to load prediction:', err);
    } finally {
      setLoading(false);
    }
  };

  const currentIndex = allPredictions.findIndex((p) => p.id === params.id);
  const prevPrediction = currentIndex > 0 ? allPredictions[currentIndex - 1] : null;
  const nextPrediction = currentIndex < allPredictions.length - 1 ? allPredictions[currentIndex + 1] : null;

  const gradcamLeft = prediction?.output_payload?.gradcam_left as string | undefined;
  const gradcamRight = prediction?.output_payload?.gradcam_right as string | undefined;
  const grade = prediction?.output_payload?.combined_grade as number | undefined;
  const gradeLabel = grade !== undefined ? GRADE_LABELS[grade] : null;
  const gradeColor = grade !== undefined ? (GRADE_COLORS_FALLBACK[grade] || 'bg-muted') : 'bg-muted';

  if (loading) {
    return (
      <PageContainer>
        <div className="flex h-96 items-center justify-center">
          <Loader className="h-8 w-8 animate-spin text-[var(--brand-teal)]" />
        </div>
      </PageContainer>
    );
  }

  if (!prediction) {
    return (
      <PageContainer>
        <div className="flex flex-col items-center justify-center py-12">
          <p className="text-muted-foreground">Prediction not found</p>
          <Button variant="outline" className="mt-4" onClick={() => router.back()}>
            Back to Predictions
          </Button>
        </div>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <motion.div
        variants={shouldReduceMotion ? {} : { hidden: { opacity: 0 }, visible: { opacity: 1 } }}
        initial="hidden"
        animate="visible"
        className="flex flex-col gap-6"
      >
        {/* Header */}
        <div className="flex items-center justify-between">
          <Button variant="ghost" onClick={() => router.back()}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Predictions
          </Button>
          <h1 className="text-2xl font-bold">DR Screening Analysis</h1>
        </div>

        {/* Patient Info */}
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-4 text-sm flex-wrap">
              <span>
                <strong>Patient:</strong> {patient?.first_name} {patient?.last_name}
              </span>
              <span>|</span>
              <span>
                <strong>Date:</strong> {new Date(prediction.created_at).toLocaleString()}
              </span>
              <span>|</span>
              <span>
                <strong>Grade:</strong>{' '}
                {gradeLabel ? (
                  <Badge className={gradeColor}>{gradeLabel}</Badge>
                ) : (
                  'N/A'
                )}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* GradCAM Images */}
        <div className="grid md:grid-cols-2 gap-6">
          <GradCAMImageCard
            title="Left Eye (OS)"
            gradcamBase64={gradcamLeft}
            showOverlay={showOverlay}
            onToggle={() => setShowOverlay(!showOverlay)}
          />
          <GradCAMImageCard
            title="Right Eye (OD)"
            gradcamBase64={gradcamRight}
            showOverlay={showOverlay}
            onToggle={() => setShowOverlay(!showOverlay)}
          />
        </div>

        {/* Prediction Details */}
        <Card>
          <CardHeader>
            <CardTitle>Prediction Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Confidence</p>
                <p className="text-2xl font-bold">
                  {prediction.confidence_score ? `${(prediction.confidence_score * 100).toFixed(1)}%` : 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Model</p>
                <p className="font-medium">{prediction.model_name}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Version</p>
                <p className="font-medium">{prediction.model_version}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Class Probabilities */}
        {(prediction.output_payload as any)?.left_eye?.probabilities && (
          <Card>
            <CardHeader>
              <CardTitle>Class Probabilities (Left Eye)</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {Object.entries((prediction.output_payload as any).left_eye.probabilities as Record<string, number>).map(
                ([label, prob]) => {
                  const percentage = (prob as number) * 100;
                  const isSelected = label === gradeLabel;
                  return (
                    <div key={label} className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className={isSelected ? 'font-bold' : ''}>{label}</span>
                        <span>{percentage.toFixed(1)}%</span>
                      </div>
                      <div className="h-2 bg-muted rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${percentage}%` }}
                          transition={{ duration: 0.5 }}
                          className={`h-full ${isSelected ? 'bg-[var(--brand-teal)]' : 'bg-[var(--brand-teal)]/50'}`}
                        />
                      </div>
                    </div>
                  );
                }
              )}
            </CardContent>
          </Card>
        )}

        {/* Navigation */}
        <div className="flex justify-between">
          <Button
            variant="outline"
            onClick={() => router.push(`/dashboard/predictions/${prevPrediction?.id}/gradcam`)}
            disabled={!prevPrediction}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Previous
          </Button>
          <Button
            variant="outline"
            onClick={() => router.push(`/dashboard/predictions/${nextPrediction?.id}/gradcam`)}
            disabled={!nextPrediction}
          >
            Next
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </motion.div>
    </PageContainer>
  );
}
