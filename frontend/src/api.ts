export interface DashboardSummary {
  patients: number
  observations: number
  published_patients: number
  draft_patients: number
  published_observations: number
  draft_observations: number
}

export interface PatientDemographicsLookup {
  genders: string[]
  blood_groups: string[]
  districts: string[]
  police_stations: string[]
  socio_economic_statuses: string[]
  patient_types: string[]
  marital_statuses: string[]
  alcohol_history_options: string[]
  smoking_statuses: string[]
  tb_statuses: string[]
  covid_statuses: string[]
  covid_vaccine_names: string[]
  covid_vaccination_doses: string[]
  diagnosis_disease_groups: string[]
  diagnosis_disease_subgroups: string[]
  diagnosis_primary_sites: string[]
  diagnosis_lateralities: string[]
  diagnosis_metastatic_sites: string[]
  histopathology_details: string[]
  histopathology_types: string[]
  ihc_marker_types: string[]
  molecular_pathology_options: Record<string, string[]>
}

export interface AuthUser {
  id: number
  username: string
  full_name: string
  email: string
  role: 'admin' | 'doctor' | 'user'
  default_redirect: string
  is_staff: boolean
  is_superuser: boolean
}

export interface PatientListResponse {
  count: number
  next: string | null
  previous: string | null
  results: Patient[]
}

export interface LegacyUnlinkedHistory {
  legacy_history_id: number
  missing_observation_id: number
  marital_status: string
  first_diagnosis_date: string | null
  created_at: string | null
  updated_at: string | null
  resolution_status: 'open' | 'reviewed' | 'resolved'
}

export interface LegacyUnlinkedHistoryResponse {
  count: number
  page: number
  per_page: number
  next: number | null
  previous: number | null
  results: LegacyUnlinkedHistory[]
}

export interface Patient {
  id: number
  legacy_id: number | null
  registry_id: string
  legacy_unique_id: string | null
  registration_no: string | null
  name: string
  phone: string | null
  age: number | null
  gender: string | null
  district: string | null
  socio_economic_status: string | null
  observation_count: number
  latest_observation: ClinicalObservationSummary | null
  can_edit: boolean
}

export interface PatientDetail {
  id: number
  legacy_id: number | null
  registry_id: string
  legacy_unique_id: string | null
  registration_no: string | null
  name: string
  phone: string | null
  email: string | null
  nid: string | null
  date_of_birth: string | null
  age: number | null
  gender: string | null
  blood_group: string | null
  area: string | null
  police_station: string | null
  district: string | null
  socio_economic_status: string | null
  passport: string | null
  patient_type: string | null
  is_draft: boolean
  can_edit: boolean
  observations: ClinicalObservation[]
}

export interface ClinicalObservationSummary {
  id: number
  legacy_id: number | null
  registration_no: string | null
  observed_at: string | null
  consulting_doctor_name: string | null
  center_name: string | null
  cancer_type: string | null
  diagnosis_disease_group: string | null
  diagnosis_subgroup: string | null
  diagnosis_primary_site: string | null
  diagnosis_laterality: string | null
  grade: string | null
  is_draft: boolean
  can_edit: boolean
}

export interface ClinicalObservation extends ClinicalObservationSummary {
  history: PatientHistory | null
  diagnoses: Diagnosis[]
  metastatic_sites: ValueItem[]
  comorbidities: DetailItem[]
  histopathologies: Histopathology[]
  molecular_pathologies: MolecularPathology[]
  cancer_markers: CancerMarker[]
  clinical_stagings: Staging[]
  pathological_stagings: Staging[]
  pathological_staging_details: PathologicalStagingDetail[]
  ihc_panels: IHCPanel[]
  treatment_cycles: TreatmentCycle[]
  past_treatment_histories: PastTreatmentHistory[]
  radiotherapy_schedules: RadiotherapySchedule[]
  surgeries: Surgery[]
}

export interface PatientHistory {
  id: number
  marital_status: string | null
  dietary_habit: string | null
  height_cm: number | null
  weight_kg: number | null
  bmi: number | null
  alcohol_history: string | null
  radiotherapy_to_chest: string | null
  family_cancer_history: string | null
  known_mutation: string | null
  first_diagnosis_date: string | null
  smoking_histories: SmokingHistory[]
  tb_histories: TuberculosisHistory[]
  covid_histories: CovidHistory[]
}

export interface SmokingHistory {
  id: number
  status: string | null
  cigarettes_per_day: number | null
  duration_years: number | null
  pack_years: number | null
  quit_period_years: number | null
}

export interface TuberculosisHistory {
  id: number
  status: string | null
  date: string | null
  treatment: string | null
}

export interface CovidHistory {
  id: number
  status: string | null
  date: string | null
  vaccine_name: string | null
  vaccination_dose: string | null
}

export interface Diagnosis {
  id: number
  detail: string | null
}

export interface ValueItem {
  id: number
  value: string | null
}

export interface DetailItem {
  id: number
  detail: string | null
}

export interface Histopathology {
  id: number
  detail: string | null
  site: string | null
  histology_type: string | null
  observed_on: string | null
}

