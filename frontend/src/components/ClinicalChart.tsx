import { useEffect, useMemo, useRef, useState } from 'react'
import ReactECharts from 'echarts-for-react'
import type { EChartsOption } from 'echarts'
import { Download } from 'lucide-react'

type ClinicalChartProps = {
  option: EChartsOption
  height?: number
  className?: string
}

export function ClinicalChart({
  option,
  height = 280,
  className,
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
    window.requestAnimationFrame(() => {
      const link = document.createElement('a')
      link.href = chart.getDataURL({
        type: 'png',
        pixelRatio: 2,
        backgroundColor: exportBackground,
        excludeComponents: ['toolbox'],
      })
      link.download = 'lung-panel-chart.png'
      link.click()
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
        theme={isDark ? 'dark' : undefined}
        style={{ height, width: '100%' }}
        notMerge
        lazyUpdate
      />
    </div>
  )
}
