import { type ReactNode, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Activity,
  ArrowLeft,
  ChevronDown,
  ClipboardList,
  Dna,
  Download,
  FileText,
  HeartPulse,
  Printer,
  UserRound,
} from 'lucide-react'
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import { fetchPatientDetail } from '../api'
import {
  DataBadge,
  DataPoint,
  EmptyState,
  ListPanel,
  LoadingState,
} from '../components/registry-ui'
import {
  buildMarkerSeries,
  buildObservationTrend,
  buildTreatmentMix,
  compactJoin,
  formatDate,
  formatDateTime,
  formatMeasure,
  formatStage,
  joinValues,
  metricPalette,
} from '../lib/registry'

function hasChanged(left: string | number | null | undefined, right: string | number | null | undefined) {
  return String(left ?? '').trim() !== String(right ?? '').trim()
}

function stageScore(value: string | null | undefined) {
  if (!value) {
    return 0
  }
  const normalized = value.toUpperCase()
  if (normalized === 'X') {
    return 0
  }
  const numeric = Number(normalized.replace(/[^0-9.]/g, ''))
  return Number.isFinite(numeric) ? numeric : 0
}

function ClinicalCard({
  id,
  eyebrow,
  title,
  icon,
  count,
  hasData,
  defaultOpen = false,
  emptyMessage,
  children,
}: {
  id: string
  eyebrow: string
  title: string
  icon: ReactNode
  count?: number
  hasData: boolean
  defaultOpen?: boolean
  emptyMessage: string
  children: ReactNode
}) {
  return (
    <details className={hasData ? 'clinical-card clinical-card-populated' : 'clinical-card'} id={id} open={defaultOpen}>
      <summary>
        <span className="clinical-card-icon">{icon}</span>
        <span className="clinical-card-title">
          <small>{eyebrow}</small>
          <strong>{title}</strong>
        </span>
        <span className={hasData ? 'clinical-card-state clinical-card-state-live' : 'clinical-card-state'}>
          {hasData ? `${count ?? 1} recorded` : 'No data'}
        </span>
        <ChevronDown className="clinical-card-chevron" size={18} aria-hidden="true" />
      </summary>
      <div className="clinical-card-body">
        {hasData ? children : <p className="clinical-card-empty-copy">{emptyMessage}</p>}
      </div>
    </details>
  )
}