export interface MolecularPathology {
  id: number
  specimen: string | null
  method: string | null
  gene: string | null
  exon: string | null
  status: string | null
  observed_on: string | null
}

export interface CancerMarker {
  id: number
  name: string | null
  value: string | null
  unit: string | null
  observed_on: string | null
}

export interface Staging {
  id: number
  t: string | null
  n: string | null
  m: string | null
  result: string | null
  staged_on: string | null
}

export interface PathologicalStagingDetail {
  id: number
  lvsi: string | null
  pni: string | null
  margin: string | null
  ki67: string | null
  staged_on: string | null
}

export interface IHCDetail {
  id: number
  marker_type: string | null
  value: string | null
}

export interface IHCPanel {
  id: number
  observed_on: string | null
  details: IHCDetail[]
}

export interface TreatmentCycle {
  id: number
  current_chemo_protocol: string | null
  chemo_cycle_no: string | null
  chemo_detail: string | null
  chemo_starting_date: string | null
  chemo_end_date: string | null
  line_of_treatment: string | null
  disease_progression_status: string | null
  disease_progression_status_date: string | null
  survival_status: string | null
  survival_status_date: string | null
  recist_1_target_lesion: string | null
  recist_1_non_target_lesion: string | null
  recist_1_new_lesion: string | null
  recist_1_result: string | null
  recist_1_date: string | null
  recist_1_method_of_estimation: string | null
  irecist_target_lesion: string | null
  irecist_non_target_lesion: string | null
  irecist_new_lesion: string | null
  irecist_result: string | null
  irecist_date: string | null
  irecist_method_of_estimation: string | null
  pathological_response_rate_target_lesion: string | null
  pathological_response_rate_non_target_lesion: string | null
  pathological_response_rate_new_lesion: string | null
  pathological_response_rate_result: string | null
  pathological_response_rate_date: string | null
  pathological_method_of_estimation: string | null
  progression_free_survival: string | null
  overall_survival: string | null
  chemotherapy_protocols: ChemotherapyProtocol[]
  chemotherapy_modalities: ChemotherapyModality[]
}

export interface ChemotherapyProtocol {
  id: number
  cycle_no: string | number | null
  protocol_type: string | null
}

export interface ChemotherapyModality {
  id: number
  detail: string | null
}

export interface PastTreatmentHistory {
  id: number
  detail: string | null
  date: string | null
}

export interface RadiotherapySchedule {
  id: number
  start_date: string | null
  end_date: string | null
  intent: string | null
  fraction: string | null
  fraction_number: string | null
  total_dose: string | null
  sites: ValueItem[]
  modalities: ValueItem[]
}

export interface Surgery {
  id: number
  surgery_date: string | null
  modality: string | null
  lateralities: ValueItem[]
}

export interface PatientEntryPayload {
  observation_id?: number
  registry_id?: string
  legacy_unique_id?: string
  registration_no?: string
  name: string
  phone?: string
  email?: string
  nid?: string
  date_of_birth?: string | null
  age?: number | null
  gender?: string
  blood_group?: string
  area?: string
  police_station?: string
  district?: string
  socio_economic_status?: string
  passport?: string
  patient_type?: string
  patient_is_draft?: boolean
  observed_at?: string | null
  consulting_doctor_name?: string
  center_name?: string
  cancer_type?: string
  diagnosis_disease_group?: string
  diagnosis_subgroup?: string
  diagnosis_primary_site?: string
  diagnosis_laterality?: string
  grade?: string
  laterality_notes?: string
  observation_is_draft?: boolean
  history?: {
    marital_status?: string
    dietary_habit?: string
    height_cm?: string | number | null
    weight_kg?: string | number | null
    bmi?: string | number | null
    alcohol_history?: string
    radiotherapy_to_chest?: string
    family_cancer_history?: string
    known_mutation?: string
    first_diagnosis_date?: string | null
  }
  smoking_histories?: Array<{
    status?: string
    cigarettes_per_day?: number | null
    duration_years?: string | number | null
    pack_years?: string | number | null
    quit_period_years?: string | number | null
  }>
  tb_histories?: Array<{
    status?: string
    date?: string | null
    treatment?: string
  }>
  covid_histories?: Array<{
    status?: string
    date?: string | null
    vaccine_name?: string
    vaccination_dose?: string
  }>
  diagnoses?: string[]
  metastatic_sites?: string[]
  comorbidities?: string[]
  histopathologies?: Array<{
    detail?: string
    site?: string
    histology_type?: string
    observed_on?: string | null
  }>
  molecular_pathologies?: Array<{
    specimen?: string
    method?: string
    gene?: string
    exon?: string
    status?: string
    observed_on?: string | null
  }>
  cancer_markers?: Array<{
    name: string
    value: string
    unit?: string
    observed_on: string
  }>
  clinical_staging?: {
    t?: string
    n?: string
    m?: string
    result?: string
    staged_on?: string | null
  }
  pathological_staging?: {
    t?: string
    n?: string
    m?: string
    result?: string
    staged_on?: string | null
  }
  pathological_staging_detail?: {
    lvsi?: string
    pni?: string
    margin?: string
    ki67?: string
    staged_on?: string | null
  }
  ihc_panels?: Array<{
    observed_on?: string | null
    details?: Array<{
      marker_type?: string
      value?: string
    }>
  }>
  treatment_cycles?: Array<{
    current_chemo_protocol?: string
    chemo_cycle_no?: string
    chemo_detail?: string
    chemo_starting_date?: string | null
    chemo_end_date?: string | null
    line_of_treatment?: string
    disease_progression_status?: string
    disease_progression_status_date?: string | null
    survival_status?: string
    survival_status_date?: string | null
  }>
  past_treatment_histories?: Array<{
    detail?: string
    date?: string | null
  }>
  radiotherapy_schedules?: Array<{
    start_date?: string | null
    end_date?: string | null
    intent?: string
    fraction?: string
    fraction_number?: string
    total_dose?: string
    sites?: string[]
    modalities?: string[]
  }>
  surgeries?: Array<{
    surgery_date: string
    modality?: string
    lateralities?: string[]
  }>
}

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

