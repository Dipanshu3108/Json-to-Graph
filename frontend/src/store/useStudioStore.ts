import { create } from "zustand";

import { repairChart, validateChart } from "../services/api";
import type { AnyChartInput, ChartType, JsonPayload, RenderMode, StudioState, Theme } from "../types";

interface StudioActions {
  setRawJson: (json: string) => void;
  setChartType: (type: ChartType) => void;
  setTheme: (theme: Theme) => void;
  setRenderMode: (mode: RenderMode) => void;
  runValidation: () => Promise<void>;
  runRepair: () => Promise<void>;
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

    set({
      rawJson: json,
      parsedInput,
      parseError,
      validationStatus: "idle",
      validationErrors: [],
      activeData: null,
      repairedData: null,
      repairChanges: [],
      generatedCode: null,
    });
  },

  setChartType(chartType) {
    set({ chartType, validationStatus: "idle", activeData: null, generatedCode: null });
  },

  setTheme(theme) {
    set({ theme });
  },

  setRenderMode(renderMode) {
    set({ renderMode });
  },

  async runValidation() {
    const { parsedInput, parseError, chartType } = get();
    if (parseError || !parsedInput) return;

    if (typeof parsedInput !== "object" || parsedInput === null || Array.isArray(parsedInput)) {
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
      return;
    }

    const validationInput = parsedInput as Record<string, unknown>;

    set({ validationStatus: "validating" });

    try {
      const result = await validateChart(chartType, validationInput);

      if (result.valid) {
        set({
          validationStatus: "valid",
          validationErrors: [],
          activeData: result.normalizedData ?? null,
        });
      } else {
        set({
          validationStatus: "invalid",
          validationErrors: result.errors,
          activeData: null,
        });
      }
    } catch (error) {
      const message = (error as { message?: string }).message ?? "Validation failed.";
      set({
        validationStatus: "invalid",
        validationErrors: [{ field: "root", message }],
        activeData: null,
      });
    }
  },

  async runRepair() {
    const { parsedInput, rawJson, chartType } = get();
    const repairInput = parsedInput ?? rawJson.trim();
    if (!repairInput) return;

    set({ validationStatus: "repairing" });

    try {
      const result = await repairChart(chartType, repairInput);

      if (result.fixed && result.normalizedData) {
        const repairedJson = JSON.stringify(result.normalizedData, null, 2);
        set({
          rawJson: repairedJson,
          parsedInput: result.normalizedData,
          parseError: null,
          validationStatus: "repaired",
          repairedData: result.normalizedData,
          repairChanges: result.changes,
          activeData: result.normalizedData,
          validationErrors: [],
        });
      } else {
        set({
          validationStatus: "repair-failed",
          validationErrors: [{ field: "root", message: result.error ?? "Repair failed." }],
        });
      }
    } catch (error) {
      const message = (error as { message?: string }).message ?? "Repair failed.";
      set({
        validationStatus: "repair-failed",
        validationErrors: [{ field: "root", message }],
      });
    }
  },

  setGeneratedCode(code) {
    set({ generatedCode: code });
  },

  setIsGeneratingCode(v) {
    set({ isGeneratingCode: v });
  },
}));
