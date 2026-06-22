import { useEffect, useRef } from "react";

import { useStudioStore } from "../store/useStudioStore";

const DEBOUNCE_MS = 600;

export function useValidate(): void {
  const rawJson = useStudioStore((s) => s.rawJson);
  const chartType = useStudioStore((s) => s.chartType);
  const parseError = useStudioStore((s) => s.parseError);
  const runValidation = useStudioStore((s) => s.runValidation);
  const timer = useRef<number | undefined>(undefined);

  useEffect(() => {
    window.clearTimeout(timer.current);

    if (!rawJson.trim() || parseError) return;

    timer.current = window.setTimeout(() => {
      void runValidation();
    }, DEBOUNCE_MS);

    return () => window.clearTimeout(timer.current);
  }, [rawJson, chartType, parseError, runValidation]);
}
