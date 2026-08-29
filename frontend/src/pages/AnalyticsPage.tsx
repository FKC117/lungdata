import { useQuery } from '@tanstack/react-query'
import { useMemo, useState, type ReactNode } from 'react'
import { BarChart3, Download, FileDown, Filter, ShieldCheck } from 'lucide-react'
import type { EChartsOption } from 'echarts'
import {
  buildAnalyticsExportUrl,
  fetchAnalyticsDistributions,
  fetchAnalyticsFacet,
  fetchAnalyticsFilters,
  fetchAnalyticsSummary,
  fetchAnalyticsSurvival,
} from '../api'
import { ClinicalChart } from '../components/ClinicalChart'
import { LoadingState } from '../components/registry-ui'

type Filters = Record<string, string>
type ChartType = 'bar' | 'donut' | 'table'
type DistributionItem = { label: string; count: number }
const clinicalPalette = ['#0f766e', '#168aa2', '#3f74ad', '#5e6f91', '#7c6a9f', '#4f8b72', '#a77a45', '#b25b70', '#8b9650', '#4b8891', '#7288a9', '#8b7697']
const initialFilters: Filters = { start_date: '', end_date: '', center: '', doctor: '', diagnosis: '', stage: '', biomarker: '', treatment: '', outcome: '' }
const labels: Record<string, string> = { total_patients: 'Total patients', new_diagnoses: 'Recorded diagnoses', active_treatment: 'Active treatment', recorded_response: 'Recorded response', response_rate: 'Response rate', pfs_available: 'PFS available', os_available: 'OS available' }

function downloadDistributionCsv(title: string, items: DistributionItem[], total: number) {
  const rows = [['Category', 'Patients', 'Share'], ...items.map((item) => [item.label, String(item.count), total ? `${(item.count / total * 100).toFixed(1)}%` : ''])]
  const csv = rows.map((row) => row.map((value) => `"${value.replace(/"/g, '""')}"`).join(',')).join('\n')
  const link = document.createElement('a')
  link.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }))
  link.download = `${title.toLowerCase().replace(/[^a-z0-9]+/g, '-')}.csv`
  link.click()
  URL.revokeObjectURL(link.href)
}

function DistributionChart({
  title,
  items,
  defaultChartType = 'bar',
  horizontal = false,
  defaultTopN = 0,
  supportsMissing = true,
  facetFilters,
}: {
  title: string
  items: DistributionItem[]
  defaultChartType?: ChartType
  horizontal?: boolean
  defaultTopN?: number
  supportsMissing?: boolean
  facetFilters?: ReactNode
}) {
  const [chartType, setChartType] = useState<ChartType>(defaultChartType)
  const [includeMissing, setIncludeMissing] = useState(false)
  const [topN, setTopN] = useState(defaultTopN)
  const usableItems = useMemo(
    () => items.filter((item) => includeMissing || item.label !== 'Not recorded'),
    [includeMissing, items],
  )
  const displayItems = useMemo(() => {
    if (!topN || usableItems.length <= topN) return usableItems
    const topItems = usableItems.slice(0, topN)
    const otherCount = usableItems.slice(topN).reduce((total, item) => total + item.count, 0)
    return otherCount ? [...topItems, { label: 'Other', count: otherCount }] : topItems
  }, [topN, usableItems])
  const total = displayItems.reduce((sum, item) => sum + item.count, 0)
  const labels = displayItems.map((item) => item.label)
  const values = displayItems.map((item) => item.count)
  const option: EChartsOption = chartType === 'donut'
    ? {
      color: clinicalPalette,
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { type: 'scroll', bottom: 0, textStyle: { fontSize: 10 } },
      series: [{
        type: 'pie',
        radius: ['42%', '70%'],
        center: ['50%', '42%'],
        label: { show: true, formatter: '{b}: {c}', fontSize: 10, overflow: 'truncate', width: 86 },
        labelLine: { length: 9, length2: 8 },
        labelLayout: { hideOverlap: true },
        data: displayItems.map((item) => ({ name: item.label, value: item.count })),
        itemStyle: { borderRadius: 4, borderColor: 'transparent', borderWidth: 2 },
      }],
    }
    : horizontal
      ? {
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: 118, right: 22, top: 16, bottom: 18 },
        xAxis: { type: 'value', minInterval: 1 },
        yAxis: { type: 'category', data: labels, inverse: true, axisLabel: { fontSize: 10, width: 102, overflow: 'truncate' } },
        series: [{ type: 'bar', data: values, label: { show: true, position: 'right', fontSize: 10 }, itemStyle: { color: '#0f766e', borderRadius: [0, 6, 6, 0] } }],
      }
      : {
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: 42, right: 20, top: 18, bottom: 70 },
        xAxis: { type: 'category', data: labels, axisLabel: { rotate: 35, fontSize: 10, interval: 0 } },
        yAxis: { type: 'value', minInterval: 1 },
        series: [{ type: 'bar', data: values, label: { show: true, position: 'top', fontSize: 10 }, itemStyle: { color: '#0f766e', borderRadius: [6, 6, 0, 0] } }],
      }

  return (
    <article className="panel analytics-chart">
      <div className="panel-heading analytics-chart-heading">
        <h3>{title}</h3>
        <div className="analytics-chart-controls">
          {facetFilters}
          <label>Chart
            <select value={chartType} onChange={(event) => setChartType(event.target.value as ChartType)}>
              <option value="bar">Bar</option>
              <option value="donut">Donut</option>
              <option value="table">Table</option>
            </select>
          </label>
          {items.length > 10 ? <label>Categories
            <select value={topN} onChange={(event) => setTopN(Number(event.target.value))}>
              <option value={0}>All</option>
              <option value={5}>Top 5</option>
              <option value={10}>Top 10</option>
            </select>
          </label> : null}
        </div>
      </div>
      {supportsMissing ? <label className="analytics-missing-toggle">
        <input type="checkbox" checked={includeMissing} onChange={(event) => setIncludeMissing(event.target.checked)} />
        Include not recorded
      </label> : null}
      {chartType === 'table' ? (
        <div className="analytics-distribution-table">
          <button className="analytics-table-download" type="button" onClick={() => downloadDistributionCsv(title, displayItems, total)}><FileDown size={14} /> Download CSV</button>
          <table className="registry-table"><thead><tr><th>Category</th><th>Patients</th><th>Share</th></tr></thead>
            <tbody>{displayItems.map((item) => <tr key={item.label}><td>{item.label}</td><td>{item.count}</td><td>{total ? `${(item.count / total * 100).toFixed(1)}%` : '—'}</td></tr>)}</tbody>
          </table>
        </div>
      ) : <ClinicalChart height={230} option={option} exportTitle={title} exportTitleLayout={chartType === 'donut' ? 'donut' : 'bar'} />}
    </article>
  )
}

