import { useEffect, useMemo, useRef, useState } from 'react'
import ReactECharts from 'echarts-for-react'
import type { EChartsOption } from 'echarts'
import { Download } from 'lucide-react'

type ClinicalChartProps = {
  option: EChartsOption
  height?: number
  className?: string
  onEvents?: Record<string, (params: unknown) => void>
  exportTitle?: string
  exportTitleLayout?: 'bar' | 'donut'
}

export function ClinicalChart({
  option,
  height = 280,
  className,
  onEvents,
  exportTitle,
  exportTitleLayout = 'bar',
}: ClinicalChartProps) {
  const [isDark, setIsDark] = useState(() => document.documentElement.dataset.theme === 'dark')
  const chartRef = useRef<ReactECharts>(null)

  useEffect(() => {
    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.dataset.theme === 'dark')
    })
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
    return () => observer.disconnect()
  }, [])

  const exportBackground = isDark ? '#0e233a' : '#ffffff'
  const exportOption = useMemo<EChartsOption>(() => ({
    ...option,
    backgroundColor: exportBackground,
  }), [exportBackground, option])

  function downloadChart() {
    const chart = chartRef.current?.getEchartsInstance()
    if (!chart) return

    // ECharts otherwise includes the current axis-pointer selection in the PNG.
    chart.dispatchAction({ type: 'hideTip' })
    if (exportTitle) {
      const titleLayout: EChartsOption = exportTitleLayout === 'donut'
        ? { series: [{ center: ['50%', '48%'] }] }
        : { grid: { top: 52 } }
      chart.setOption({
        ...titleLayout,
        graphic: [{
          id: 'export-chart-title',
          type: 'text',
          left: 12,
          top: 10,
          style: { text: exportTitle, fill: isDark ? '#e8f5ff' : '#16324a', font: '600 16px sans-serif' },
        }],
      })
    }
    window.requestAnimationFrame(() => {
      const link = document.createElement('a')
      link.href = chart.getDataURL({
        type: 'png',
        pixelRatio: 2,
        backgroundColor: exportBackground,
        excludeComponents: ['toolbox'],
      })
      link.download = `${(exportTitle || 'lung-panel-chart').toLowerCase().replace(/[^a-z0-9]+/g, '-')}.png`
      link.click()
      if (exportTitle) {
        const restoreLayout: EChartsOption = exportTitleLayout === 'donut'
          ? { series: option.series }
          : { grid: option.grid }
        chart.setOption({
          ...restoreLayout,
          graphic: [{ id: 'export-chart-title', $action: 'remove' }],
        })
      }
    })
  }

  return (
    <div className="clinical-chart-export-wrap">
      <button
        type="button"
        className="clinical-chart-export-button"
        onClick={downloadChart}
        aria-label="Download chart as PNG"
        title="Download chart as PNG"
      >
        <Download size={15} />
      </button>
      <ReactECharts
        key={isDark ? 'dark' : 'light'}
        ref={chartRef}
        className={className}
        option={exportOption}
        onEvents={onEvents}
        theme={isDark ? 'dark' : undefined}
        style={{ height, width: '100%' }}
        notMerge
        lazyUpdate
      />
    </div>
  )
}