function getCookie(name: string) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) {
    return parts.pop()?.split(';').shift() ?? ''
  }
  return ''
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers ?? {})
  const method = (init?.method ?? 'GET').toUpperCase()
  if (!headers.has('Accept')) {
    headers.set('Accept', 'application/json')
  }
  if (init?.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  if (method !== 'GET' && method !== 'HEAD' && !headers.has('X-CSRFToken')) {
    const csrfToken = getCookie('csrftoken')
    if (csrfToken) {
      headers.set('X-CSRFToken', csrfToken)
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    credentials: 'include',
    headers,
  })

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`
    const contentType = response.headers.get('content-type') ?? ''
    if (contentType.includes('application/json')) {
      const payload = (await response.json()) as { detail?: string }
      if (payload.detail) {
        message = payload.detail
      }
    }
    throw new ApiError(message, response.status)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

export function fetchCsrfToken() {
  return request<{ detail: string }>('/api/auth/csrf/')
}

export function fetchCurrentUser() {
  return request<{ user: AuthUser }>('/api/auth/me/').then((payload) => payload.user)
}

export async function loginUser(
  username: string,
  password: string,
  role: 'admin' | 'doctor' | 'user',
) {
  await fetchCsrfToken()
  return request<{ user: AuthUser }>('/api/auth/login/', {
    method: 'POST',
    body: JSON.stringify({ username, password, role }),
  }).then((payload) => payload.user)
}

export async function logoutUser() {
  await fetchCsrfToken()
  return request<void>('/api/auth/logout/', {
    method: 'POST',
  })
}

export function fetchDashboardSummary() {
  return request<DashboardSummary>('/api/dashboard/summary/')
}

export function fetchPatientDemographics(district = '', diseaseGroup = '') {
  const params = new URLSearchParams()
  if (district) {
    params.set('district', district)
  }
  if (diseaseGroup) {
    params.set('disease_group', diseaseGroup)
  }
  const query = params.toString()
  return request<PatientDemographicsLookup>(
    `/api/patients/demographics/${query ? `?${query}` : ''}`,
  )
}

export function fetchPatients(
  query: string,
  page = 1,
  perPage = 24,
  state = 'all',
  sort = 'name',
  direction = 'asc',
) {
  const params = new URLSearchParams()
  params.set('page', String(page))
  params.set('per_page', String(perPage))
  if (query) {
    params.set('q', query)
  }
  if (state !== 'all') {
    params.set('state', state)
  }
  params.set('sort', sort)
  params.set('dir', direction)

  return request<PatientListResponse>(`/api/patients/?${params.toString()}`)
}

export function fetchPatientDetail(registryId: string) {
  return request<PatientDetail>(`/api/patients/${registryId}/`)
}

export function fetchLegacyUnlinkedHistories(query = '', page = 1, status = 'open') {
  const params = new URLSearchParams({ page: String(page), per_page: '25', status })
  if (query) {
    params.set('q', query)
  }
  return request<LegacyUnlinkedHistoryResponse>(
    `/api/legacy-review/unlinked-histories/?${params.toString()}`,
  )
}

export function createPatientEntry(payload: PatientEntryPayload) {
  return request<{ id: number; registry_id: string; name: string }>('/api/patients/create/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updatePatientEntry(registryId: string, payload: PatientEntryPayload) {
  return request<{ id: number; registry_id: string; name: string }>(
    `/api/patients/${registryId}/update/`,
    {
      method: 'PATCH',
      body: JSON.stringify(payload),
    },
  )
}

export function buildPatientExportUrl(
  query: string,
  state = 'all',
  sort = 'name',
  direction = 'asc',
) {
  const params = new URLSearchParams()
  if (query) {
    params.set('q', query)
  }
  if (state !== 'all') {
    params.set('state', state)
  }
  params.set('sort', sort)
  params.set('dir', direction)

  return `${API_BASE_URL}/api/patients/export/?${params.toString()}`
}
