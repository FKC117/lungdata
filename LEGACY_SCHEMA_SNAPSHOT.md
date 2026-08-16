# Legacy Schema Snapshot

Schema: `lung_local`

Table count: `75`

## `auth_group`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `int` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(150)` | `NO` | `UNI` | `` |

### Foreign Keys

- None

## `auth_group_permissions`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint` | `NO` | `PRI` | `auto_increment` |
| `group_id` | `int` | `NO` | `MUL` | `` |
| `permission_id` | `int` | `NO` | `MUL` | `` |

### Foreign Keys

- `group_id` -> `auth_group.id`
- `permission_id` -> `auth_permission.id`

## `auth_permission`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `int` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(255)` | `NO` | `` | `` |
| `content_type_id` | `int` | `NO` | `MUL` | `` |
| `codename` | `varchar(100)` | `NO` | `` | `` |

### Foreign Keys

- `content_type_id` -> `django_content_type.id`

## `auth_user`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `int` | `NO` | `PRI` | `auto_increment` |
| `password` | `varchar(128)` | `NO` | `` | `` |
| `last_login` | `datetime(6)` | `YES` | `` | `` |
| `is_superuser` | `tinyint(1)` | `NO` | `` | `` |
| `username` | `varchar(150)` | `NO` | `UNI` | `` |
| `first_name` | `varchar(150)` | `NO` | `` | `` |
| `last_name` | `varchar(150)` | `NO` | `` | `` |
| `email` | `varchar(254)` | `NO` | `` | `` |
| `is_staff` | `tinyint(1)` | `NO` | `` | `` |
| `is_active` | `tinyint(1)` | `NO` | `` | `` |
| `date_joined` | `datetime(6)` | `NO` | `` | `` |

### Foreign Keys

- None

## `auth_user_groups`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint` | `NO` | `PRI` | `auto_increment` |
| `user_id` | `int` | `NO` | `MUL` | `` |
| `group_id` | `int` | `NO` | `MUL` | `` |

### Foreign Keys

- `group_id` -> `auth_group.id`
- `user_id` -> `auth_user.id`

## `auth_user_user_permissions`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint` | `NO` | `PRI` | `auto_increment` |
| `user_id` | `int` | `NO` | `MUL` | `` |
| `permission_id` | `int` | `NO` | `MUL` | `` |

### Foreign Keys

- `permission_id` -> `auth_permission.id`
- `user_id` -> `auth_user.id`

## `cancer_marker_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `unit` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `cancer_markers`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_observation_id` | `bigint unsigned` | `NO` | `` | `` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `value` | `varchar(191)` | `NO` | `` | `` |
| `unit` | `varchar(191)` | `NO` | `` | `` |
| `date` | `date` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `centers`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `chemotherapy_modalities`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_observation_detail_id` | `bigint unsigned` | `NO` | `` | `` |
| `detail` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `chemotherapy_modality_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `chemotherapy_protocol_details`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `chemotherapy_protocol_id` | `bigint unsigned` | `NO` | `` | `` |
| `value` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `chemotherapy_protocol_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `chemotherapy_protocols`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_observation_detail_id` | `bigint unsigned` | `NO` | `` | `` |
| `cycle_no` | `double(8,2)` | `YES` | `` | `` |
| `type` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `comorbidities`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_observation_id` | `bigint unsigned` | `NO` | `` | `` |
| `detail` | `text` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `comorbidity_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `covid_histories`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_history_id` | `bigint unsigned` | `NO` | `` | `` |
| `status` | `varchar(191)` | `NO` | `` | `` |
| `date` | `date` | `YES` | `` | `` |
| `vaccine_name` | `varchar(191)` | `YES` | `` | `` |
| `vaccination_dose` | `varchar(191)` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `covid_vaccine_company_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `diagnoses`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_observation_id` | `bigint unsigned` | `NO` | `` | `` |
| `detail` | `text` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `diagnosis_disease_group_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `diagnosis_disease_subgroup_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `diagnosis_disease_group_record_id` | `bigint unsigned` | `NO` | `` | `` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `diagnosis_laterility_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `diagnosis_metastatic_site_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `diagnosis_metastatic_sites`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_observation_id` | `bigint unsigned` | `NO` | `` | `` |
| `value` | `varchar(191)` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `diagnosis_primary_site_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `disease_progression_status_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `django_admin_log`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `int` | `NO` | `PRI` | `auto_increment` |
| `action_time` | `datetime(6)` | `NO` | `` | `` |
| `object_id` | `longtext` | `YES` | `` | `` |
| `object_repr` | `varchar(200)` | `NO` | `` | `` |
| `action_flag` | `smallint unsigned` | `NO` | `` | `` |
| `change_message` | `longtext` | `NO` | `` | `` |
| `content_type_id` | `int` | `YES` | `MUL` | `` |
| `user_id` | `int` | `NO` | `MUL` | `` |

