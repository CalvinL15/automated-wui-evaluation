export interface InputDataType {
  id: string;
  wui_name: string;
  screenshot_url: string | undefined;
  html_url: string | undefined;
  metrics_to_evaluate: string[];
  created_at: string;
}