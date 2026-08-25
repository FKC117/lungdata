import { Fragment, useDeferredValue, useEffect, useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Activity,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronsUpDown,
  ChevronUp,
  Microscope,
  Search,
  Stethoscope,
  Waves,
} from 'lucide-react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import {
  buildPatientExportUrl,
  fetchDashboardSummary,
  fetchPatients,
  type DashboardSummary,
} from '../api'
import { EmptyState, LoadingState } from '../components/registry-ui'
import { ClinicalChart } from '../components/ClinicalChart'
import { metricPalette } from '../lib/registry'

function DashboardSection({
  summary,
  isLoading,
}: {
  summary?: DashboardSummary
  isLoading: boolean
}) {
  const metrics = [
    {
      label: 'Patients',
      value: summary?.patients ?? 0,
      description: 'Canonical patient records',
      icon: Stethoscope,
    },
    {
      label: 'Observations',
      value: summary?.observations ?? 0,
      description: 'Clinical observation records',
      icon: Activity,
    },
    {
      label: 'Published Patients',
      value: summary?.published_patients ?? 0,
      description: `${summary?.published_observations ?? 0} published observations`,
      icon: Microscope,
    },
    {
      label: 'Draft Patients',
      value: summary?.draft_patients ?? 0,
      description: `${summary?.draft_observations ?? 0} draft observations`,
      icon: Waves,
    },
  ]

  return (
    <section className="metric-grid">
      {metrics.map((metric, index) => {
        const Icon = metric.icon
        return (
          <article key={metric.label} className="metric-card">
            <div
              className="metric-icon"
              style={{
                backgroundColor: `${metricPalette[index]}14`,
                color: metricPalette[index],
              }}
            >
              <Icon size={18} />
            </div>
            <p className="metric-label">{metric.label}</p>
            <p className="metric-value">
              {isLoading ? '...' : metric.value.toLocaleString()}
            </p>
            <p className="metric-description">{metric.description}</p>
          </article>
        )
      })}
    </section>
  )
}

