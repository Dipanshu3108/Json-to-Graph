import type { AnyChartInput, ChartInput, ScatterInput } from "../types";

export interface PrecheckResult {
  ok: boolean;
  message?: string;
}

export function precheckInput(data: AnyChartInput, chartType: string): PrecheckResult {
  if (chartType === "scatter") {
    const scatter = data as ScatterInput;
    if (!Array.isArray(scatter.datasets)) {
      return { ok: false, message: "Scatter data requires datasets array." };
    }
    return { ok: true };
  }

  const regular = data as ChartInput;
  if (!Array.isArray(regular.labels) || !Array.isArray(regular.datasets)) {
    return { ok: false, message: "Expected labels[] and datasets[] fields." };
  }
  return { ok: true };
}
