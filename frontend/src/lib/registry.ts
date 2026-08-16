import type { ClinicalObservation } from '../api'

export const metricPalette = ['#0f4c81', '#f97316', '#0ea5a4', '#164e63']

export function buildObservationTrend(observations: ClinicalObservation[]) {
  const map = new Map<string, number>()

  observations.forEach((observation) => {
    const key = observation.observed_at
      ? new Date(observation.observed_at).getFullYear().toString()
      : 'Unknown'
    map.set(key, (map.get(key) ?? 0) + 1)
  })

  return [...map.entries()].map(([label, count]) => ({ label, count }))
}

export function buildTreatmentMix(observations: ClinicalObservation[]) {
  const cycles = observations.reduce(
    (sum, observation) => sum + observation.treatment_cycles.length,
    0,
  )
  const radiotherapy = observations.reduce(
    (sum, observation) => sum + observation.radiotherapy_schedules.length,
    0,
  )
  const surgeries = observations.reduce(
    (sum, observation) => sum + observation.surgeries.length,
    0,
  )

  return [
    { label: 'Treatment cycles', value: cycles },
    { label: 'Radiotherapy', value: radiotherapy },
    { label: 'Surgeries', value: surgeries },
  ]
}

export function buildMarkerSeries(observations: ClinicalObservation[]) {
  const points = observations
    .flatMap((observation) =>
      observation.cancer_markers.map((marker) => ({
        label: marker.observed_on
          ? formatDate(marker.observed_on)
          : formatDateTime(observation.observed_at),
        value: Number(marker.value),
      })),
    )
    .filter((point) => Number.isFinite(point.value))

  return points
}

export function joinValues(values: Array<string | null | undefined>) {
  const cleanValues = values.filter(Boolean)
  return cleanValues.length ? cleanValues.join(', ') : 'N/A'
}

export function compactJoin(values: Array<string | null | undefined>) {
  const cleanValues = values.filter(Boolean)
  return cleanValues.length ? cleanValues.join(' | ') : null
}

export function formatMeasure(value?: string | number | null, unit?: string) {
  if (value === null || value === undefined || value === '') {
    return 'N/A'
  }

  return unit ? `${value} ${unit}` : String(value)
}

export function formatStage(
  t?: string | null,
  n?: string | null,
  m?: string | null,
) {
  const parts = [t, n, m].filter(Boolean)
  return parts.length ? parts.join(' / ') : 'N/A'
}

export function formatDate(value?: string | null) {
  if (!value) {
    return 'N/A'
  }

  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(new Date(value))
}

export function formatDateTime(value?: string | null) {
  if (!value) {
    return 'N/A'
  }

  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(new Date(value))
}
