import { useState } from "react";
import { generateCode } from "../services/api";
import { useStudioStore } from "../store/useStudioStore";

export function CodePreview(): JSX.Element {
  const activeData = useStudioStore((s) => s.activeData);
  const parsedInput = useStudioStore((s) => s.parsedInput);
  const rawJson = useStudioStore((s) => s.rawJson);
  const chartType = useStudioStore((s) => s.chartType);
  const theme = useStudioStore((s) => s.theme);
  const validationStatus = useStudioStore((s) => s.validationStatus);
  const generatedCode = useStudioStore((s) => s.generatedCode);
  const isGeneratingCode = useStudioStore((s) => s.isGeneratingCode);
  const setGeneratedCode = useStudioStore((s) => s.setGeneratedCode);
  const setIsGeneratingCode = useStudioStore((s) => s.setIsGeneratingCode);

  const [customChartDesc, setCustomChartDesc] = useState("");
  const isBusy = validationStatus === "validating" || validationStatus === "repairing" || isGeneratingCode;
  const generationData = activeData ?? parsedInput ?? rawJson.trim();
  const canGenerate = Boolean(generationData) && !isBusy;

  const handleGenerate = async () => {
    if (!generationData) return;
    const chartTypeToUse = customChartDesc.trim() || chartType;
    console.info("[CodePreview] handleGenerate chartType=%s", chartTypeToUse);
    setIsGeneratingCode(true);
    try {
      const res = await generateCode(chartTypeToUse, generationData, theme);
      if (res.error && !res.code) {
        console.warn("[CodePreview] generateCode returned error", res.error);
        setGeneratedCode(`<!doctype html><html><body><pre>${res.error}</pre></body></html>`);
      } else {
        console.info("[CodePreview] generateCode success codeLen=%d", res.code.length);
        setGeneratedCode(res.code);
      }
    } catch (error) {
      console.error("[CodePreview] generateCode threw", error);
      setGeneratedCode(`<!doctype html><html><body><pre>${String(error)}</pre></body></html>`);
    } finally {
      setIsGeneratingCode(false);
    }
  };

  return (
    <section className="panel">
      <header className="panel-header split">
        <span>LLM HTML Preview</span>
        <div>
          <button onClick={() => void handleGenerate()} disabled={!canGenerate}>
            {isGeneratingCode ? "Generating..." : "Generate with AI"}
          </button>
          {generatedCode && (
            <button className="ghost" onClick={() => setGeneratedCode(null)} disabled={isBusy}>
              Clear
            </button>
          )}
        </div>
      </header>
      <div className="chart-desc-row">
        <input
          type="text"
          className="chart-desc-input"
          placeholder="Describe a new chart type (e.g. radar, gauge, treemap, heatmap…)"
          value={customChartDesc}
          onChange={(e) => setCustomChartDesc(e.target.value)}
          disabled={isBusy}
        />
      </div>
      {generatedCode ? (
        <iframe title="Generated Chart" srcDoc={generatedCode} sandbox="allow-scripts" className="iframe" />
      ) : (
        <div className="empty">Describe a chart type above and click Generate with AI.</div>
      )}
    </section>
  );
}
