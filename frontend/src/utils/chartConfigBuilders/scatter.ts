import type { EChartsOption } from "echarts";

import type { ScatterInput, Theme } from "../../types";
import { generateColors } from "../colorPalette";

export function buildScatterConfig(data: ScatterInput, theme: Theme): EChartsOption {
  const colors = generateColors(theme, data.datasets.length);

  return {
    tooltip: {
      trigger: "item",
      confine: true,
      formatter: (params: any) => {
        const point = params?.data as [number, number] | undefined;
        if (!point) return "";
        return `(${point[0]}, ${point[1]})`;
      },
    },
    legend: { data: data.datasets.map((ds) => ds.label) },
    xAxis: { type: "value", scale: true },
    yAxis: { type: "value", scale: true },
    series: data.datasets.map((ds, i) => ({
      name: ds.label,
      type: "scatter",
      data: ds.data.map((pt) => [pt.x, pt.y]),
      itemStyle: { color: colors[i] },
      symbolSize: 10,
      animationDuration: 650,
    })),
  };
}