function FacetedChart({ title, subject, filters, horizontal = false, defaultChartType = 'bar' }: {
  title: string
  subject: string
  filters: Filters
  horizontal?: boolean
  defaultChartType?: ChartType
}) {
  const [localFilters, setLocalFilters] = useState<Filters>({})
  const queryFilters = { ...filters, ...localFilters }
  const facetQuery = useQuery({ queryKey: ['analytics-facet', subject, queryFilters], queryFn: () => fetchAnalyticsFacet(subject, queryFilters) })
  const facetFilters = <div className="analytics-facet-filters">{Object.entries(facetQuery.data?.filters ?? {}).map(([key, values]) => <label key={key}>{key.replace('_', ' ')}<select value={localFilters[key] ?? ''} onChange={event => setLocalFilters(current => ({ ...current, [key]: event.target.value }))}><option value="">All</option>{values.map(value => <option key={value} value={value}>{value}</option>)}</select></label>)}</div>
  return <div className="analytics-faceted-chart">{facetQuery.isLoading ? <LoadingState label="Loading chart" /> : <DistributionChart title={title} items={facetQuery.data?.items ?? []} horizontal={horizontal} defaultChartType={defaultChartType} defaultTopN={horizontal ? 10 : 0} supportsMissing={false} facetFilters={facetFilters} />}</div>
}

