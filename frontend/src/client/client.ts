import ky from 'ky';

import {EvaluationResultType} from "@/types/EvaluationResultType";
import {InputDataType} from "@/types/InputDataType";
import {MetricExtensionRequestMetadataType} from "@/types/MetricExtensionRequestMetadataType";
import {MetricsType} from "@/types/MetricType";
const prefixUrl = import.meta.env.VITE_PREFIX_URL;

const client = ky.create(
  {
    prefixUrl: prefixUrl,
    timeout: false,
    // headers: {
    //   'ngrok-skip-browser-warning': true
    // }
  }
);

export async function getMetrics(): Promise<MetricsType> {
  return client.get('metrics').json();
}

export function getEvaluationResults(
  wui_id: string
): Promise<EvaluationResultType[]> | '' {
  if (wui_id !== 'result')
    return client.get(`result/${wui_id}`).json();
  return '';
}

export function getInputData(
  wui_id: string
): Promise<InputDataType> | '' {
  if (wui_id !== 'result')
    return client.get(`data/${wui_id}`).json();
  return '';
}

export function evaluateUrlInput(
  url: string,
  metrics: string[]
) {
  return client.post('evaluate_url_input',{json: { url, metrics }}).json();
}

export function evaluateFileInput(file: File, metrics: string[]) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('metrics', JSON.stringify({metrics}));

  return client.post('evaluate_file_input', {
    body: formData
  }).json();
}

export function processMetricExtensionRequest(files: File[], metricExtensionRequestMetadata: MetricExtensionRequestMetadataType) {
  const formData = new FormData();
  files.forEach(file =>
  {
    formData.append('files', file.file);
  });
  formData.append('metadata', JSON.stringify({metricExtensionRequestMetadata}));
  return client.post('extension', {
    body: formData
  }).json();
}

