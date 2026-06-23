import { create } from "zustand";

import { repairChart, validateChart } from "../services/api";
import type { AnyChartInput, ChartType, JsonPayload, RenderMode, StudioState, Theme } from "../types";

interface StudioActions {
  setRawJson: (json: string) => void;
  setChartType: (type: ChartType) => void;
  setTheme: (theme: Theme) => void;
  setRenderMode: (mode: RenderMode) => void;
  runValidation: () => Promise<boolean>;
  runRepair: () => Promise<boolean>;
  setGeneratedCode: (code: string | null) => void;
  setIsGeneratingCode: (v: boolean) => void;
}

type StudioStore = StudioState & StudioActions;

const INITIAL: StudioState = {
  rawJson: "",
  parsedInput: null,
  parseError: null,
  chartType: "bar",
  theme: "default",
  renderMode: "echarts",
  validationStatus: "idle",
  validationErrors: [],
  repairedData: null,
  repairChanges: [],
  generatedDataPoints: [],
  activeData: null,
  generatedCode: null,
  isGeneratingCode: false,
};

export const useStudioStore = create<StudioStore>((set, get) => ({
  ...INITIAL,

  setRawJson(json) {
    let parsedInput: JsonPayload | null = null;
    let parseError: string | null = null;
    try {
      parsedInput = JSON.parse(json) as JsonPayload;
    } catch (error) {
      parseError = (error as Error).message;
    }

    console.info("[store] setRawJson parseError=%s", parseError);

    set({
      rawJson: json,
      parsedInput,
      parseError,
      validationStatus: "idle",
      validationErrors: [],
      activeData: null,
      repairedData: null,
      repairChanges: [],
      generatedDataPoints: [],
      generatedCode: null,
    });
  },

  setChartType(chartType) {
    console.info("[store] setChartType chartType=%s", chartType);
    set({ chartType, validationStatus: "idle", activeData: null, generatedDataPoints: [], generatedCode: null });
  },

  setTheme(theme) {
    console.info("[store] setTheme theme=%s", theme);
    set({ theme });
  },

  setRenderMode(renderMode) {
    console.info("[store] setRenderMode mode=%s", renderMode);
    set({ renderMode });
  },

  async runValidation() {
    const { parsedInput, parseError, chartType } = get();
    console.info("[store] runValidation start chartType=%s", chartType);

    if (parseError || !parsedInput) {
      console.info("[store] runValidation skipped reason=parse_error_or_empty");
      return false;
    }

    if (typeof parsedInput !== "object" || parsedInput === null || Array.isArray(parsedInput)) {
      console.info("[store] runValidation failed reason=root_not_object");
      set({
        validationStatus: "invalid",
        validationErrors: [
          {
            field: "root",
            message: "Validation expects a JSON object at the root.",
            suggestion: "Use an object like {\"labels\": [...], \"datasets\": [...]} or click Ask AI to repair.",
          },
        ],
        activeData: null,
      });
      return false;
    }

    const validationInput = parsedInput as Record<string, unknown>;

    set({ validationStatus: "validating" });

    try {
      const result = await validateChart(chartType, validationInput);

      if (result.valid) {
        console.info("[store] runValidation success");
        set({
          validationStatus: "valid",
          validationErrors: [],
          activeData: result.normalizedData ?? null,
        });
        return true;
      }

      console.info("[store] runValidation invalid errors=%d", result.errors.length);
      set({
        validationStatus: "invalid",
        validationErrors: result.errors,
        activeData: null,
      });
      return false;
    } catch (error) {
      const message = (error as { message?: string }).message ?? "Validation failed.";
      console.error("[store] runValidation error", error);
      set({
        validationStatus: "invalid",
        validationErrors: [{ field: "root", message }],
        activeData: null,
      });
      return false;
    }
  },

  async runRepair() {
    const { parsedInput, rawJson, chartType } = get();
    const repairInput = parsedInput ?? rawJson.trim();
    console.info("[store] runRepair start chartType=%s", chartType);

    if (!repairInput) {
      console.info("[store] runRepair skipped reason=no_input");
      return false;
    }

    set({ validationStatus: "repairing" });

    try {
      const result = await repairChart(chartType, repairInput);

      if (result.fixed && result.normalizedData) {
        const repairedJson = JSON.stringify(result.normalizedData, null, 2);
        console.info("[store] runRepair success changes=%d generated=%d", result.changes.length, result.generatedDataPoints.length);
        set({
          rawJson: repairedJson,
          parsedInput: result.normalizedData,
          parseError: null,
          validationStatus: "repaired",
          repairedData: result.normalizedData,
          repairChanges: result.changes,
          generatedDataPoints: result.generatedDataPoints,
          activeData: result.normalizedData,
          validationErrors: [],
        });
        return true;
      }

      console.warn("[store] runRepair failed error=%s", result.error);
      set({
        validationStatus: "repair-failed",
        validationErrors: [{ field: "root", message: result.error ?? "Repair failed." }],
      });
      return false;
    } catch (error) {
      const message = (error as { message?: string }).message ?? "Repair failed.";
      console.error("[store] runRepair error", error);
      set({
        validationStatus: "repair-failed",
        validationErrors: [{ field: "root", message }],
      });
      return false;
    }
  },

  setGeneratedCode(code) {
    console.info("[store] setGeneratedCode hasCode=%s", Boolean(code));
    set({ generatedCode: code });
  },

  setIsGeneratingCode(v) {
    console.info("[store] setIsGeneratingCode isGenerating=%s", v);
    set({ isGeneratingCode: v });
  },
}));