### Foreign Keys

- `content_type_id` -> `django_content_type.id`
- `user_id` -> `auth_user.id`

## `django_content_type`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `int` | `NO` | `PRI` | `auto_increment` |
| `app_label` | `varchar(100)` | `NO` | `MUL` | `` |
| `model` | `varchar(100)` | `NO` | `` | `` |

### Foreign Keys

- None

## `django_migrations`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint` | `NO` | `PRI` | `auto_increment` |
| `app` | `varchar(255)` | `NO` | `` | `` |
| `name` | `varchar(255)` | `NO` | `` | `` |
| `applied` | `datetime(6)` | `NO` | `` | `` |

### Foreign Keys

- None

## `django_session`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `session_key` | `varchar(40)` | `NO` | `PRI` | `` |
| `session_data` | `longtext` | `NO` | `` | `` |
| `expire_date` | `datetime(6)` | `NO` | `MUL` | `` |

### Foreign Keys

- None

## `doctor_degrees`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `doctor_id` | `bigint unsigned` | `NO` | `` | `` |
| `degree` | `varchar(50)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `doctor_patients`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `doctor_id` | `bigint unsigned` | `NO` | `MUL` | `` |
| `patient_id` | `bigint unsigned` | `NO` | `MUL` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `doctor_recognition_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `group` | `varchar(191)` | `NO` | `` | `` |
| `value` | `varchar(191)` | `NO` | `` | `` |

### Foreign Keys

- None

## `doctors`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `phone` | `varchar(20)` | `YES` | `` | `` |
| `email` | `varchar(191)` | `NO` | `` | `` |
| `date_of_birth` | `date` | `YES` | `` | `` |
| `designation` | `varchar(50)` | `YES` | `` | `` |
| `department` | `varchar(50)` | `YES` | `` | `` |
| `institution` | `varchar(255)` | `YES` | `` | `` |
| `bmdc_number` | `varchar(10)` | `YES` | `` | `` |
| `photo` | `varchar(55)` | `YES` | `` | `` |
| `center_id` | `bigint unsigned` | `NO` | `MUL` | `` |
| `password` | `text` | `NO` | `` | `` |
| `status` | `varchar(10)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `exon_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `molecular_pathology_record_id` | `bigint unsigned` | `NO` | `` | `` |
| `value` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `failed_jobs`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `uuid` | `varchar(191)` | `NO` | `UNI` | `` |
| `connection` | `text` | `NO` | `` | `` |
| `queue` | `text` | `NO` | `` | `` |
| `payload` | `longtext` | `NO` | `` | `` |
| `exception` | `longtext` | `NO` | `` | `` |
| `failed_at` | `timestamp` | `NO` | `` | `DEFAULT_GENERATED` |

### Foreign Keys

- None

## `histopathologies`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_observation_id` | `bigint unsigned` | `NO` | `` | `` |
| `detail` | `text` | `YES` | `` | `` |
| `site` | `text` | `YES` | `` | `` |
| `type` | `text` | `YES` | `` | `` |
| `date` | `date` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `histopathology_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `type` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `ihc_details`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `ihc_id` | `bigint unsigned` | `NO` | `` | `` |
| `type` | `varchar(191)` | `NO` | `` | `` |
| `value` | `varchar(191)` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `ihc_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `ihcs`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_observation_id` | `bigint unsigned` | `NO` | `` | `` |
| `date` | `date` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `line_of_treatment_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `migrations`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `int unsigned` | `NO` | `PRI` | `auto_increment` |
| `migration` | `varchar(191)` | `NO` | `` | `` |
| `batch` | `int` | `NO` | `` | `` |