export default function PatientSearchPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [draftQuery, setDraftQuery] = useState(searchParams.get('q') ?? '')
  const [expandedRegistryId, setExpandedRegistryId] = useState<string | null>(null)
  const deferredQuery = useDeferredValue(draftQuery.trim())
  const page = Math.max(1, Number(searchParams.get('page') ?? '1') || 1)
  const stateFilter = searchParams.get('state') ?? 'all'
  const sortKey = searchParams.get('sort') ?? 'name'
  const sortDirection = searchParams.get('dir') ?? 'asc'
  const navigate = useNavigate()

  const summaryQuery = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: fetchDashboardSummary,
  })

  const patientsQuery = useQuery({
    queryKey: ['patients', deferredQuery, page, stateFilter, sortKey, sortDirection],
    queryFn: () =>
      fetchPatients(
        deferredQuery,
        page,
        24,
        stateFilter,
        sortKey,
        sortDirection,
      ),
  })

  useEffect(() => {
    const next = new URLSearchParams(searchParams)
    const currentQuery = next.get('q') ?? ''
    if (currentQuery !== deferredQuery) {
      if (deferredQuery) {
        next.set('q', deferredQuery)
      } else {
        next.delete('q')
      }
      next.set('page', '1')
      setSearchParams(next, { replace: true })
    }
  }, [deferredQuery, searchParams, setSearchParams])

  const patients = patientsQuery.data?.results ?? []
  const observationChartData = useMemo(
    () =>
      patients.slice(0, 8).map((patient) => ({
        name: patient.name || patient.registry_id,
        observations: patient.observation_count,
      })),
    [patients],
  )

  const publicationData = useMemo(() => {
    const summary = summaryQuery.data
    if (!summary) {
      return []
    }

    return [
      { name: 'Published Patients', value: summary.published_patients, fill: '#0f766e' },
      { name: 'Draft Patients', value: summary.draft_patients, fill: '#fb923c' },
    ]
  }, [summaryQuery.data])

  const totalCount = patientsQuery.data?.count ?? 0
  const hasNextPage = Boolean(patientsQuery.data?.next)
  const hasPreviousPage = Boolean(patientsQuery.data?.previous)
  const pageSize = 24
  const startItem = totalCount === 0 ? 0 : (page - 1) * pageSize + 1
  const endItem = Math.min(page * pageSize, totalCount)

  function handleSearchSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const next = new URLSearchParams(searchParams)
    if (draftQuery.trim()) {
      next.set('q', draftQuery.trim())
    } else {
      next.delete('q')
    }
    next.set('page', '1')
    setSearchParams(next)
  }

  function handleStateChange(nextState: string) {
    const next = new URLSearchParams(searchParams)
    if (nextState === 'all') {
      next.delete('state')
    } else {
      next.set('state', nextState)
    }
    next.set('page', '1')
    setSearchParams(next)
  }

  function goToPage(nextPage: number) {
    const next = new URLSearchParams(searchParams)
    next.set('page', String(nextPage))
    if (draftQuery.trim()) {
      next.set('q', draftQuery.trim())
    }
    setSearchParams(next)
  }

  function handleSort(nextSortKey: string) {
    const next = new URLSearchParams(searchParams)
    const nextDirection =
      sortKey === nextSortKey && sortDirection === 'asc' ? 'desc' : 'asc'
    next.set('sort', nextSortKey)
    next.set('dir', nextDirection)
    next.set('page', '1')
    setSearchParams(next, { replace: true })
  }

  function toggleExpandedRow(registryId: string) {
    setExpandedRegistryId((current) =>
      current === registryId ? null : registryId,
    )
  }

  function renderSortIcon(columnKey: string) {
    if (sortKey !== columnKey) {
      return <ChevronsUpDown size={14} />
    }
    return sortDirection === 'asc' ? <ChevronUp size={14} /> : <ChevronDown size={14} />
  }

  return (
    <section className="page-grid">
      <section className="hero-panel">
        <div className="hero-copy">
          <p className="eyebrow">Patient Search and Analytics</p>
          <h2>Search by patient ID, registration number, or phone.</h2>
          <p className="hero-text">
            Canonical Django-backed registry search with observation-state filtering.
          </p>
        </div>
        <form className="search-panel" onSubmit={handleSearchSubmit}>
          <label className="search-label" htmlFor="patient-search">
            Patient lookup
          </label>
          <div className="search-row">
            <Search className="search-icon" size={18} />
            <input
              id="patient-search"
              className="search-input"
              value={draftQuery}
              onChange={(event) => setDraftQuery(event.target.value)}
              placeholder="Try 01754423423, REG-000000001, or a patient name"
            />
            <button className="primary-button" type="submit">
              Search
            </button>
          </div>
          <div className="inline-filter-row">
            <label className="inline-filter-label" htmlFor="state-filter">
              Observation state
            </label>
            <select
              id="state-filter"
              className="inline-filter-select"
              value={stateFilter}
              onChange={(event) => handleStateChange(event.target.value)}
            >
              <option value="all">All patients</option>
              <option value="published">Published observations</option>
              <option value="draft">Draft observations</option>
            </select>
          </div>
        </form>
      </section>

      <DashboardSection
        summary={summaryQuery.data}
        isLoading={summaryQuery.isLoading}
      />

      <section className="insight-grid">
        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Registry Balance</p>
              <h3>Patients by publication state</h3>
            </div>
            <Activity className="panel-icon" />
          </div>
          <div className="chart-box">
            {summaryQuery.isLoading ? (
              <LoadingState label="Loading summary" />
            ) : (
              <ClinicalChart
                height={260}
                option={{
                  tooltip: { trigger: 'item', valueFormatter: (value) => String(value) },
                  legend: { bottom: 0 },
                  series: [{
                    type: 'pie',
                    radius: ['48%', '72%'],
                    padAngle: 4,
                    itemStyle: { borderRadius: 8, borderColor: 'transparent', borderWidth: 3 },
                    label: { show: false },
                    data: publicationData.map(({ name, value, fill }) => ({ name, value, itemStyle: { color: fill } })),
                  }],
                }}
              />
            )}
          </div>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Result Snapshot</p>
              <h3>Observation volume in current page</h3>
            </div>
            <Waves className="panel-icon" />
          </div>
          <div className="chart-box">
            {patientsQuery.isLoading ? (
              <LoadingState label="Loading patients" />
            ) : observationChartData.length ? (
              <ClinicalChart
                height={260}
                option={{
                  tooltip: { trigger: 'axis' },
                  grid: { left: 42, right: 14, top: 18, bottom: 74 },
                  xAxis: { type: 'category', data: observationChartData.map((entry) => entry.name), axisLabel: { rotate: 18, fontSize: 11, interval: 0 } },
                  yAxis: { type: 'value', minInterval: 1 },
                  series: [{
                    type: 'bar',
                    data: observationChartData.map((entry, index) => ({ value: entry.observations, itemStyle: { color: metricPalette[index % metricPalette.length], borderRadius: [8, 8, 0, 0] } })),
                  }],
                }}
              />
            ) : (
              <EmptyState
                title="No matching patients"
                detail="Adjust the search and the chart will update with the current result set."
              />
            )}
          </div>
        </article>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Patient Registry</p>
            <h3>Search results</h3>
          </div>
          <div className="panel-actions">
            <a
              className="secondary-button"
              href={buildPatientExportUrl(
                deferredQuery,
                stateFilter,
                sortKey,
                sortDirection,
              )}
            >
              Export CSV
            </a>
            <span className="result-chip">
              {startItem}-{endItem} of {totalCount}
            </span>
          </div>
        </div>
        {patientsQuery.isLoading ? (
          <LoadingState label="Loading patient list" />
        ) : patients.length ? (
          <>
            <div className="registry-table-wrap">
              <table className="registry-table">
                <thead>
                  <tr>
                    <th>
                      <button type="button" className="sort-button" onClick={() => handleSort('name')}>
                        Patient
                        {renderSortIcon('name')}
                      </button>
                    </th>
                    <th>
                      <button type="button" className="sort-button" onClick={() => handleSort('registry_id')}>
                        Registry ID
                        {renderSortIcon('registry_id')}
                      </button>
                    </th>
                    <th>
                      <button type="button" className="sort-button" onClick={() => handleSort('phone')}>
                        Phone
                        {renderSortIcon('phone')}
                      </button>
                    </th>
                    <th>
                      <button type="button" className="sort-button" onClick={() => handleSort('age')}>
                        Age
                        {renderSortIcon('age')}
                      </button>
                    </th>
                    <th>
                      <button type="button" className="sort-button" onClick={() => handleSort('gender')}>
                        Gender
                        {renderSortIcon('gender')}
                      </button>
                    </th>
                    <th>
                      <button type="button" className="sort-button" onClick={() => handleSort('district')}>
                        District
                        {renderSortIcon('district')}
                      </button>
                    </th>
                    <th>
                      <button type="button" className="sort-button" onClick={() => handleSort('observations')}>
                        Observations
                        {renderSortIcon('observations')}
                      </button>
                    </th>
                    <th>
                      <button type="button" className="sort-button" onClick={() => handleSort('state')}>
                        Latest State
                        {renderSortIcon('state')}
                      </button>
                    </th>
                    <th>
                      <button type="button" className="sort-button" onClick={() => handleSort('disease_group')}>
                        Latest Disease Group
                        {renderSortIcon('disease_group')}
                      </button>
                    </th>
                    <th aria-label="Open"></th>
                  </tr>
                </thead>
                <tbody>
                  {patients.map((patient) => (
                    <Fragment key={patient.registry_id}>
                      <tr
                        className="registry-row"
                        onClick={() => navigate(`/patients/${patient.registry_id}`)}
                      >
                        <td>
                          <div className="table-patient">
                            <strong>{patient.name || 'Unnamed patient'}</strong>
                            <span>
                              {patient.legacy_unique_id || 'No legacy business ID'}
                            </span>
                          </div>
                        </td>
                        <td>{patient.registry_id}</td>
                        <td>{patient.phone || 'N/A'}</td>
                        <td>{patient.age ?? 'N/A'}</td>
                        <td>{patient.gender || 'N/A'}</td>
                        <td>{patient.district || 'N/A'}</td>
                        <td>{patient.observation_count}</td>
                        <td>
                          {patient.latest_observation ? (
                            <span
                              className={
                                patient.latest_observation.is_draft
                                  ? 'status-pill status-draft'
                                  : 'status-pill status-live'
                              }
                            >
                              {patient.latest_observation.is_draft ? 'Draft' : 'Published'}
                            </span>
                          ) : (
                            <span className="status-pill status-empty">No observation</span>
                          )}
                        </td>
                        <td>
                          {patient.latest_observation?.diagnosis_disease_group || 'N/A'}
                        </td>
                        <td className="table-arrow-cell">
                          <button
                            type="button"
                            className="expand-button"
                            onClick={(event) => {
                              event.stopPropagation()
                              toggleExpandedRow(patient.registry_id)
                            }}
                          >
                            {expandedRegistryId === patient.registry_id ? (
                              <ChevronDown size={18} />
                            ) : (
                              <ChevronRight size={18} />
                            )}
                          </button>
                        </td>
                      </tr>
                      {expandedRegistryId === patient.registry_id ? (
                        <tr className="registry-expanded-row">
                          <td colSpan={10}>
                            <div className="expanded-summary">
                              <div className="expanded-grid">
                                <div>
                                  <span className="expanded-label">Registration No</span>
                                  <strong>{patient.registration_no || 'N/A'}</strong>
                                </div>
                                <div>
                                  <span className="expanded-label">Legacy ID</span>
                                  <strong>{patient.legacy_id ?? 'N/A'}</strong>
                                </div>
                                <div>
                                  <span className="expanded-label">Socio-economic</span>
                                  <strong>{patient.socio_economic_status || 'N/A'}</strong>
                                </div>
                                <div>
                                  <span className="expanded-label">Latest site</span>
                                  <strong>{patient.latest_observation?.diagnosis_primary_site || 'N/A'}</strong>
                                </div>
                                <div>
                                  <span className="expanded-label">Latest laterality</span>
                                  <strong>{patient.latest_observation?.diagnosis_laterality || 'N/A'}</strong>
                                </div>
                                <div>
                                  <span className="expanded-label">Latest observed at</span>
                                  <strong>{patient.latest_observation?.observed_at || 'N/A'}</strong>
                                </div>
                              </div>
                              <div className="expanded-actions">
                                {patient.can_edit ? (
                                  <button
                                    type="button"
                                    className="secondary-button"
                                    onClick={(event) => {
                                      event.stopPropagation()
                                      navigate(`/patients/${patient.registry_id}/edit`)
                                    }}
                                  >
                                    Edit Record
                                  </button>
                                ) : null}
                                <button
                                  type="button"
                                  className="secondary-button"
                                  onClick={(event) => {
                                    event.stopPropagation()
                                    navigate(`/patients/${patient.registry_id}`)
                                  }}
                                >
                                  Open Full Record
                                </button>
                              </div>
                            </div>
                          </td>
                        </tr>
                      ) : null}
                    </Fragment>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="pagination-row">
              <button
                type="button"
                className="pager-button"
                disabled={!hasPreviousPage}
                onClick={() => goToPage(page - 1)}
              >
                <ChevronLeft size={16} />
                Previous
              </button>
              <span className="pagination-label">Page {page}</span>
              <button
                type="button"
                className="pager-button"
                disabled={!hasNextPage}
                onClick={() => goToPage(page + 1)}
              >
                Next
                <ChevronRight size={16} />
              </button>
            </div>
          </>
        ) : (
          <EmptyState
            title="No patients found"
            detail="Try searching with a phone number, registration number, registry ID, or patient name."
          />
        )}
      </section>
    </section>
  )
}