export default function PatientDetailPage() {
  const { registryId = '' } = useParams()
  const [searchParams, setSearchParams] = useSearchParams()
  const patientQuery = useQuery({
    queryKey: ['patient-detail', registryId],
    queryFn: () => fetchPatientDetail(registryId),
    enabled: Boolean(registryId),
  })
  const patient = patientQuery.data ?? null
  const siteFilter = searchParams.get('site') ?? 'all'
  const draftFilter = searchParams.get('draft') ?? 'all'

  const filteredObservations = useMemo(
    () =>
      (patient?.observations ?? []).filter((observation) => {
        const siteMatches =
          siteFilter === 'all' ||
          (observation.diagnosis_primary_site ?? '').toLowerCase() === siteFilter
        const draftMatches =
          draftFilter === 'all' ||
          (draftFilter === 'draft' ? observation.is_draft : !observation.is_draft)

        return siteMatches && draftMatches
      }),
    [draftFilter, patient?.observations, siteFilter],
  )

  const availableSites = useMemo(
    () =>
      [
        ...new Set(
          (patient?.observations ?? [])
            .map((observation) => observation.diagnosis_primary_site?.trim())
            .filter((site): site is string => Boolean(site)),
        ),
      ].sort((left, right) => left.localeCompare(right)),
    [patient?.observations],
  )

  const requestedObservation = Math.max(
    0,
    Number(searchParams.get('observation') ?? '0') || 0,
  )
  const requestedCompareObservation = Math.max(
    0,
    Number(searchParams.get('compare') ?? '0') || 0,
  )
  const activeObservationIndex = Math.min(
    requestedObservation,
    Math.max(filteredObservations.length - 1, 0),
  )
  const compareObservationIndex = Math.min(
    requestedCompareObservation,
    Math.max(filteredObservations.length - 1, 0),
  )
  const activeObservation = filteredObservations[activeObservationIndex]
  const compareObservation = filteredObservations[compareObservationIndex]
  const observationTrend = buildObservationTrend(patient?.observations ?? [])
  const treatmentMix = buildTreatmentMix(patient?.observations ?? [])
  const markerSeries = buildMarkerSeries(patient?.observations ?? [])
  const molecularProfile = useMemo(() => {
    const counts = new Map<string, number>()
    filteredObservations.forEach((observation) => {
      observation.molecular_pathologies.forEach((item) => {
        const label = item.gene || item.method || item.status || 'Unspecified'
        counts.set(label, (counts.get(label) ?? 0) + 1)
      })
    })
    return [...counts.entries()]
      .map(([label, value]) => ({ label, value }))
      .sort((left, right) => right.value - left.value || left.label.localeCompare(right.label))
      .slice(0, 8)
  }, [filteredObservations])
  const stagingTrend = useMemo(
    () =>
      filteredObservations.map((observation, index) => ({
        label: `Obs ${index + 1}`,
        clinical:
          stageScore(observation.clinical_stagings[0]?.t) +
          stageScore(observation.clinical_stagings[0]?.n) +
          stageScore(observation.clinical_stagings[0]?.m),
        pathological:
          stageScore(observation.pathological_stagings[0]?.t) +
          stageScore(observation.pathological_stagings[0]?.n) +
          stageScore(observation.pathological_stagings[0]?.m),
      })),
    [filteredObservations],
  )
  const treatmentTrend = useMemo(
    () =>
      filteredObservations.map((observation, index) => ({
        label: `Obs ${index + 1}`,
        cycles: observation.treatment_cycles.length,
        radiotherapy: observation.radiotherapy_schedules.length,
        surgeries: observation.surgeries.length,
      })),
    [filteredObservations],
  )
  const activeHistory = activeObservation?.history
  const activeClinicalStage = activeObservation?.clinical_stagings[0]
  const activePathologicalStage = activeObservation?.pathological_stagings[0]
  const activePathologicalDetail =
    activeObservation?.pathological_staging_details[0]
  const activeIhcPanel = activeObservation?.ihc_panels[0]
  const comparisonHighlights = [
    {
      label: 'Observation date',
      changed: hasChanged(activeObservation?.observed_at, compareObservation?.observed_at),
      summary: `${formatDate(activeObservation?.observed_at)} -> ${formatDate(compareObservation?.observed_at)}`,
    },
    {
      label: 'Disease group',
      changed: hasChanged(
        activeObservation?.diagnosis_disease_group,
        compareObservation?.diagnosis_disease_group,
      ),
      summary: `${activeObservation?.diagnosis_disease_group || 'N/A'} -> ${compareObservation?.diagnosis_disease_group || 'N/A'}`,
    },
    {
      label: 'Primary site',
      changed: hasChanged(
        activeObservation?.diagnosis_primary_site,
        compareObservation?.diagnosis_primary_site,
      ),
      summary: `${activeObservation?.diagnosis_primary_site || 'N/A'} -> ${compareObservation?.diagnosis_primary_site || 'N/A'}`,
    },
    {
      label: 'Clinical TNM',
      changed: hasChanged(
        formatStage(
          activeObservation?.clinical_stagings[0]?.t,
          activeObservation?.clinical_stagings[0]?.n,
          activeObservation?.clinical_stagings[0]?.m,
        ),
        formatStage(
          compareObservation?.clinical_stagings[0]?.t,
          compareObservation?.clinical_stagings[0]?.n,
          compareObservation?.clinical_stagings[0]?.m,
        ),
      ),
      summary: `${formatStage(
        activeObservation?.clinical_stagings[0]?.t,
        activeObservation?.clinical_stagings[0]?.n,
        activeObservation?.clinical_stagings[0]?.m,
      ) || 'N/A'} -> ${formatStage(
        compareObservation?.clinical_stagings[0]?.t,
        compareObservation?.clinical_stagings[0]?.n,
        compareObservation?.clinical_stagings[0]?.m,
      ) || 'N/A'}`,
    },
    {
      label: 'Pathological TNM',
      changed: hasChanged(
        formatStage(
          activeObservation?.pathological_stagings[0]?.t,
          activeObservation?.pathological_stagings[0]?.n,
          activeObservation?.pathological_stagings[0]?.m,
        ),
        formatStage(
          compareObservation?.pathological_stagings[0]?.t,
          compareObservation?.pathological_stagings[0]?.n,
          compareObservation?.pathological_stagings[0]?.m,
        ),
      ),
      summary: `${formatStage(
        activeObservation?.pathological_stagings[0]?.t,
        activeObservation?.pathological_stagings[0]?.n,
        activeObservation?.pathological_stagings[0]?.m,
      ) || 'N/A'} -> ${formatStage(
        compareObservation?.pathological_stagings[0]?.t,
        compareObservation?.pathological_stagings[0]?.n,
        compareObservation?.pathological_stagings[0]?.m,
      ) || 'N/A'}`,
    },
    {
      label: 'Treatment load',
      changed:
        hasChanged(
          activeObservation?.treatment_cycles.length,
          compareObservation?.treatment_cycles.length,
        ) ||
        hasChanged(
          activeObservation?.radiotherapy_schedules.length,
          compareObservation?.radiotherapy_schedules.length,
        ) ||
        hasChanged(activeObservation?.surgeries.length, compareObservation?.surgeries.length),
      summary: `Cycles ${activeObservation?.treatment_cycles.length ?? 0} -> ${compareObservation?.treatment_cycles.length ?? 0}, RT ${activeObservation?.radiotherapy_schedules.length ?? 0} -> ${compareObservation?.radiotherapy_schedules.length ?? 0}, Surgery ${activeObservation?.surgeries.length ?? 0} -> ${compareObservation?.surgeries.length ?? 0}`,
    },
    {
      label: 'Marker profile',
      changed: hasChanged(
        joinValues(activeObservation?.cancer_markers.map((item) => compactJoin([item.name, item.value])) ?? []),
        joinValues(compareObservation?.cancer_markers.map((item) => compactJoin([item.name, item.value])) ?? []),
      ),
      summary: `${joinValues(
        activeObservation?.cancer_markers.map((item) => compactJoin([item.name, item.value])) ?? [],
      ) || 'N/A'} -> ${joinValues(
        compareObservation?.cancer_markers.map((item) => compactJoin([item.name, item.value])) ?? [],
      ) || 'N/A'}`,
    },
  ].filter((item) => item.changed)
  const compareReportLines = [
    `Primary observation: ${formatDateTime(activeObservation?.observed_at) || 'N/A'}${
      activeObservation?.center_name ? ` at ${activeObservation.center_name}` : ''
    }`,
    `Comparison observation: ${formatDateTime(compareObservation?.observed_at) || 'N/A'}${
      compareObservation?.center_name ? ` at ${compareObservation.center_name}` : ''
    }`,
    hasChanged(
      activeObservation?.diagnosis_primary_site,
      compareObservation?.diagnosis_primary_site,
    )
      ? `Primary site changed from ${activeObservation?.diagnosis_primary_site || 'N/A'} to ${compareObservation?.diagnosis_primary_site || 'N/A'}.`
      : `Primary site remained ${activeObservation?.diagnosis_primary_site || 'N/A'}.`,
    hasChanged(
      activeObservation?.diagnosis_disease_group,
      compareObservation?.diagnosis_disease_group,
    )
      ? `Disease group changed from ${activeObservation?.diagnosis_disease_group || 'N/A'} to ${compareObservation?.diagnosis_disease_group || 'N/A'}.`
      : `Disease group remained ${activeObservation?.diagnosis_disease_group || 'N/A'}.`,
    hasChanged(
      formatStage(
        activeObservation?.clinical_stagings[0]?.t,
        activeObservation?.clinical_stagings[0]?.n,
        activeObservation?.clinical_stagings[0]?.m,
      ),
      formatStage(
        compareObservation?.clinical_stagings[0]?.t,
        compareObservation?.clinical_stagings[0]?.n,
        compareObservation?.clinical_stagings[0]?.m,
      ),
    )
      ? `Clinical TNM changed from ${
          formatStage(
            activeObservation?.clinical_stagings[0]?.t,
            activeObservation?.clinical_stagings[0]?.n,
            activeObservation?.clinical_stagings[0]?.m,
          ) || 'N/A'
        } to ${
          formatStage(
            compareObservation?.clinical_stagings[0]?.t,
            compareObservation?.clinical_stagings[0]?.n,
            compareObservation?.clinical_stagings[0]?.m,
          ) || 'N/A'
        }.`
      : `Clinical TNM remained ${
          formatStage(
            activeObservation?.clinical_stagings[0]?.t,
            activeObservation?.clinical_stagings[0]?.n,
            activeObservation?.clinical_stagings[0]?.m,
          ) || 'N/A'
        }.`,
    hasChanged(
      joinValues(activeObservation?.cancer_markers.map((item) => compactJoin([item.name, item.value, item.unit])) ?? []),
      joinValues(compareObservation?.cancer_markers.map((item) => compactJoin([item.name, item.value, item.unit])) ?? []),
    )
      ? `Marker profile changed from ${
          joinValues(
            activeObservation?.cancer_markers.map((item) => compactJoin([item.name, item.value, item.unit])) ?? [],
          ) || 'N/A'
        } to ${
          joinValues(
            compareObservation?.cancer_markers.map((item) => compactJoin([item.name, item.value, item.unit])) ?? [],
          ) || 'N/A'
        }.`
      : `Marker profile remained ${
          joinValues(
            activeObservation?.cancer_markers.map((item) => compactJoin([item.name, item.value, item.unit])) ?? [],
          ) || 'N/A'
        }.`,
    `Treatment burden: cycles ${activeObservation?.treatment_cycles.length ?? 0} -> ${compareObservation?.treatment_cycles.length ?? 0}, radiotherapy ${activeObservation?.radiotherapy_schedules.length ?? 0} -> ${compareObservation?.radiotherapy_schedules.length ?? 0}, surgeries ${activeObservation?.surgeries.length ?? 0} -> ${compareObservation?.surgeries.length ?? 0}.`,
  ]
  const sectionLinks = [
    { id: 'clinical-snapshot', label: 'Snapshot' },
    { id: 'demography', label: 'Demography' },
    { id: 'history', label: 'History' },
    { id: 'diagnosis', label: 'Diagnosis' },
    { id: 'staging', label: 'Staging' },
    { id: 'pathology', label: 'Pathology' },
    { id: 'treatment', label: 'Treatment' },
    { id: 'marker-trend', label: 'Markers' },
    { id: 'observation-timeline', label: 'Timeline' },
  ]

  if (patientQuery.isLoading) {
    return (
      <section className="panel">
        <LoadingState label="Loading patient detail" />
      </section>
    )
  }

  if (!patient) {
    return (
      <section className="panel">
        <EmptyState
          title="Patient not found"
          detail="The selected registry record could not be loaded."
        />
      </section>
    )
  }
  const currentPatient = patient

  function updateFilters(nextSite: string, nextDraft: string) {
    const next = new URLSearchParams(searchParams)
    if (nextSite === 'all') {
      next.delete('site')
    } else {
      next.set('site', nextSite)
    }
    if (nextDraft === 'all') {
      next.delete('draft')
    } else {
      next.set('draft', nextDraft)
    }
    next.delete('observation')
    next.delete('compare')
    setSearchParams(next, { replace: true })
  }

  function selectObservation(index: number) {
    const next = new URLSearchParams(searchParams)
    if (index === 0) {
      next.delete('observation')
    } else {
      next.set('observation', String(index))
    }
    setSearchParams(next, { replace: true })
  }

  function selectCompareObservation(index: number) {
    const next = new URLSearchParams(searchParams)
    if (index === 0) {
      next.delete('compare')
    } else {
      next.set('compare', String(index))
    }
    setSearchParams(next, { replace: true })
  }

  function focusObservation(index: number) {
    selectObservation(index)
    const section = document.getElementById('clinical-snapshot')
    section?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  function printRecord() {
    window.print()
  }

  function exportSummary() {
    const lines = [
      `Patient Name,${currentPatient.name || ''}`,
      `Registry ID,${currentPatient.registry_id || ''}`,
      `Legacy Unique ID,${currentPatient.legacy_unique_id || ''}`,
      `Registration No,${currentPatient.registration_no || ''}`,
      `Phone,${currentPatient.phone || ''}`,
      `Gender,${currentPatient.gender || ''}`,
      `Age,${currentPatient.age ?? ''}`,
      `District,${currentPatient.district || ''}`,
      `Publication Filter,${draftFilter}`,
      `Site Filter,${siteFilter}`,
      '',
      'Selected Observation',
      `Observed At,${activeObservation?.observed_at || ''}`,
      `Doctor,${activeObservation?.consulting_doctor_name || ''}`,
      `Center,${activeObservation?.center_name || ''}`,
      `Cancer Type,${activeObservation?.cancer_type || ''}`,
      `Disease Group,${activeObservation?.diagnosis_disease_group || ''}`,
      `Primary Site,${activeObservation?.diagnosis_primary_site || ''}`,
      `Laterality,${activeObservation?.diagnosis_laterality || ''}`,
      `Grade,${activeObservation?.grade || ''}`,
      '',
      'Observation Timeline',
      ...filteredObservations.map(
        (observation, index) =>
          [
            index + 1,
            observation.observed_at || '',
            observation.is_draft ? 'Draft' : 'Published',
            observation.diagnosis_disease_group || '',
            observation.diagnosis_primary_site || '',
            observation.center_name || '',
          ].join(','),
      ),
    ]
    const blob = new Blob([lines.join('\n')], {
      type: 'text/csv;charset=utf-8;',
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${currentPatient.registry_id || 'patient-record'}-summary.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  function exportCompareCsv() {
    const rows = [
      ['Field', 'Primary Observation', 'Comparison Observation'],
      ['Observed At', formatDateTime(activeObservation?.observed_at), formatDateTime(compareObservation?.observed_at)],
      ['Doctor', activeObservation?.consulting_doctor_name || '', compareObservation?.consulting_doctor_name || ''],
      ['Center', activeObservation?.center_name || '', compareObservation?.center_name || ''],
      ['Disease Group', activeObservation?.diagnosis_disease_group || '', compareObservation?.diagnosis_disease_group || ''],
      ['Primary Site', activeObservation?.diagnosis_primary_site || '', compareObservation?.diagnosis_primary_site || ''],
      ['Laterality', activeObservation?.diagnosis_laterality || '', compareObservation?.diagnosis_laterality || ''],
      ['Clinical TNM',
        formatStage(
          activeObservation?.clinical_stagings[0]?.t,
          activeObservation?.clinical_stagings[0]?.n,
          activeObservation?.clinical_stagings[0]?.m,
        ) || '',
        formatStage(
          compareObservation?.clinical_stagings[0]?.t,
          compareObservation?.clinical_stagings[0]?.n,
          compareObservation?.clinical_stagings[0]?.m,
        ) || '',
      ],
      ['Pathological TNM',
        formatStage(
          activeObservation?.pathological_stagings[0]?.t,
          activeObservation?.pathological_stagings[0]?.n,
          activeObservation?.pathological_stagings[0]?.m,
        ) || '',
        formatStage(
          compareObservation?.pathological_stagings[0]?.t,
          compareObservation?.pathological_stagings[0]?.n,
          compareObservation?.pathological_stagings[0]?.m,
        ) || '',
      ],
      ['Treatment Cycles', String(activeObservation?.treatment_cycles.length ?? 0), String(compareObservation?.treatment_cycles.length ?? 0)],
      ['Radiotherapy Schedules', String(activeObservation?.radiotherapy_schedules.length ?? 0), String(compareObservation?.radiotherapy_schedules.length ?? 0)],
      ['Surgeries', String(activeObservation?.surgeries.length ?? 0), String(compareObservation?.surgeries.length ?? 0)],
      [
        'Cancer Markers',
        joinValues(
          activeObservation?.cancer_markers.map((item) => compactJoin([item.name, item.value, item.unit])) ?? [],
        ),
        joinValues(
          compareObservation?.cancer_markers.map((item) => compactJoin([item.name, item.value, item.unit])) ?? [],
        ),
      ],
    ]
    const content = rows
      .map((row) => row.map((value) => `"${String(value ?? '').replaceAll('"', '""')}"`).join(','))
      .join('\n')
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${currentPatient.registry_id || 'patient-record'}-comparison.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  async function copyCompareReport() {
    try {
      await navigator.clipboard.writeText(compareReportLines.join('\n'))
    } catch (_error) {
      window.alert('Copy failed. You can still print or export the summary.')
    }
  }

  return (
    <section className="page-grid">
      <Link className="back-link" to="/patients">
        <ArrowLeft size={16} />
        Back to search
      </Link>

      <section className="hero-panel hero-panel-tight">
        <div className="hero-copy">
          <p className="eyebrow">Patient Record</p>
          <h2>{patient.name || patient.registry_id}</h2>
          <p className="hero-text">
            {patient.registry_id}
            {patient.legacy_unique_id ? ` | ${patient.legacy_unique_id}` : ''}
            {patient.registration_no ? ` | Reg ${patient.registration_no}` : ''}
          </p>
        </div>
        <div className="header-badges">
          <span className="data-pill">{patient.gender || 'Gender N/A'}</span>
          <span className="data-pill">
            {patient.age ? `${patient.age} years` : 'Age N/A'}
          </span>
          <span className="data-pill">{patient.phone || 'No phone'}</span>
        </div>
      </section>

      <section className="panel detail-toolbar-panel">
        <div className="detail-toolbar">
          <div className="section-nav" aria-label="Patient detail sections">
            {sectionLinks.map((section) => (
              <a key={section.id} className="section-chip" href={`#${section.id}`}>
                {section.label}
              </a>
            ))}
          </div>
          <div className="panel-actions">
            {patient.can_edit ? (
              <Link className="secondary-button" to={`/patients/${patient.registry_id}/edit`}>
                Edit record
              </Link>
            ) : null}
            <button type="button" className="secondary-button" onClick={printRecord}>
              <Printer size={16} />
              Print record
            </button>
            <button type="button" className="secondary-button" onClick={exportSummary}>
              <Download size={16} />
              Export summary
            </button>
          </div>
        </div>
      </section>

      <section className="panel panel-compact">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Observation Filter</p>
            <h3>Narrow visits fast</h3>
          </div>
          <span className="result-chip">
            {filteredObservations.length} of {currentPatient.observations.length} shown
          </span>
        </div>
        <div className="filter-bar">
          <label className="filter-field">
            <span>Primary site</span>
            <select
              className="filter-select"
              value={siteFilter}
              onChange={(event) => updateFilters(event.target.value, draftFilter)}
            >
              <option value="all">All sites</option>
              {availableSites.map((site) => (
                <option key={site} value={site.toLowerCase()}>
                  {site}
                </option>
              ))}
            </select>
          </label>
          <label className="filter-field">
            <span>Publication state</span>
            <select
              className="filter-select"
              value={draftFilter}
              onChange={(event) => updateFilters(siteFilter, event.target.value)}
            >
              <option value="all">All observations</option>
              <option value="published">Published only</option>
              <option value="draft">Draft only</option>
            </select>
          </label>
        </div>
      </section>

      <section className="panel panel-compact">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Observation Switcher</p>
            <h3>Visit selector</h3>
          </div>
          <span className="result-chip">
            {filteredObservations.length
              ? `Observation ${activeObservationIndex + 1} of ${filteredObservations.length}`
              : 'No observations'}
          </span>
        </div>
        {filteredObservations.length ? (
          <div className="observation-strip observation-strip-compact">
            {filteredObservations.map((observation, index) => (
              <button
                key={observation.id}
                type="button"
                className={
                  index === activeObservationIndex
                    ? 'observation-tab observation-tab-active'
                    : 'observation-tab'
                }
                onClick={() => selectObservation(index)}
              >
                <span>Obs {index + 1}</span>
                <strong>{formatDate(observation.observed_at)}</strong>
                <small>{observation.diagnosis_primary_site || 'No site'}</small>
              </button>
            ))}
          </div>
        ) : (
          <EmptyState
            title="No observations match the current filter"
            detail="Try switching the site or publication-state filters to bring observations back into view."
          />
        )}
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Observation Compare</p>
            <h3>Place two visits side by side</h3>
          </div>
          <span className="result-chip">
            {filteredObservations.length ? `Comparing ${activeObservationIndex + 1} and ${compareObservationIndex + 1}` : 'No observations'}
          </span>
        </div>
        {filteredObservations.length ? (
          <>
            <div className="compare-report">
              <div className="compare-report-head">
                <div>
                  <p className="eyebrow">Clinical Brief</p>
                  <h3>Shareable comparison summary</h3>
                </div>
                <div className="panel-actions">
                  <button type="button" className="secondary-button" onClick={exportCompareCsv}>
                    <Download size={16} />
                    Export compare CSV
                  </button>
                  <button type="button" className="secondary-button" onClick={copyCompareReport}>
                    <FileText size={16} />
                    Copy summary
                  </button>
                </div>
              </div>
              <div className="compare-report-body">
                {compareReportLines.map((line) => (
                  <p key={line}>{line}</p>
                ))}
              </div>
            </div>
            <div className="compare-summary">
              {comparisonHighlights.length ? (
                comparisonHighlights.map((item) => (
                  <article key={item.label} className="compare-summary-card">
                    <span className="compare-summary-label">{item.label}</span>
                    <strong>{item.summary}</strong>
                  </article>
                ))
              ) : (
                <article className="compare-summary-card compare-summary-card-neutral">
                  <span className="compare-summary-label">Comparison summary</span>
                  <strong>No meaningful changes across the tracked clinical fields.</strong>
                </article>
              )}
            </div>
            <div className="filter-bar">
              <label className="filter-field">
                <span>Primary observation</span>
                <select
                  className="filter-select"
                  value={String(activeObservationIndex)}
                  onChange={(event) => selectObservation(Number(event.target.value))}
                >
                  {filteredObservations.map((observation, index) => (
                    <option key={`primary-${observation.id}`} value={index}>
                      {`Obs ${index + 1} · ${formatDate(observation.observed_at)} · ${observation.diagnosis_primary_site || 'No site'}`}
                    </option>
                  ))}
                </select>
              </label>
              <label className="filter-field">
                <span>Comparison observation</span>
                <select
                  className="filter-select"
                  value={String(compareObservationIndex)}
                  onChange={(event) => selectCompareObservation(Number(event.target.value))}
                >
                  {filteredObservations.map((observation, index) => (
                    <option key={`compare-${observation.id}`} value={index}>
                      {`Obs ${index + 1} · ${formatDate(observation.observed_at)} · ${observation.diagnosis_primary_site || 'No site'}`}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <div className="compare-grid">
              <article className="compare-card">
                <div className="compare-card-head">
                  <p className="timeline-title">Primary observation</p>
                  <span className={activeObservation?.is_draft ? 'status-pill status-draft' : 'status-pill status-live'}>
                    {activeObservation?.is_draft ? 'Draft' : 'Published'}
                  </span>
                </div>
                <div className="detail-grid">
                  <div className={hasChanged(activeObservation?.observed_at, compareObservation?.observed_at) ? 'compare-point compare-point-changed' : 'compare-point'}>
                    <DataPoint label="Observed at" value={formatDateTime(activeObservation?.observed_at)} />
                  </div>
                  <div className={hasChanged(activeObservation?.consulting_doctor_name, compareObservation?.consulting_doctor_name) ? 'compare-point compare-point-changed' : 'compare-point'}>
                    <DataPoint label="Doctor" value={activeObservation?.consulting_doctor_name} />
                  </div>
                  <div className={hasChanged(activeObservation?.center_name, compareObservation?.center_name) ? 'compare-point compare-point-changed' : 'compare-point'}>
                    <DataPoint label="Center" value={activeObservation?.center_name} />
                  </div>
                  <div className={hasChanged(activeObservation?.diagnosis_disease_group, compareObservation?.diagnosis_disease_group) ? 'compare-point compare-point-changed' : 'compare-point'}>
                    <DataPoint label="Disease group" value={activeObservation?.diagnosis_disease_group} />
                  </div>
                  <div className={hasChanged(activeObservation?.diagnosis_primary_site, compareObservation?.diagnosis_primary_site) ? 'compare-point compare-point-changed' : 'compare-point'}>
                    <DataPoint label="Primary site" value={activeObservation?.diagnosis_primary_site} />
                  </div>
                  <div className={hasChanged(activeObservation?.diagnosis_laterality, compareObservation?.diagnosis_laterality) ? 'compare-point compare-point-changed' : 'compare-point'}>
                    <DataPoint label="Laterality" value={activeObservation?.diagnosis_laterality} />
                  </div>
                  <div className={hasChanged(activeObservation?.grade, compareObservation?.grade) ? 'compare-point compare-point-changed' : 'compare-point'}>
                    <DataPoint label="Grade" value={activeObservation?.grade} />
                  </div>
                  <div
                    className={
                      hasChanged(
                        joinValues(activeObservation?.metastatic_sites.map((item) => item.value) ?? []),
                        joinValues(compareObservation?.metastatic_sites.map((item) => item.value) ?? []),
                      )
                        ? 'compare-point compare-point-changed'
                        : 'compare-point'
                    }
                    >
                      <DataPoint
                        label="Metastatic sites"
                        value={joinValues(activeObservation?.metastatic_sites.map((item) => item.value) ?? [])}
                      />
                    </div>
                  <div
                    className={
                      hasChanged(
                        formatStage(
                          activeObservation?.clinical_stagings[0]?.t,
                          activeObservation?.clinical_stagings[0]?.n,
                          activeObservation?.clinical_stagings[0]?.m,
                        ),
                        formatStage(
                          compareObservation?.clinical_stagings[0]?.t,
                          compareObservation?.clinical_stagings[0]?.n,
                          compareObservation?.clinical_stagings[0]?.m,
                        ),
                      )
                        ? 'compare-point compare-point-changed'
                        : 'compare-point'
                    }
                  >
                    <DataPoint
                      label="Clinical TNM"
                      value={formatStage(
                        activeObservation?.clinical_stagings[0]?.t,
                        activeObservation?.clinical_stagings[0]?.n,
                        activeObservation?.clinical_stagings[0]?.m,
                      )}
                    />
                  </div>
                  <div
                    className={
                      hasChanged(
                        formatStage(
                          activeObservation?.pathological_stagings[0]?.t,
                          activeObservation?.pathological_stagings[0]?.n,
                          activeObservation?.pathological_stagings[0]?.m,
                        ),
                        formatStage(
                          compareObservation?.pathological_stagings[0]?.t,
                          compareObservation?.pathological_stagings[0]?.n,
                          compareObservation?.pathological_stagings[0]?.m,
                        ),
                      )
                        ? 'compare-point compare-point-changed'
                        : 'compare-point'
                    }
                  >
                    <DataPoint
                      label="Pathological TNM"
                      value={formatStage(
                        activeObservation?.pathological_stagings[0]?.t,
                        activeObservation?.pathological_stagings[0]?.n,
                        activeObservation?.pathological_stagings[0]?.m,
                      )}
                    />
                  </div>
                  <div
                    className={
                      hasChanged(
                        activeObservation?.treatment_cycles.length,
                        compareObservation?.treatment_cycles.length,
                      )
                        ? 'compare-point compare-point-changed'
                        : 'compare-point'
                    }
                  >
                    <DataPoint
                      label="Treatment cycles"
                      value={activeObservation?.treatment_cycles.length ?? 0}
                    />
                  </div>
                  <div
                    className={
                      hasChanged(
                        activeObservation?.radiotherapy_schedules.length,
                        compareObservation?.radiotherapy_schedules.length,
                      )
                        ? 'compare-point compare-point-changed'
                        : 'compare-point'
                    }
                  >
                    <DataPoint
                      label="Radiotherapy schedules"
                      value={activeObservation?.radiotherapy_schedules.length ?? 0}
                    />
                  </div>
                  <div
                    className={
                      hasChanged(
                        activeObservation?.surgeries.length,
                        compareObservation?.surgeries.length,
                      )
                        ? 'compare-point compare-point-changed'
                        : 'compare-point'
                    }
                  >
                    <DataPoint
                      label="Surgeries"
                      value={activeObservation?.surgeries.length ?? 0}
                    />
                  </div>
                  <div
                    className={
                      hasChanged(
                        joinValues(activeObservation?.cancer_markers.map((item) => compactJoin([item.name, item.value])) ?? []),
                        joinValues(compareObservation?.cancer_markers.map((item) => compactJoin([item.name, item.value])) ?? []),
                      )
                        ? 'compare-point compare-point-changed'
                        : 'compare-point'
                    }
                  >
                    <DataPoint
                      label="Cancer markers"
                      value={joinValues(
                        activeObservation?.cancer_markers.map((item) =>
                          compactJoin([item.name, item.value, item.unit]),
                        ) ?? [],
                      )}
                    />
                  </div>
                  <div
                    className={
                      hasChanged(
                        joinValues(activeObservation?.histopathologies.map((item) => item.detail) ?? []),
                        joinValues(compareObservation?.histopathologies.map((item) => item.detail) ?? []),
                      )
                        ? 'compare-point compare-point-changed'
                        : 'compare-point'
                    }
                  >
                    <DataPoint
                      label="Histopathology"
                      value={joinValues(
                        activeObservation?.histopathologies.map((item) => item.detail) ?? [],
                      )}
                    />
                  </div>
                </div>
              </article>
              <article className="compare-card">
                <div className="compare-card-head">
                  <p className="timeline-title">Comparison observation</p>
                  <span className={compareObservation?.is_draft ? 'status-pill status-draft' : 'status-pill status-live'}>
                    {compareObservation?.is_draft ? 'Draft' : 'Published'}
                  </span>
                </div>
                <div className="detail-grid">
                  <div className={hasChanged(compareObservation?.observed_at, activeObservation?.observed_at) ? 'compare-point compare-point-changed' : 'compare-point'}>
                    <DataPoint label="Observed at" value={formatDateTime(compareObservation?.observed_at)} />
                  </div>
                  <div className={hasChanged(compareObservation?.consulting_doctor_name, activeObservation?.consulting_doctor_name) ? 'compare-point compare-point-changed' : 'compare-point'}>
                    <DataPoint label="Doctor" value={compareObservation?.consulting_doctor_name} />
                  </div>
                  <div className={hasChanged(compareObservation?.center_name, activeObservation?.center_name) ? 'compare-point compare-point-changed' : 'compare-point'}>
                    <DataPoint label="Center" value={compareObservation?.center_name} />
                  </div>
                  <div className={hasChanged(compareObservation?.diagnosis_disease_group, activeObservation?.diagnosis_disease_group) ? 'compare-point compare-point-changed' : 'compare-point'}>
                    <DataPoint label="Disease group" value={compareObservation?.diagnosis_disease_group} />
                  </div>
                  <div className={hasChanged(compareObservation?.diagnosis_primary_site, activeObservation?.diagnosis_primary_site) ? 'compare-point compare-point-changed' : 'compare-point'}>
                    <DataPoint label="Primary site" value={compareObservation?.diagnosis_primary_site} />
                  </div>
                  <div className={hasChanged(compareObservation?.diagnosis_laterality, activeObservation?.diagnosis_laterality) ? 'compare-point compare-point-changed' : 'compare-point'}>
                    <DataPoint label="Laterality" value={compareObservation?.diagnosis_laterality} />
                  </div>
                  <div className={hasChanged(compareObservation?.grade, activeObservation?.grade) ? 'compare-point compare-point-changed' : 'compare-point'}>
                    <DataPoint label="Grade" value={compareObservation?.grade} />
                  </div>
                  <div
                    className={
                      hasChanged(
                        joinValues(compareObservation?.metastatic_sites.map((item) => item.value) ?? []),
                        joinValues(activeObservation?.metastatic_sites.map((item) => item.value) ?? []),
                      )
                        ? 'compare-point compare-point-changed'
                        : 'compare-point'
                    }
                    >
                      <DataPoint
                        label="Metastatic sites"
                        value={joinValues(compareObservation?.metastatic_sites.map((item) => item.value) ?? [])}
                      />
                    </div>
                  <div
                    className={
                      hasChanged(
                        formatStage(
                          compareObservation?.clinical_stagings[0]?.t,
                          compareObservation?.clinical_stagings[0]?.n,
                          compareObservation?.clinical_stagings[0]?.m,
                        ),
                        formatStage(
                          activeObservation?.clinical_stagings[0]?.t,
                          activeObservation?.clinical_stagings[0]?.n,
                          activeObservation?.clinical_stagings[0]?.m,
                        ),
                      )
                        ? 'compare-point compare-point-changed'
                        : 'compare-point'
                    }
                  >
                    <DataPoint
                      label="Clinical TNM"
                      value={formatStage(
                        compareObservation?.clinical_stagings[0]?.t,
                        compareObservation?.clinical_stagings[0]?.n,
                        compareObservation?.clinical_stagings[0]?.m,
                      )}
                    />
                  </div>
                  <div
                    className={
                      hasChanged(
                        formatStage(
                          compareObservation?.pathological_stagings[0]?.t,
                          compareObservation?.pathological_stagings[0]?.n,
                          compareObservation?.pathological_stagings[0]?.m,
                        ),
                        formatStage(
                          activeObservation?.pathological_stagings[0]?.t,
                          activeObservation?.pathological_stagings[0]?.n,
                          activeObservation?.pathological_stagings[0]?.m,
                        ),
                      )
                        ? 'compare-point compare-point-changed'
                        : 'compare-point'
                    }
                  >
                    <DataPoint
                      label="Pathological TNM"
                      value={formatStage(
                        compareObservation?.pathological_stagings[0]?.t,
                        compareObservation?.pathological_stagings[0]?.n,
                        compareObservation?.pathological_stagings[0]?.m,
                      )}
                    />
                  </div>
                  <div
                    className={
                      hasChanged(
                        compareObservation?.treatment_cycles.length,
                        activeObservation?.treatment_cycles.length,
                      )
                        ? 'compare-point compare-point-changed'
                        : 'compare-point'
                    }
                  >
                    <DataPoint
                      label="Treatment cycles"
                      value={compareObservation?.treatment_cycles.length ?? 0}
                    />
                  </div>
                  <div
                    className={
                      hasChanged(
                        compareObservation?.radiotherapy_schedules.length,
                        activeObservation?.radiotherapy_schedules.length,
                      )
                        ? 'compare-point compare-point-changed'
                        : 'compare-point'
                    }
                  >
                    <DataPoint
                      label="Radiotherapy schedules"
                      value={compareObservation?.radiotherapy_schedules.length ?? 0}
                    />
                  </div>
                  <div
                    className={
                      hasChanged(
                        compareObservation?.surgeries.length,
                        activeObservation?.surgeries.length,
                      )
                        ? 'compare-point compare-point-changed'
                        : 'compare-point'
                    }
                  >
                    <DataPoint
                      label="Surgeries"
                      value={compareObservation?.surgeries.length ?? 0}
                    />
                  </div>
                  <div
                    className={
                      hasChanged(
                        joinValues(compareObservation?.cancer_markers.map((item) => compactJoin([item.name, item.value])) ?? []),
                        joinValues(activeObservation?.cancer_markers.map((item) => compactJoin([item.name, item.value])) ?? []),
                      )
                        ? 'compare-point compare-point-changed'
                        : 'compare-point'
                    }
                  >
                    <DataPoint
                      label="Cancer markers"
                      value={joinValues(
                        compareObservation?.cancer_markers.map((item) =>
                          compactJoin([item.name, item.value, item.unit]),
                        ) ?? [],
                      )}
                    />
                  </div>
                  <div
                    className={
                      hasChanged(
                        joinValues(compareObservation?.histopathologies.map((item) => item.detail) ?? []),
                        joinValues(activeObservation?.histopathologies.map((item) => item.detail) ?? []),
                      )
                        ? 'compare-point compare-point-changed'
                        : 'compare-point'
                    }
                  >
                    <DataPoint
                      label="Histopathology"
                      value={joinValues(
                        compareObservation?.histopathologies.map((item) => item.detail) ?? [],
                      )}
                    />
                  </div>
                </div>
              </article>
            </div>
          </>
        ) : (
          <EmptyState
            title="No observations available to compare"
            detail="Once observations are available under the current filters, you can compare any two visits here."
          />
        )}
      </section>

      <section className="insight-grid">
        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Staging Progression</p>
              <h3>Clinical versus pathological stage intensity</h3>
            </div>
          </div>
          <div className="chart-box">
            {stagingTrend.length ? (
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={stagingTrend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#d5e1eb" />
                  <XAxis dataKey="label" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="clinical"
                    stroke="#0f4c81"
                    strokeWidth={3}
                    dot={{ r: 4 }}
                    name="Clinical stage score"
                  />
                  <Line
                    type="monotone"
                    dataKey="pathological"
                    stroke="#f97316"
                    strokeWidth={3}
                    dot={{ r: 4 }}
                    name="Pathological stage score"
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <EmptyState
                title="No staging trend available"
                detail="Stage progression will appear here when multiple filtered observations include staging data."
              />
            )}
          </div>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Treatment Progression</p>
              <h3>How intervention burden changes by visit</h3>
            </div>
          </div>
          <div className="chart-box">
            {treatmentTrend.length ? (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={treatmentTrend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#d5e1eb" />
                  <XAxis dataKey="label" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="cycles" fill="#0f766e" radius={[8, 8, 0, 0]} name="Cycles" />
                  <Bar dataKey="radiotherapy" fill="#0f4c81" radius={[8, 8, 0, 0]} name="Radiotherapy" />
                  <Bar dataKey="surgeries" fill="#f97316" radius={[8, 8, 0, 0]} name="Surgeries" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <EmptyState
                title="No treatment trend available"
                detail="Treatment progression will appear here when filtered observations include cycles, radiotherapy, or surgery."
              />
            )}
          </div>
        </article>
      </section>

      <section className="insight-grid">
        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Observation Rhythm</p>
              <h3>Case activity over time</h3>
            </div>
          </div>
          <div className="chart-box">
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={observationTrend}>
                <defs>
                  <linearGradient id="observationFill" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="5%" stopColor="#0f4c81" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="#0f4c81" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#d5e1eb" />
                <XAxis dataKey="label" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="count"
                  stroke="#0f4c81"
                  fill="url(#observationFill)"
                  strokeWidth={3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Treatment Footprint</p>
              <h3>Cycle, radiotherapy, and surgery volume</h3>
            </div>
          </div>
          <div className="chart-box">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={treatmentMix}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d5e1eb" />
                <XAxis dataKey="label" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" radius={[12, 12, 0, 0]}>
                  {treatmentMix.map((entry, index) => (
                    <Cell
                      key={entry.label}
                      fill={metricPalette[index % metricPalette.length]}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>
      </section>

      <section className="clinical-card-grid" aria-label="Clinical record">
        <ClinicalCard
          id="clinical-snapshot"
          eyebrow="Clinical snapshot"
          title="Selected observation"
          icon={<HeartPulse size={19} />}
          count={patient.observations.length}
          hasData={Boolean(activeObservation)}
          defaultOpen
          emptyMessage="This patient has no imported clinical observations yet."
        >
          {activeObservation ? (
          <div className="detail-grid">
            <DataPoint
              label="Observed at"
              value={formatDateTime(activeObservation.observed_at)}
            />
            <DataPoint
              label="Doctor"
              value={activeObservation.consulting_doctor_name}
            />
            <DataPoint label="Center" value={activeObservation.center_name} />
            <DataPoint label="Cancer type" value={activeObservation.cancer_type} />
            <DataPoint
              label="Disease group"
              value={activeObservation.diagnosis_disease_group}
            />
            <DataPoint
              label="Primary site"
              value={activeObservation.diagnosis_primary_site}
            />
            <DataPoint
              label="Laterality"
              value={activeObservation.diagnosis_laterality}
            />
            <DataPoint label="Grade" value={activeObservation.grade} />
          </div>
          ) : null}
        </ClinicalCard>

        <ClinicalCard
          id="demography"
          eyebrow="Demography"
          title="Core patient profile"
          icon={<UserRound size={19} />}
          count={[patient.phone, patient.date_of_birth, patient.district].filter(Boolean).length}
          hasData={Boolean(patient.phone || patient.email || patient.nid || patient.date_of_birth || patient.district)}
          emptyMessage="No demographic detail has been recorded for this patient."
        >
          <div className="detail-grid">
            <DataPoint label="Phone" value={patient.phone} />
            <DataPoint label="Email" value={patient.email} />
            <DataPoint label="NID" value={patient.nid} />
            <DataPoint label="Date of birth" value={formatDate(patient.date_of_birth)} />
            <DataPoint label="Blood group" value={patient.blood_group} />
            <DataPoint label="District" value={patient.district} />
            <DataPoint label="Area" value={patient.area} />
            <DataPoint label="Police station" value={patient.police_station} />
            <DataPoint
              label="Socio-economic status"
              value={patient.socio_economic_status}
            />
            <DataPoint label="Patient type" value={patient.patient_type} />
          </div>
        </ClinicalCard>

        <ClinicalCard
          id="history"
          eyebrow="History"
          title="Personal and family background"
          icon={<ClipboardList size={19} />}
          count={activeHistory ? 1 : 0}
          hasData={Boolean(activeHistory)}
          emptyMessage="No linked history was imported for the selected observation."
        >
          {activeHistory ? (
            <div className="detail-grid">
              <DataPoint label="Marital status" value={activeHistory.marital_status} />
              <DataPoint label="Dietary habit" value={activeHistory.dietary_habit} />
              <DataPoint label="Height" value={formatMeasure(activeHistory.height_cm, 'cm')} />
              <DataPoint label="Weight" value={formatMeasure(activeHistory.weight_kg, 'kg')} />
              <DataPoint label="BMI" value={activeHistory.bmi} />
              <DataPoint label="Alcohol history" value={activeHistory.alcohol_history} />
              <DataPoint
                label="Chest RT history"
                value={activeHistory.radiotherapy_to_chest}
              />
              <DataPoint
                label="Family cancer history"
                value={activeHistory.family_cancer_history}
              />
              <DataPoint label="Known mutation" value={activeHistory.known_mutation} />
              <DataPoint
                label="Smoking status"
                value={activeHistory.smoking_histories[0]?.status}
              />
              <DataPoint label="TB history" value={activeHistory.tb_histories[0]?.status} />
              <DataPoint
                label="Covid history"
                value={activeHistory.covid_histories[0]?.status}
              />
            </div>
          ) : null}
        </ClinicalCard>

        <ClinicalCard
          id="diagnosis"
          eyebrow="Diagnosis"
          title="Disease framing"
          icon={<Activity size={19} />}
          count={(activeObservation?.diagnoses.length ?? 0) + (activeObservation?.metastatic_sites.length ?? 0)}
          hasData={Boolean(activeObservation?.diagnosis_disease_group || activeObservation?.diagnoses.length)}
          defaultOpen
          emptyMessage="No diagnosis is available for the selected observation."
        >
          {activeObservation ? (
            <div className="stack-grid stack-grid-compact">
              <div className="badge-row badge-row-compact">
                <DataBadge label="Group" value={activeObservation.diagnosis_disease_group} />
                <DataBadge label="Subgroup" value={activeObservation.diagnosis_subgroup} />
                <DataBadge label="Site" value={activeObservation.diagnosis_primary_site} />
                <DataBadge label="Diagnosis laterality" value={activeObservation.diagnosis_laterality} />
              </div>
              <ListPanel
                title="Diagnosis details"
                items={activeObservation.diagnoses.map((item) => item.detail)}
              />
              <ListPanel
                title="Metastatic sites"
                items={activeObservation.metastatic_sites.map((item) => item.value)}
              />
              <ListPanel
                title="Comorbidities"
                items={activeObservation.comorbidities.map((item) => item.detail)}
              />
            </div>
          ) : null}
        </ClinicalCard>

        <ClinicalCard
          id="staging"
          eyebrow="Staging"
          title="Clinical and pathological status"
          icon={<ClipboardList size={19} />}
          count={(activeClinicalStage ? 1 : 0) + (activePathologicalStage ? 1 : 0)}
          hasData={Boolean(activeClinicalStage || activePathologicalStage || activePathologicalDetail)}
          emptyMessage="No staging record is attached to this observation."
        >
          {activeObservation ? (
            <div className="detail-grid detail-grid-compact">
              <DataPoint
                label="Clinical TNM"
                value={formatStage(
                  activeClinicalStage?.t,
                  activeClinicalStage?.n,
                  activeClinicalStage?.m,
                )}
              />
              <DataPoint label="Clinical result" value={activeClinicalStage?.result} />
              <DataPoint
                label="Pathological TNM"
                value={formatStage(
                  activePathologicalStage?.t,
                  activePathologicalStage?.n,
                  activePathologicalStage?.m,
                )}
              />
              <DataPoint
                label="Pathological result"
                value={activePathologicalStage?.result}
              />
              <DataPoint label="LVSI" value={activePathologicalDetail?.lvsi} />
              <DataPoint label="PNI" value={activePathologicalDetail?.pni} />
              <DataPoint label="Margin" value={activePathologicalDetail?.margin} />
              <DataPoint label="Ki67" value={activePathologicalDetail?.ki67} />
            </div>
          ) : null}
        </ClinicalCard>

        <ClinicalCard
          id="pathology"
          eyebrow="Pathology"
          title="Histopathology and molecular workup"
          icon={<Dna size={19} />}
          count={(activeObservation?.histopathologies.length ?? 0) + (activeIhcPanel?.details.length ?? 0)}
          hasData={Boolean(activeObservation?.histopathologies.length || activeIhcPanel?.details.length)}
          emptyMessage="No pathology workup is available for this observation."
        >
          {activeObservation ? (
            <div className="stack-grid stack-grid-compact">
              <ListPanel
                title="Histopathology"
                items={activeObservation.histopathologies.map((item) =>
                  compactJoin([
                    item.detail,
                    item.site,
                    item.histology_type,
                    item.observed_on ? `Date: ${formatDate(item.observed_on)}` : null,
                  ]),
                )}
              />
              <ListPanel
                title="IHC panel"
                items={
                  activeIhcPanel?.details.map((item) =>
                    compactJoin([item.marker_type, item.value]),
                  ) ?? []
                }
              />
            </div>
          ) : null}
        </ClinicalCard>

        <ClinicalCard
          id="molecular-pathology"
          eyebrow="Molecular pathology"
          title="Gene and biomarker profile"
          icon={<Dna size={19} />}
          count={activeObservation?.molecular_pathologies.length ?? 0}
          hasData={Boolean(activeObservation?.molecular_pathologies.length || molecularProfile.length)}
          emptyMessage="No molecular pathology result is available for this observation."
        >
          <div className="stack-grid stack-grid-compact">
            <ListPanel
              title="Selected observation results"
              items={
                activeObservation?.molecular_pathologies.map((item) =>
                  compactJoin([
                    item.method,
                    item.gene,
                    item.exon,
                    item.specimen,
                    item.status,
                    item.observed_on ? `Date: ${formatDate(item.observed_on)}` : null,
                  ]),
                ) ?? []
              }
            />
            {molecularProfile.length ? (
              <div className="molecular-chart">
                <p className="list-panel-title">Recorded molecular activity</p>
                <ResponsiveContainer width="100%" height={210}>
                  <BarChart data={molecularProfile} margin={{ top: 8, right: 8, left: -18, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.22} />
                    <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                    <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Bar dataKey="value" name="Records" fill="#16c7b0" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : null}
          </div>
        </ClinicalCard>

        <ClinicalCard
          id="treatment"
          eyebrow="Treatment"
          title="Treatment footprint"
          icon={<HeartPulse size={19} />}
          count={(activeObservation?.treatment_cycles.length ?? 0) + (activeObservation?.radiotherapy_schedules.length ?? 0) + (activeObservation?.surgeries.length ?? 0)}
          hasData={Boolean(activeObservation?.treatment_cycles.length || activeObservation?.radiotherapy_schedules.length || activeObservation?.surgeries.length)}
          emptyMessage="No treatment records are available for this observation."
        >
          {activeObservation ? (
            <div className="stack-grid stack-grid-compact">
              <ListPanel
                title="Treatment cycles"
                items={activeObservation.treatment_cycles.map((cycle) => {
                  const protocolCycle = cycle.chemotherapy_protocols
                    .map((protocol) => protocol.cycle_no)
                    .find((value) => value !== null && value !== undefined)
                  const cycleNumber = protocolCycle ?? cycle.chemo_cycle_no
                  return compactJoin([
                    joinValues(cycle.chemotherapy_modalities.map((modality) => modality.detail)),
                    cycle.current_chemo_protocol,
                    cycleNumber !== null && cycleNumber !== undefined && cycleNumber !== ''
                      ? `Cycle ${String(cycleNumber).replace(/\.00$/, '')}`
                      : null,
                    cycle.line_of_treatment,
                    cycle.chemo_starting_date ? `Started ${formatDate(cycle.chemo_starting_date)}` : null,
                  ])
                })}
              />
              <ListPanel
                title="Radiotherapy schedules"
                items={activeObservation.radiotherapy_schedules.map((schedule) =>
                  compactJoin([
                    joinValues(schedule.sites.map((item) => item.value)),
                    joinValues(schedule.modalities.map((item) => item.value)),
                    schedule.intent,
                    schedule.total_dose ? `${schedule.total_dose} cGy` : null,
                  ]),
                )}
              />
              <ListPanel
                title="Surgeries"
                items={activeObservation.surgeries.map((surgery) =>
                  compactJoin([
                    surgery.modality,
                    formatDate(surgery.surgery_date),
                    joinValues(surgery.lateralities.map((item) => item.value)),
                  ]),
                )}
              />
            </div>
          ) : null}
        </ClinicalCard>
      </section>

      <section className="panel" id="marker-trend">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Marker Trend</p>
            <h3>Cancer marker values across observations</h3>
          </div>
        </div>
        <div className="chart-box">
          {markerSeries.length ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={markerSeries}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d5e1eb" />
                <XAxis dataKey="label" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#f97316"
                  strokeWidth={3}
                  dot={{ r: 4 }}
                  name="Marker value"
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState
              title="No marker series available"
              detail="As more canonical observations arrive, marker trend lines will become available here."
            />
          )}
        </div>
      </section>

      <section className="panel panel-compact" id="observation-timeline">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Observation Timeline</p>
            <h3>Filtered observations</h3>
          </div>
        </div>
        <div className="timeline-list timeline-list-compact">
          {filteredObservations.map((observation) => (
            <article key={observation.id} className="timeline-card timeline-card-compact">
              <div className="timeline-head">
                <div>
                  <p className="timeline-title">
                    {observation.diagnosis_disease_group ||
                      observation.cancer_type ||
                      'Clinical observation'}
                  </p>
                  <p className="timeline-subtitle">
                    {formatDateTime(observation.observed_at)}
                    {observation.center_name ? ` | ${observation.center_name}` : ''}
                  </p>
                </div>
                <span
                  className={
                    observation.is_draft
                      ? 'status-pill status-draft'
                      : 'status-pill status-live'
                  }
                >
                  {observation.is_draft ? 'Draft' : 'Published'}
                </span>
              </div>
              <div className="timeline-grid timeline-grid-compact">
                <DataPoint
                  label="Primary site"
                  value={observation.diagnosis_primary_site}
                />
                <DataPoint
                  label="Diagnosis laterality"
                  value={observation.diagnosis_laterality}
                />
                <DataPoint
                  label="Subgroup"
                  value={observation.diagnosis_subgroup}
                />
                <DataPoint
                  label="Metastatic sites"
                  value={joinValues(
                    observation.metastatic_sites.map((item) => item.value),
                  )}
                />
                <DataPoint
                  label="Comorbidities"
                  value={joinValues(
                    observation.comorbidities.map((item) => item.detail),
                  )}
                />
                <DataPoint
                  label="Histopathology"
                  value={joinValues(
                    observation.histopathologies.map((item) => item.detail),
                  )}
                />
                <DataPoint
                  label="Histopathology date"
                  value={joinValues(
                    observation.histopathologies.map((item) =>
                      item.observed_on ? formatDate(item.observed_on) : null,
                    ),
                  )}
                />
                <DataPoint
                  label="Molecular pathology"
                  value={joinValues(
                    observation.molecular_pathologies.map(
                      (item) => item.status || item.gene,
                    ),
                  )}
                />
                <DataPoint
                  label="Molecular pathology date"
                  value={joinValues(
                    observation.molecular_pathologies.map((item) =>
                      item.observed_on ? formatDate(item.observed_on) : null,
                    ),
                  )}
                />
              </div>
              <div className="timeline-actions">
                {patient.can_edit && observation.can_edit ? (
                  <Link
                    className="secondary-button"
                    to={`/patients/${patient.registry_id}/edit`}
                  >
                    Edit
                  </Link>
                ) : null}
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() =>
                    focusObservation(
                      filteredObservations.findIndex((item) => item.id === observation.id),
                    )
                  }
                >
                  Focus
                </button>
              </div>
            </article>
          ))}
        </div>
      </section>
    </section>
  )
}
