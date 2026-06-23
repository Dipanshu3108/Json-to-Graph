import { useStudioStore } from "../store/useStudioStore";
import { SchemaExamples } from "./SchemaExamples";

const STATUS_CONFIG = {
  idle: { text: "Paste JSON to get started", tone: "muted" },
  validating: { text: "Validating...", tone: "info" },
  valid: { text: "Valid - chart rendered", tone: "ok" },
  invalid: { text: "Schema invalid", tone: "bad" },
  repairing: { text: "Asking AI to repair...", tone: "warn" },
  repaired: { text: "AI repaired the schema", tone: "ok" },
  "repair-failed": { text: "Repair failed", tone: "bad" },
} as const;

export function StatusBar(): JSX.Element {
  const validationStatus = useStudioStore((s) => s.validationStatus);
  const validationErrors = useStudioStore((s) => s.validationErrors);
  const repairChanges = useStudioStore((s) => s.repairChanges);
  const parseError = useStudioStore((s) => s.parseError);
  const isGeneratingCode = useStudioStore((s) => s.isGeneratingCode);
  const runRepair = useStudioStore((s) => s.runRepair);
  const isBusy = validationStatus === "validating" || validationStatus === "repairing" || isGeneratingCode;

  const cfg = STATUS_CONFIG[validationStatus];

  return (
    <section className="panel">
      <header className="panel-header">Status</header>
      {parseError && <div className="error-row">JSON parse error: {parseError}</div>}

      <div className={`status ${cfg.tone}`}>
        <span>{cfg.text}</span>
        {(validationStatus === "invalid" || !!parseError) && (
          <button onClick={() => void runRepair()} disabled={isBusy}>
            {validationStatus === "repairing" ? "Repairing..." : "Ask AI to repair"}
          </button>
        )}
      </div>

      {validationStatus === "invalid" && validationErrors.length > 0 && (
        <details className="issue-dropdown">
          <summary>
            {validationErrors.length} issue{validationErrors.length !== 1 ? "s" : ""} detected — expand to view
          </summary>
          <ul className="issues">
            {validationErrors.map((error, idx) => (
              <li key={`${error.field}-${idx}`}>
                <strong>{error.field}</strong>: {error.message}
                {error.suggestion ? ` — ${error.suggestion}` : ""}
              </li>
            ))}
          </ul>
        </details>
      )}

      {(validationStatus === "repaired" || validationStatus === "repair-failed") && repairChanges.length > 0 && (
        <details className="issue-dropdown" open>
          <summary>
            {repairChanges.length} fix{repairChanges.length !== 1 ? "es" : ""} applied — expand to view
          </summary>
          <ul className="issues changes">
            {repairChanges.map((change, idx) => (
              <li key={`${change}-${idx}`}>{change}</li>
            ))}
          </ul>
        </details>
      )}

      <SchemaExamples />
    </section>
  );
}
