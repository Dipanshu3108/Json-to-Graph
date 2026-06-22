import type { Theme } from "../types";
import { useStudioStore } from "../store/useStudioStore";

const THEMES: Theme[] = ["default", "dark", "pastel", "vivid"];

export function ThemeSelector(): JSX.Element {
  const theme = useStudioStore((s) => s.theme);
  const setTheme = useStudioStore((s) => s.setTheme);
  const validationStatus = useStudioStore((s) => s.validationStatus);
  const isGeneratingCode = useStudioStore((s) => s.isGeneratingCode);
  const isBusy = validationStatus === "validating" || validationStatus === "repairing" || isGeneratingCode;

  return (
    <label className="control">
      <span>Theme</span>
      <select value={theme} onChange={(e) => setTheme(e.target.value as Theme)} disabled={isBusy}>
        {THEMES.map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
      </select>
    </label>
  );
}
