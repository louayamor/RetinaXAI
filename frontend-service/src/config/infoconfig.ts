import type { InfobarContent } from '@/components/ui/infobar';

export const patientsInfoContent: InfobarContent = {
  title: 'Patient Management',
  sections: [
    {
      title: 'Overview',
      description:
        'The Patients page allows you to manage your patient registry. You can view all registered patients, create new patient records, and access individual patient details including their scan history.',
      links: []
    },
    {
      title: 'Adding Patients',
      description:
        'To add a new patient, click the "New Patient" button. Fill in the required demographic information. Once created, you can upload retinal scans and run predictions for that patient.',
      links: []
    }
  ]
};

export const predictionsInfoContent: InfobarContent = {
  title: 'Predictions',
  sections: [
    {
      title: 'Overview',
      description:
        'The Predictions page shows all DR grading results produced by the model. Each prediction includes a severity classification and a Grad-CAM heatmap for explainability.',
      links: []
    },
    {
      title: 'DR Severity Grades',
      description:
        'The model classifies scans into five grades: No DR, Mild, Moderate, Severe, and Proliferative DR. Higher grades indicate more advanced disease requiring urgent clinical attention.',
      links: []
    }
  ]
};

export const reportsInfoContent: InfobarContent = {
  title: 'Reports',
  sections: [
    {
      title: 'Overview',
      description:
        'The Reports page allows you to generate and view LLM-powered clinical summaries for each prediction. Reports are generated from the prediction result and stored for future reference.',
      links: []
    }
  ]
};

export const monitoringInfoContent: InfobarContent = {
  title: 'Model Monitoring',
  sections: [
    {
      title: 'Overview',
      description:
        'The Monitoring page displays live metrics from the inference service via Prometheus. Key indicators include prediction latency, request volume, and data drift scores.',
      links: []
    }
  ]
};