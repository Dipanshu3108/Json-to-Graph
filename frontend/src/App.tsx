import { Suspense, lazy } from "react";

import { ChartPreview } from "./components/ChartPreview";
import { ChartTypeSelector } from "./components/ChartTypeSelector";
import { CodePreview } from "./components/CodePreview";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { StatusBar } from "./components/StatusBar";
import { ThemeSelector } from "./components/ThemeSelector";
import { useValidate } from "./hooks/useValidate";

const JsonEditor = lazy(() => import("./components/JsonEditor").then((m) => ({ default: m.JsonEditor })));

export default function App(): JSX.Element {
  useValidate();

  return (
    <ErrorBoundary>
      <main className="app">
        <aside className="left">
          <div className="toolbar">
            <ChartTypeSelector />
            <ThemeSelector />
          </div>
          <Suspense fallback={<section className="panel">Loading editor...</section>}>
            <JsonEditor />
          </Suspense>
          <StatusBar />
        </aside>

        <section className="right">
          <ChartPreview />
          <CodePreview />
        </section>
      </main>
    </ErrorBoundary>
  );
}
