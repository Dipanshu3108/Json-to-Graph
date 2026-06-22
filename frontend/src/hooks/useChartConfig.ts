import { useMemo } from "react";
import type { EChartsOption } from "echarts";

import type { AnyChartInput, ChartInput, ChartType, ScatterInput, Theme } from "../types";
import { buildAreaConfig } from "../utils/chartConfigBuilders/area";
import { buildBarConfig } from "../utils/chartConfigBuilders/bar";
import { buildDoughnutConfig } from "../utils/chartConfigBuilders/doughnut";
import { buildLineConfig } from "../utils/chartConfigBuilders/line";
import { buildPieConfig } from "../utils/chartConfigBuilders/pie";
import { buildScatterConfig } from "../utils/chartConfigBuilders/scatter";

export function useChartConfig(
  data: AnyChartInput | null,
  chartType: ChartType,
  theme: Theme
): EChartsOption | null {
  return useMemo(() => {
    if (!data) return null;

    switch (chartType) {
      case "bar":
        return buildBarConfig(data as ChartInput, theme);
      case "line":
        return buildLineConfig(data as ChartInput, theme);
      case "area":
        return buildAreaConfig(data as ChartInput, theme);
      case "pie":
        return buildPieConfig(data as ChartInput, theme, false);
      case "doughnut":
        return buildDoughnutConfig(data as ChartInput, theme);
      case "scatter":
        return buildScatterConfig(data as ScatterInput, theme);
      default:
        return null;
    }
  }, [data, chartType, theme]);
}
