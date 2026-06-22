import type { EChartsOption } from "echarts";

import type { ChartInput, Theme } from "../../types";
import { buildPieConfig } from "./pie";

export function buildDoughnutConfig(data: ChartInput, theme: Theme): EChartsOption {
  return buildPieConfig(data, theme, true);
}
