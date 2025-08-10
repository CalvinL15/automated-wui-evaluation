import {useQuery} from '@tanstack/react-query';

import {getEvaluationResults, getInputData,getMetrics} from "./client";

export function useMetrics() {
  return useQuery({
    queryKey: ['getMetrics'],
    queryFn: () => getMetrics(),
    refetchOnReconnect: false,
    refetchOnWindowFocus: false,
    retry: false
  });
}

export function useEvaluationResults(wui_id: string) {
  return useQuery({
    queryKey: [`getEvaluationResults/${wui_id}`],
    queryFn: () => getEvaluationResults(wui_id),
    refetchOnReconnect: true,
    refetchOnWindowFocus: false,
    retry: 5
  });
}

export function useInputData(wui_id: string) {
  return useQuery({
    queryKey: [`getInputData/${wui_id}`],
    queryFn: () => getInputData(wui_id),
    refetchOnReconnect: false,
    refetchOnWindowFocus: false,
    retry: 5
  });
}


