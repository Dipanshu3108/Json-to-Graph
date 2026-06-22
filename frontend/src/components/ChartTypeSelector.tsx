import type { ChartType } from "../types";
import { useStudioStore } from "../store/useStudioStore";

const TYPES: ChartType[] = ["bar", "line", "area", "pie", "doughnut", "scatter"];

export function ChartTypeSelector(): JSX.Element {
  const chartType = useStudioStore((s) => s.chartType);
  const setChartType = useStudioStore((s) => s.setChartType);
  const validationStatus = useStudioStore((s) => s.validationStatus);
  const isGeneratingCode = useStudioStore((s) => s.isGeneratingCode);
  const isBusy = validationStatus === "validating" || validationStatus === "repairing" || isGeneratingCode;

  return (
    <label className="control">
      <span>Chart Type</span>
      <select value={chartType} onChange={(e) => setChartType(e.target.value as ChartType)} disabled={isBusy}>
        {TYPES.map((type) => (
          <option key={type} value={type}>
            {type}
          </option>
        ))}
      </select>
    </label>
  );
}