### Foreign Keys

- None

## `molecular_pathologies`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_observation_id` | `bigint unsigned` | `NO` | `` | `` |
| `specimen` | `varchar(191)` | `YES` | `` | `` |
| `method` | `varchar(191)` | `YES` | `` | `` |
| `gene` | `varchar(191)` | `YES` | `` | `` |
| `exon` | `varchar(191)` | `YES` | `` | `` |
| `status` | `varchar(191)` | `YES` | `` | `` |
| `date` | `date` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `molecular_pathology_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `group` | `varchar(191)` | `NO` | `` | `` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `password_resets`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `email` | `varchar(191)` | `NO` | `MUL` | `` |
| `token` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `past_treatment_histories`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_observation_id` | `bigint unsigned` | `NO` | `` | `` |
| `detail` | `text` | `YES` | `` | `` |
| `date` | `date` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `patient_histories`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_observation_id` | `bigint unsigned` | `NO` | `` | `` |
| `marital_status` | `varchar(10)` | `YES` | `` | `` |
| `dietary_habit` | `varchar(191)` | `YES` | `` | `` |
| `height` | `double` | `YES` | `` | `` |
| `weight` | `double` | `YES` | `` | `` |
| `bmi` | `double` | `YES` | `` | `` |
| `h_o_alcoholism` | `varchar(191)` | `YES` | `` | `` |
| `rt_to_chest` | `varchar(191)` | `YES` | `` | `` |
| `cancer_history` | `varchar(191)` | `YES` | `` | `` |
| `known_mutation` | `varchar(191)` | `YES` | `` | `` |
| `first_diagnosis_date` | `date` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `patient_observation_details`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_observation_id` | `bigint unsigned` | `NO` | `` | `` |
| `current_chemo_protocol` | `text` | `YES` | `` | `` |
| `chemo_cycle_no` | `text` | `YES` | `` | `` |
| `chemo_detail` | `text` | `YES` | `` | `` |
| `chemo_starting_date` | `date` | `YES` | `` | `` |
| `chemo_end_date` | `date` | `YES` | `` | `` |
| `line_of_treatment` | `varchar(191)` | `YES` | `` | `` |
| `disease_progression_status` | `varchar(191)` | `YES` | `` | `` |
| `disease_progression_status_date` | `date` | `YES` | `` | `` |
| `survival_status` | `varchar(191)` | `YES` | `` | `` |
| `survival_status_date` | `date` | `YES` | `` | `` |
| `recist_1_target_lasion` | `varchar(191)` | `YES` | `` | `` |
| `recist_1_non_target_lasion` | `varchar(191)` | `YES` | `` | `` |
| `recist_1_new_lasion` | `varchar(191)` | `YES` | `` | `` |
| `recist_1_result` | `varchar(191)` | `YES` | `` | `` |
| `recist_1_date` | `date` | `YES` | `` | `` |
| `recist_1_method_of_estimation` | `varchar(191)` | `YES` | `` | `` |
| `irecist_target_lasion` | `varchar(191)` | `YES` | `` | `` |
| `irecist_non_target_lasion` | `varchar(191)` | `YES` | `` | `` |
| `irecist_new_lasion` | `varchar(191)` | `YES` | `` | `` |
| `irecist_result` | `varchar(191)` | `YES` | `` | `` |
| `irecist_date` | `date` | `YES` | `` | `` |
| `irecist_method_of_estimation` | `varchar(191)` | `YES` | `` | `` |
| `pathological_response_rate_target_lasion` | `varchar(191)` | `YES` | `` | `` |
| `pathological_response_rate_non_target_lasion` | `varchar(191)` | `YES` | `` | `` |
| `pathological_response_rate_new_lasion` | `varchar(191)` | `YES` | `` | `` |
| `pathological_response_rate_result` | `varchar(191)` | `YES` | `` | `` |
| `pathological_response_rate_date` | `date` | `YES` | `` | `` |
| `pathological_method_of_estimation` | `varchar(191)` | `YES` | `` | `` |
| `pfs` | `varchar(191)` | `YES` | `` | `` |
| `overall_survival` | `varchar(191)` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `patient_observation_response_rate_progression_sites`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_observation_detail_id` | `bigint unsigned` | `NO` | `` | `` |
| `type` | `varchar(191)` | `NO` | `` | `` |
| `value` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `patient_observations`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_id` | `bigint unsigned` | `NO` | `` | `` |
| `doctor_id` | `bigint unsigned` | `NO` | `` | `` |
| `center_id` | `bigint unsigned` | `NO` | `` | `` |
| `time` | `datetime` | `YES` | `` | `` |
| `registration_no` | `varchar(191)` | `YES` | `` | `` |
| `laterality` | `text` | `YES` | `` | `` |
| `grade` | `text` | `YES` | `` | `` |
| `diagnosis_disease_group` | `varchar(191)` | `YES` | `` | `` |
| `diagnosis_subgroup` | `varchar(191)` | `YES` | `` | `` |
| `diagnosis_primary_site` | `varchar(191)` | `YES` | `` | `` |
| `diagnosis_laterility` | `varchar(191)` | `YES` | `` | `` |
| `cancer_type` | `varchar(191)` | `YES` | `` | `` |
| `is_draft` | `tinyint(1)` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `patients`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `unique_id` | `varchar(15)` | `YES` | `` | `` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `phone` | `varchar(20)` | `YES` | `` | `` |
| `email` | `varchar(191)` | `YES` | `` | `` |
| `nid` | `varchar(15)` | `YES` | `` | `` |
| `date_of_birth` | `date` | `YES` | `` | `` |
| `age` | `int` | `NO` | `` | `` |
| `gender` | `varchar(10)` | `YES` | `` | `` |
| `blood_group` | `varchar(4)` | `YES` | `` | `` |
| `area` | `text` | `YES` | `` | `` |
| `police_station` | `varchar(55)` | `YES` | `` | `` |
| `district` | `varchar(55)` | `YES` | `` | `` |
| `socio_economic_status` | `varchar(191)` | `YES` | `` | `` |
| `photo` | `varchar(55)` | `YES` | `` | `` |
| `passport` | `varchar(13)` | `YES` | `` | `` |
| `type` | `varchar(15)` | `YES` | `` | `` |
| `is_draft` | `tinyint(1)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |
| `deleted_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `personal_access_tokens`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `tokenable_type` | `varchar(191)` | `NO` | `MUL` | `` |
| `tokenable_id` | `bigint unsigned` | `NO` | `` | `` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `token` | `varchar(64)` | `NO` | `UNI` | `` |
| `abilities` | `text` | `YES` | `` | `` |
| `last_used_at` | `timestamp` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `police_stations`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `district` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `radiotherapy_schedule_intent_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `value` | `text` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `radiotherapy_schedule_modalities`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `radiotherapy_schedule_id` | `bigint unsigned` | `NO` | `` | `` |
| `value` | `text` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `radiotherapy_schedule_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `type` | `varchar(191)` | `NO` | `` | `` |
| `value` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `radiotherapy_schedule_sites`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `radiotherapy_schedule_id` | `bigint unsigned` | `NO` | `` | `` |
| `value` | `varchar(191)` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `radiotherapy_schedules`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_observation_id` | `bigint unsigned` | `NO` | `` | `` |
| `start_date` | `date` | `YES` | `` | `` |
| `end_date` | `date` | `YES` | `` | `` |
| `intent` | `text` | `YES` | `` | `` |
| `fraction` | `text` | `YES` | `` | `` |
| `fraction_number` | `text` | `YES` | `` | `` |
| `total_dose` | `text` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `response_rate_calculation_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `target_lasion` | `varchar(191)` | `NO` | `` | `` |
| `non_target_lasion` | `varchar(191)` | `NO` | `` | `` |
| `new_lasion` | `varchar(191)` | `NO` | `` | `` |
| `result` | `varchar(191)` | `NO` | `` | `` |
| `type` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `response_rate_calculations`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `target_lasion` | `varchar(191)` | `NO` | `` | `` |
| `non_target_lasion` | `varchar(191)` | `NO` | `` | `` |
| `new_lasion` | `varchar(191)` | `NO` | `` | `` |
| `result` | `varchar(191)` | `NO` | `` | `` |
| `type` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `response_rate_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `type` | `varchar(191)` | `NO` | `` | `` |
| `group` | `varchar(191)` | `NO` | `` | `` |
| `value` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `smoking_histories`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_history_id` | `bigint unsigned` | `NO` | `` | `` |
| `status` | `varchar(191)` | `NO` | `` | `` |
| `per_day` | `int` | `YES` | `` | `` |
| `duration_in_year` | `double` | `YES` | `` | `` |
| `packs_per_year` | `double` | `YES` | `` | `` |
| `quit_period` | `double` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `socio_economic_status_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `staging_calculation_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `t` | `varchar(191)` | `YES` | `` | `` |
| `n` | `varchar(191)` | `YES` | `` | `` |
| `m` | `varchar(191)` | `YES` | `` | `` |
| `result` | `varchar(191)` | `NO` | `` | `` |
| `type` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `staging_clinicals`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_observation_id` | `bigint unsigned` | `NO` | `` | `` |
| `t` | `varchar(191)` | `YES` | `` | `` |
| `n` | `varchar(191)` | `YES` | `` | `` |
| `m` | `varchar(191)` | `YES` | `` | `` |
| `result` | `varchar(191)` | `YES` | `` | `` |
| `date` | `date` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `staging_pathological_details`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_observation_id` | `bigint unsigned` | `NO` | `` | `` |
| `lvsi` | `varchar(191)` | `YES` | `` | `` |
| `pni` | `varchar(191)` | `YES` | `` | `` |
| `margin` | `varchar(191)` | `YES` | `` | `` |
| `ki67` | `varchar(191)` | `YES` | `` | `` |
| `date` | `date` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `staging_pathologicals`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_observation_id` | `bigint unsigned` | `NO` | `` | `` |
| `t` | `varchar(191)` | `YES` | `` | `` |
| `n` | `varchar(191)` | `YES` | `` | `` |
| `m` | `varchar(191)` | `YES` | `` | `` |
| `result` | `varchar(191)` | `YES` | `` | `` |
| `date` | `date` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `surgeries`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_observation_id` | `bigint unsigned` | `NO` | `` | `` |
| `surgery_date` | `date` | `NO` | `` | `` |
| `modality` | `text` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `surgery_modality_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `surgical_lateralities`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `surgery_id` | `bigint unsigned` | `NO` | `` | `` |
| `value` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `surgical_laterality_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `value` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `survival_status_records`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `tb_histories`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `patient_history_id` | `bigint unsigned` | `NO` | `` | `` |
| `status` | `varchar(191)` | `NO` | `` | `` |
| `date` | `date` | `YES` | `` | `` |
| `treatment` | `text` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None

## `users`

### Columns

| Column | Type | Nullable | Key | Extra |
| --- | --- | --- | --- | --- |
| `id` | `bigint unsigned` | `NO` | `PRI` | `auto_increment` |
| `name` | `varchar(191)` | `NO` | `` | `` |
| `email` | `varchar(191)` | `NO` | `UNI` | `` |
| `email_verified_at` | `timestamp` | `YES` | `` | `` |
| `password` | `varchar(191)` | `NO` | `` | `` |
| `status` | `varchar(25)` | `NO` | `` | `` |
| `remember_token` | `varchar(100)` | `YES` | `` | `` |
| `created_at` | `timestamp` | `YES` | `` | `` |
| `updated_at` | `timestamp` | `YES` | `` | `` |

### Foreign Keys

- None
