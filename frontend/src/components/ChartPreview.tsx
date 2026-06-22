import { useEffect, useRef } from "react";
import * as echarts from "echarts/core";
import { BarChart, LineChart, PieChart, ScatterChart } from "echarts/charts";
import {
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

import { useStudioStore } from "../store/useStudioStore";
import { useChartConfig } from "../hooks/useChartConfig";

echarts.use([
  BarChart,
  LineChart,
  PieChart,
  ScatterChart,
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
  CanvasRenderer,
]);

export function ChartPreview(): JSX.Element {
  const rootRef = useRef<HTMLDivElement | null>(null);
  const activeData = useStudioStore((s) => s.activeData);
  const chartType = useStudioStore((s) => s.chartType);
  const theme = useStudioStore((s) => s.theme);

  const option = useChartConfig(activeData, chartType, theme);

  useEffect(() => {
    if (!rootRef.current || !option) return;

    const chart = echarts.init(rootRef.current);
    chart.setOption(option);

    const onResize = () => chart.resize();
    window.addEventListener("resize", onResize);

    return () => {
      window.removeEventListener("resize", onResize);
      chart.dispose();
    };
  }, [option]);

  return (
    <section className="panel">
      <header className="panel-header">ECharts Preview</header>
      {!option ? <div className="empty">Validated chart data will render here.</div> : <div ref={rootRef} className="chart" />}
    </section>
  );
}
