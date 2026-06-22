import type { EChartsOption } from "echarts";

import type { ChartInput, Theme } from "../../types";
import { generateColors } from "../colorPalette";

export function buildLineConfig(data: ChartInput, theme: Theme): EChartsOption {
  const colors = generateColors(theme, data.datasets.length);

  return {
    tooltip: { trigger: "axis", confine: true, axisPointer: { snap: true } },
    legend: { data: data.datasets.map((ds) => ds.label) },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: { type: "category", data: data.labels, boundaryGap: false },
    yAxis: { type: "value" },
    series: data.datasets.map((ds, i) => ({
      name: ds.label,
      type: "line",
      data: ds.data,
      smooth: true,
      itemStyle: { color: colors[i] },
      lineStyle: { color: colors[i], width: 2 },
      animationDuration: 650,
    })),
  };
}
