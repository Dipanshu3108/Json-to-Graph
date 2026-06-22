import type { EChartsOption } from "echarts";

import type { ChartInput, Theme } from "../../types";
import { generateColors } from "../colorPalette";

export function buildPieConfig(data: ChartInput, theme: Theme, isDoughnut = false): EChartsOption {
  const dataset = data.datasets[0];
  const colors = generateColors(theme, data.labels.length);

  const seriesData = data.labels.map((label, i) => ({
    name: label,
    value: dataset.data[i],
    itemStyle: { color: colors[i] },
  }));

  return {
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    legend: { orient: "vertical", left: "left", data: data.labels },
    series: [
      {
        type: "pie",
        radius: isDoughnut ? ["40%", "70%"] : "60%",
        center: ["55%", "50%"],
        data: seriesData,
        emphasis: {
          itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: "rgba(0,0,0,0.3)" },
        },
        animationDuration: 650,
      },
    ],
  };
}
