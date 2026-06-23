export type ChartType = "bar" | "line" | "pie" | "doughnut" | "area" | "scatter";
export type Theme = "default" | "dark" | "pastel" | "vivid";
export type RenderMode = "echarts" | "llm-generated";

export interface Dataset {
  label: string;
  data: number[];
}

export interface ScatterPoint {
  x: number;
  y: number;
  label?: string;
}

export interface ScatterDataset {
  label: string;
  data: ScatterPoint[];
}

export interface ChartInput {
  labels: string[];
  datasets: Dataset[];
}

export interface ScatterInput {
  datasets: ScatterDataset[];
}

export type AnyChartInput = ChartInput | ScatterInput;
export type JsonObject = Record<string, unknown>;
export type JsonPayload = AnyChartInput | JsonObject | unknown[] | string;

export type ValidationStatus =
  | "idle"
  | "validating"
  | "valid"
  | "invalid"
  | "repairing"
  | "repaired"
  | "repair-failed";

export interface ValidationError {
  field: string;
  message: string;
  suggestion?: string;
}

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  normalizedData?: AnyChartInput;
}

export interface ValidateResponse {
  valid: boolean;
  errors: ValidationError[];
  normalizedData?: AnyChartInput;
}

export interface RepairResponse {
  fixed: boolean;
  normalizedData?: AnyChartInput;
  changes: string[];
  generatedDataPoints: string[];
  error?: string;
}

export interface GenerateCodeResponse {
  code: string;
  error?: string;
}

export interface ApiError {
  status: number;
  code: string;
  message: string;
}

export interface StudioState {
  rawJson: string;
  parsedInput: JsonPayload | null;
  parseError: string | null;

  chartType: ChartType;
  theme: Theme;
  renderMode: RenderMode;

  validationStatus: ValidationStatus;
  validationErrors: ValidationError[];
  repairedData: AnyChartInput | null;
  repairChanges: string[];
  generatedDataPoints: string[];

  activeData: AnyChartInput | null;

  generatedCode: string | null;
  isGeneratingCode: boolean;
}
