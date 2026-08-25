import { useEffect, useState } from 'react'
import ReactECharts from 'echarts-for-react'
import type { EChartsOption } from 'echarts'

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
  const [theme, setTheme] = useState(() => document.documentElement.dataset.theme === 'dark' ? 'dark' : undefined)

  useEffect(() => {
    const observer = new MutationObserver(() => {
      setTheme(document.documentElement.dataset.theme === 'dark' ? 'dark' : undefined)
    })
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
    return () => observer.disconnect()
  }, [])

  return (
    <ReactECharts
      className={className}
      option={option}
      theme={theme}
      style={{ height, width: '100%' }}
      notMerge
      lazyUpdate
    />
  )
}
