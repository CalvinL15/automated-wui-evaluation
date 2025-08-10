interface PreprocessingType {
  dom_analysis_required: boolean;
  grayscale_conversion_required: boolean;
  jpeg_conversion_required: boolean;
  segmentation_required: boolean;
  lab_conversion_required: boolean;
}

export interface ReferenceType {
  title: string;
  url: string;
}

interface ScoresType {
  description: string;
  range: number[];
}


interface ResultType {
  description: string;
  name: string;
  type: 'text' | 'json' | 'image';
  scores?: ScoresType[];
}

export type AcceptedInputType = 'html' | 'url' | 'png';


export interface MetricType {
  accepted_input: AcceptedInputType[];
  description: string;
  name: string;
  preprocessing: PreprocessingType;
  references: ReferenceType[];
  results: ResultType[];
}

export interface MetricsType {
  metrics: MetricType[]
}