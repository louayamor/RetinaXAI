'use client';

import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { FileText, User, Eye, AlertTriangle, CheckCircle, Clock, Download } from 'lucide-react';

interface ReportData {
  patient_info?: {
    name?: string;
    age?: string | number;
    gender?: string;
    mrn?: string;
  } | null;
  clinical_findings?: {
    left_eye?: {
      grade?: string;
      severity?: string;
      confidence?: number;
      description?: string;
    };
    right_eye?: {
      grade?: string;
      severity?: string;
      confidence?: number;
      description?: string;
    };
  } | null;
  diagnosis?: {
    condition?: string;
    severity?: string;
    overall_grade?: string;
    risk_level?: string;
  } | null;
  recommendations?: string[];
  summary?: string;
  report_metadata?: {
    generated_date?: string;
    model?: string;
    model_version?: string;
  } | null;
}

interface MedicalReportProps {
  report: {
    id: string;
    content: string | null;
    summary: string | null;
    llm_model: string;
    created_at: string;
  };
}

const SEVERITY_COLORS: Record<string, string> = {
  low: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  moderate: 'bg-amber-100 text-amber-800 border-amber-200',
  high: 'bg-orange-100 text-orange-800 border-orange-200',
  very_high: 'bg-red-100 text-red-800 border-red-200',
};

const GRADE_COLORS: Record<string, string> = {
  'No DR': 'bg-emerald-500',
  'Mild': 'bg-cyan-500',
  'Moderate': 'bg-amber-500',
  'Severe': 'bg-orange-500',
  'Proliferative DR': 'bg-rose-500',
};

