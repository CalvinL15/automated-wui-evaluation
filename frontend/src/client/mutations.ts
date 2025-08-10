import {useMutation} from "@tanstack/react-query";

import {MetricExtensionRequestMetadataType} from "../types/MetricExtensionRequestMetadataType";
import {
  evaluateFileInput,
  evaluateUrlInput,
  processMetricExtensionRequest
} from "./client";

export function useEvaluateUrlInput() {
  return useMutation({
    mutationFn: ({url, metrics}: {url: string; metrics: string[]}) => evaluateUrlInput(url, metrics),
    onSuccess: () => {
      console.log('Input evaluated successfully!');
    },
    onError: (err: Error) => {
      console.log(err.message);
    }
  });
}

export function useEvaluateFileInput() {
  return useMutation({
    mutationFn: ({file, metrics}: {file: File; metrics: string[]}) => evaluateFileInput(file, metrics),
    onSuccess: () => {
      console.log('Input evaluated successfully!');
    },
    onError: (err: Error) => {
      console.log(err.message);
    }
  });
}

export function useProcessMetricExtensionRequest() {
  return useMutation({
    mutationFn: (
      {files, metricExtensionRequestMetadata}:
        {files: File[]; metricExtensionRequestMetadata: MetricExtensionRequestMetadataType}) => processMetricExtensionRequest(files, metricExtensionRequestMetadata),
    onSuccess: () => {
      console.log('Input evaluated successfully!');
    },
    onError: (err: Error) => {
      console.log(err.message);
    }
  });
}