import type { ChartType } from "../types";
import { useStudioStore } from "../store/useStudioStore";

const EXAMPLES: Record<ChartType, string> = {
  bar: JSON.stringify(
    {
      labels: ["Jan", "Feb", "Mar"],
      datasets: [{ label: "Revenue", data: [120, 200, 150] }],
    },
    null,
    2
  ),
  line: JSON.stringify(
    {
      labels: ["Jan", "Feb", "Mar"],
      datasets: [{ label: "Users", data: [120, 200, 150] }],
    },
    null,
    2
  ),
  area: JSON.stringify(
    {
      labels: ["Jan", "Feb", "Mar"],
      datasets: [{ label: "Signups", data: [120, 200, 150] }],
    },
    null,
    2
  ),
  pie: JSON.stringify(
    {
      labels: ["Desktop", "Mobile", "Tablet"],
      datasets: [{ label: "Traffic", data: [60, 30, 10] }],
    },
    null,
    2
  ),
  doughnut: JSON.stringify(
    {
      labels: ["Desktop", "Mobile", "Tablet"],
      datasets: [{ label: "Traffic", data: [60, 30, 10] }],
    },
    null,
    2
  ),
  scatter: JSON.stringify(
    {
      datasets: [
        {
          label: "Samples",
          data: [
            { x: 1, y: 2 },
            { x: 2, y: 4 },
            { x: 3, y: 5 },
          ],
        },
      ],
    },
    null,
    2
  ),
};

export function SchemaExamples(): JSX.Element {
  const chartType = useStudioStore((s) => s.chartType);
  const setRawJson = useStudioStore((s) => s.setRawJson);
  const validationStatus = useStudioStore((s) => s.validationStatus);
  const isGeneratingCode = useStudioStore((s) => s.isGeneratingCode);
  const isBusy = validationStatus === "validating" || validationStatus === "repairing" || isGeneratingCode;

  const example = EXAMPLES[chartType];

  return (
    <div className="schema-examples">
      <div className="schema-examples-header">
        <span>Valid schema for <strong>{chartType}</strong></span>
        <button
          type="button"
          className="ghost"
          onClick={() => setRawJson(example)}
          disabled={isBusy}
        >
          Load example
        </button>
      </div>
      <pre className="schema-examples-code">{example}</pre>
    </div>
  );
}