export default function AnalyticsPage() {
  const [filters, setFilters] = useState<Filters>(initialFilters)
  const filterQuery = useQuery({ queryKey: ['analytics-filters'], queryFn: () => fetchAnalyticsFilters() })
  const summaryQuery = useQuery({ queryKey: ['analytics-summary', filters], queryFn: () => fetchAnalyticsSummary(filters) })
  const distributionQuery = useQuery({ queryKey: ['analytics-distributions', filters], queryFn: () => fetchAnalyticsDistributions(filters) })
  const survivalQuery = useQuery({ queryKey: ['analytics-survival', filters], queryFn: () => fetchAnalyticsSurvival(filters) })
  const filterOptions = filterQuery.data
  const kpis = summaryQuery.data?.kpis ?? {}
  const survival = survivalQuery.data?.survival ?? []
  const completeness = useMemo(() => distributionQuery.data?.completeness ?? [], [distributionQuery.data])
  const change = (key: string, value: string) => setFilters(current => ({ ...current, [key]: value }))
  const select = (key: string, items: Array<{ value: string; label: string }>) => <label className="analytics-filter">{key.replace('_', ' ')}<select value={filters[key]} onChange={e => change(key, e.target.value)}><option value="">All</option>{items.map(item => <option key={item.value} value={item.value}>{item.label}</option>)}</select></label>

  return <section className="page-grid">
    <section className="hero-panel analytics-hero"><div className="hero-copy"><p className="eyebrow">Read-only analytics</p><h2>Clinical outcomes workspace</h2><p className="hero-text">Published clinical records only. Filters define one patient cohort; blank fields remain missing.</p></div><a className="secondary-button" href={buildAnalyticsExportUrl(filters)}><Download size={16} /> Export safe CSV</a></section>
    <section className="panel analytics-filters"><div className="panel-heading"><div><p className="eyebrow">Cohort filters</p><h3><Filter size={17} /> Global selection</h3></div><button className="secondary-button" type="button" onClick={() => setFilters(initialFilters)}>Clear filters</button></div><div className="analytics-filter-grid">
      <label className="analytics-filter">From<input type="date" value={filters.start_date} onChange={e => change('start_date', e.target.value)} /></label>
      <label className="analytics-filter">To<input type="date" value={filters.end_date} onChange={e => change('end_date', e.target.value)} /></label>
      {select('center', (filterOptions?.centers ?? []).map(x => ({ value: String(x.center_id), label: x.center__name })))}
      {select('doctor', (filterOptions?.doctors ?? []).map(x => ({ value: String(x.doctor_id), label: x.doctor__name })))}
      {select('diagnosis', (filterOptions?.diagnoses ?? []).map(x => ({ value: x, label: x })))}
      {select('stage', (filterOptions?.stages ?? []).map(x => ({ value: x, label: x })))}
      {select('biomarker', (filterOptions?.biomarkers ?? []).map(x => ({ value: x, label: x })))}
      {select('treatment', (filterOptions?.treatments ?? []).map(x => ({ value: x, label: x })))}
      {select('outcome', [{ value: 'progressed', label: 'Progressed' }, { value: 'deceased', label: 'Deceased' }])}
    </div></section>
    {summaryQuery.isLoading ? <LoadingState label="Calculating cohort metrics" /> : <section className="analytics-kpis">{Object.entries(kpis).map(([key, value]) => <article className="metric-card" key={key}><span>{labels[key]}</span><strong>{key === 'response_rate' && value !== null ? `${value}%` : value ?? '—'}</strong></article>)}</section>}
    {distributionQuery.isLoading ? <LoadingState label="Loading distributions" /> : <>
      <section className="analytics-chart-section"><h3>Cohort overview</h3><div className="analytics-chart-grid"><DistributionChart title="Stage distribution" items={distributionQuery.data?.stage ?? []} /><DistributionChart title="Tumor grade" items={distributionQuery.data?.grade ?? []} defaultChartType="donut" /><DistributionChart title="Recorded responses" items={distributionQuery.data?.response ?? []} defaultChartType="donut" /></div></section>
      <section className="analytics-chart-section"><h3>Clinical drill-downs</h3><div className="analytics-chart-grid"><FacetedChart title="Histopathology diagnosis" subject="histopathology" filters={filters} horizontal /><FacetedChart title="Molecular test result" subject="molecular" filters={filters} defaultChartType="donut" /><FacetedChart title="Treatment protocol" subject="treatment" filters={filters} horizontal /><FacetedChart title="Radiotherapy intent" subject="radiotherapy" filters={filters} defaultChartType="donut" /><FacetedChart title="Surgery modality" subject="surgery" filters={filters} horizontal /></div></section>
    </>}
    <section className="insight-grid"><article className="panel"><div className="panel-heading"><div><p className="eyebrow">Survival summary</p><h3><BarChart3 size={17} /> PFS and OS</h3></div></div>{survivalQuery.isLoading ? <LoadingState label="Calculating survival summary" /> : <div className="analytics-table-wrap"><table className="registry-table"><thead><tr><th>Metric</th><th>Available</th><th>Median days</th></tr></thead><tbody>{survival.map(item => <tr key={item.metric}><td>{item.metric.toUpperCase()}</td><td>{item.available}</td><td>{item.median_days ?? '—'}</td></tr>)}</tbody></table></div>}</article><article className="panel"><div className="panel-heading"><div><p className="eyebrow">Data quality</p><h3>Completeness</h3></div></div><div className="analytics-completeness">{completeness.map(item => <div key={item.label}><span>{item.label}</span><strong>{item.count}/{item.total}</strong><div><i style={{ width: `${item.total ? item.count / item.total * 100 : 0}%` }} /></div></div>)}</div></article></section>
    <section className="panel analytics-definitions"><p className="eyebrow"><ShieldCheck size={16} /> Calculation definitions</p>{Object.entries(summaryQuery.data?.definitions ?? {}).map(([key, value]) => <p key={key}><strong>{key.replace('_', ' ')}:</strong> {value}</p>)}</section>
  </section>
}