export default function MedicalReport({ report }: MedicalReportProps) {
  let reportData: ReportData = {};
  
  try {
    if (report.content) {
      const parsed = JSON.parse(report.content);
      if (typeof parsed === 'object') {
        reportData = parsed;
      }
    }
  } catch {
    reportData = { summary: report.summary ?? undefined };
  }

  const { patient_info, clinical_findings, diagnosis, recommendations, summary, report_metadata } = reportData;

  const getRiskBadgeColor = (risk?: string) => {
    const lowerRisk = risk?.toLowerCase() || '';
    if (lowerRisk.includes('high') || lowerRisk.includes('severe')) return 'bg-red-500';
    if (lowerRisk.includes('moderate')) return 'bg-amber-500';
    return 'bg-emerald-500';
  };

  return (
    <Card className="overflow-hidden border-2">
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-white/20 p-2 rounded-lg">
              <FileText className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Clinical Diabetic Retinopathy Report</h2>
              <p className="text-blue-100 text-sm">AI-Generated Medical Assessment</p>
            </div>
          </div>
          <div className="text-right text-white">
            <p className="text-sm text-blue-100">Generated</p>
            <p className="font-medium">{new Date(report.created_at).toLocaleDateString()}</p>
            <p className="text-xs text-blue-200">{new Date(report.created_at).toLocaleTimeString()}</p>
          </div>
        </div>
      </div>

      <CardContent className="p-6 space-y-6">
        {patient_info && (
          <div className="bg-muted/30 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <User className="h-4 w-4 text-muted-foreground" />
              <h3 className="font-semibold text-sm uppercase tracking-wide text-muted-foreground">Patient Information</h3>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-xs text-muted-foreground">Patient Name</p>
                <p className="font-medium">{patient_info.name || 'N/A'}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Age</p>
                <p className="font-medium">{patient_info.age || 'N/A'}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Gender</p>
                <p className="font-medium">{patient_info.gender || 'N/A'}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">MRN</p>
                <p className="font-medium font-mono text-sm">{patient_info.mrn || 'N/A'}</p>
              </div>
            </div>
          </div>
        )}

        <Separator />

        {clinical_findings && (
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Eye className="h-4 w-4 text-muted-foreground" />
              <h3 className="font-semibold text-sm uppercase tracking-wide text-muted-foreground">Clinical Findings</h3>
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              {clinical_findings.left_eye && (
                <div className="border rounded-lg p-4 bg-blue-50/50">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-blue-900">Left Eye (OS)</h4>
                    <Badge className={GRADE_COLORS[clinical_findings.left_eye.grade || ''] || 'bg-gray-500'}>
                      {clinical_findings.left_eye.grade || 'N/A'}
                    </Badge>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Severity:</span>
                      <span className="font-medium capitalize">{clinical_findings.left_eye.severity || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Confidence:</span>
                      <span className="font-medium">{clinical_findings.left_eye.confidence ? `${(clinical_findings.left_eye.confidence * 100).toFixed(1)}%` : 'N/A'}</span>
                    </div>
                    {clinical_findings.left_eye.description && (
                      <p className="text-xs text-muted-foreground mt-2 pt-2 border-t">
                        {clinical_findings.left_eye.description}
                      </p>
                    )}
                  </div>
                </div>
              )}
              {clinical_findings.right_eye && (
                <div className="border rounded-lg p-4 bg-purple-50/50">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-purple-900">Right Eye (OD)</h4>
                    <Badge className={GRADE_COLORS[clinical_findings.right_eye.grade || ''] || 'bg-gray-500'}>
                      {clinical_findings.right_eye.grade || 'N/A'}
                    </Badge>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Severity:</span>
                      <span className="font-medium capitalize">{clinical_findings.right_eye.severity || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Confidence:</span>
                      <span className="font-medium">{clinical_findings.right_eye.confidence ? `${(clinical_findings.right_eye.confidence * 100).toFixed(1)}%` : 'N/A'}</span>
                    </div>
                    {clinical_findings.right_eye.description && (
                      <p className="text-xs text-muted-foreground mt-2 pt-2 border-t">
                        {clinical_findings.right_eye.description}
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {diagnosis && (
          <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-lg p-4 border border-red-100">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle className="h-4 w-4 text-red-600" />
              <h3 className="font-semibold text-sm uppercase tracking-wide text-red-900">Diagnosis</h3>
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-red-600">Condition</p>
                <p className="font-bold text-lg text-red-900">{diagnosis.condition || 'Diabetic Retinopathy'}</p>
              </div>
              <div>
                <p className="text-xs text-red-600">Overall Grade</p>
                <p className="font-bold text-lg text-red-900">{diagnosis.overall_grade || 'N/A'}</p>
              </div>
              <div className="md:col-span-2">
                <p className="text-xs text-red-600">Risk Assessment</p>
                <Badge className={`${getRiskBadgeColor(diagnosis.risk_level)} text-white mt-1`}>
                  {diagnosis.risk_level || 'Unknown Risk'}
                </Badge>
              </div>
            </div>
          </div>
        )}

        {(summary || report.summary) && (
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="h-4 w-4 text-blue-600" />
              <h3 className="font-semibold text-sm uppercase tracking-wide text-blue-900">Executive Summary</h3>
            </div>
            <p className="text-blue-900 leading-relaxed">
              {summary || report.summary}
            </p>
          </div>
        )}

        {recommendations && recommendations.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <h3 className="font-semibold text-sm uppercase tracking-wide text-muted-foreground">Recommendations</h3>
            </div>
            <div className="space-y-2">
              {recommendations.map((rec, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-muted/30 rounded-lg">
                  <div className="bg-primary text-primary-foreground w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0">
                    {index + 1}
                  </div>
                  <p className="text-sm leading-relaxed">{rec}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {report_metadata && (
          <div className="pt-4 border-t">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <div className="flex items-center gap-4">
                <span>Model: {report_metadata.model || report.llm_model}</span>
                {report_metadata.model_version && (
                  <span>Version: {report_metadata.model_version}</span>
                )}
              </div>
              <div className="flex items-center gap-2">
                <span>Generated: {report_metadata.generated_date || new Date(report.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
