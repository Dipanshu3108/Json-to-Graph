import type {
  ApiError,
  ChartType,
  GenerateCodeResponse,
  JsonObject,
  JsonPayload,
  RepairResponse,
  ValidateResponse,
} from "../types";

const BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function post<T>(path: string, body: unknown): Promise<T> {
  console.info(`[api] POST ${path} start`, body);
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json().catch(
      () =>
        ({
          status: res.status,
          code: "UNKNOWN",
          message: res.statusText,
        }) as ApiError
    );
    console.error(`[api] POST ${path} error`, err);
    throw err;
  }

  const data = (await res.json()) as T;
  console.info(`[api] POST ${path} success`, data);
  return data;
}

export const validateChart = (chartType: ChartType, data: JsonObject): Promise<ValidateResponse> =>
  post("/api/validate", { chartType, data });

export const repairChart = (chartType: ChartType, data: JsonPayload): Promise<RepairResponse> =>
  post("/api/repair", { chartType, data });

export const generateCode = (
  chartType: string,
  data: JsonPayload,
  theme: string
): Promise<GenerateCodeResponse> => post("/api/generate-code", { chartType, data, theme });
