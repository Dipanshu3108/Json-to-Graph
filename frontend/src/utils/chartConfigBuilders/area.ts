import type { EChartsOption } from "echarts";

import type { ChartInput, Theme } from "../../types";
import { generateColors, generateFillColors } from "../colorPalette";

export function buildAreaConfig(data: ChartInput, theme: Theme): EChartsOption {
  const colors = generateColors(theme, data.datasets.length);
  const fills = generateFillColors(theme, data.datasets.length, 0.25);

  return {
    tooltip: { trigger: "axis", confine: true, axisPointer: { snap: true } },
    legend: { data: data.datasets.map((ds) => ds.label) },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: { type: "category", data: data.labels, boundaryGap: false },
    yAxis: { type: "value" },
    series: data.datasets.map((ds, i) => ({
      name: ds.label,
      type: "line",
      smooth: true,
      data: ds.data,
      itemStyle: { color: colors[i] },
      lineStyle: { color: colors[i] },
      areaStyle: { color: fills[i] },
      animationDuration: 650,
    })),
  };
}
