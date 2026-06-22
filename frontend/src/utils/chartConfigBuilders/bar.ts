import type { EChartsOption } from "echarts";

import type { ChartInput, Theme } from "../../types";
import { generateColors } from "../colorPalette";

export function buildBarConfig(data: ChartInput, theme: Theme): EChartsOption {
  const colors = generateColors(theme, data.datasets.length);

  return {
    tooltip: { trigger: "item", confine: true },
    legend: { data: data.datasets.map((ds) => ds.label) },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: { type: "category", data: data.labels },
    yAxis: { type: "value" },
    series: data.datasets.map((ds, i) => ({
      name: ds.label,
      type: "bar",
      data: ds.data,
      itemStyle: { color: colors[i] },
      animationDuration: 650,
    })),
  };
}
