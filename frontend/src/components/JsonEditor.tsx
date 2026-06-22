import MonacoEditor from "@monaco-editor/react";

import { useStudioStore } from "../store/useStudioStore";

export function JsonEditor(): JSX.Element {
  const rawJson = useStudioStore((s) => s.rawJson);
  const setRawJson = useStudioStore((s) => s.setRawJson);
  const validationStatus = useStudioStore((s) => s.validationStatus);
  const isGeneratingCode = useStudioStore((s) => s.isGeneratingCode);
  const isBusy = validationStatus === "validating" || validationStatus === "repairing" || isGeneratingCode;

  return (
    <section className="panel">
      <header className="panel-header">JSON Input</header>
      <div className="editor-wrap">
        <MonacoEditor
          height="100%"
          language="json"
          value={rawJson}
          onChange={(value) => setRawJson(value ?? "")}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 13,
            wordWrap: "on",
            automaticLayout: true,
            readOnly: isBusy,
          }}
        />
      </div>
    </section>
  );
}
