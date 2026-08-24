const fs = require('fs');

const input = 'lungcanc_deleted_observations_binlog.txt';
const output = 'recover_observations_from_binlog_local_only.sql';
const report = 'binlog_observation_recovery_summary.json';
const columns = [
  'id', 'patient_id', 'doctor_id', 'center_id', 'time', 'registration_no',
  'laterality', 'grade', 'diagnosis_disease_group', 'diagnosis_subgroup',
  'diagnosis_primary_site', 'diagnosis_laterility', 'cancer_type', 'is_draft',
  'created_at', 'updated_at',
];

const text = fs.readFileSync(input, 'utf8').replace(/\r/g, '');
const blocks = text.split(/^### DELETE FROM `lungcanc`\.`patient_observations`\n/m).slice(1);
const rowsById = new Map();
const fieldCounts = new Map();

for (const block of blocks) {
  const row = [];
  for (const line of block.split('\n')) {
    const match = line.match(/^###\s+@(\d+)=(.*?)\s+\/\*/);
    if (!match) {
      if (row.length) break;
      continue;
    }
    row[Number(match[1]) - 1] = match[2];
  }
  const count = row.filter((x) => x !== undefined).length;
  fieldCounts.set(count, (fieldCounts.get(count) || 0) + 1);
  if (count !== columns.length || row.length !== columns.length || row.some((x) => x === undefined)) continue;
  const id = row[0];
  if (!/^\d+$/.test(id)) throw new Error(`Unexpected observation id: ${id}`);
  const prior = rowsById.get(id);
  if (prior && prior.join('\n') !== row.join('\n')) throw new Error(`Conflicting deleted versions for observation ${id}`);
  rowsById.set(id, row);
}

const rows = [...rowsById.values()].sort((a, b) => Number(a[0]) - Number(b[0]));
if (rows.length === 0) throw new Error('No complete rows parsed.');

function sqlValue(value, index) {
  if (index === 13) return '0'; // Publish recovered rows intentionally.
  if ((index === 14 || index === 15) && value !== 'NULL') return `FROM_UNIXTIME(${value})`;
  return value;
}

const values = rows.map((row) => `  (${row.map(sqlValue).join(', ')})`).join(',\n');
const sql = `-- LOCAL DATABASE ONLY. Do not run on live production.\n` +
`-- Source: MySQL row-format binlogs; ${rows.length} unique deleted patient_observations rows.\n` +
`-- Restores original fields and publishes the recovered observations (is_draft = 0).\n\n` +
`INSERT INTO patient_observations (\n  ${columns.join(',\n  ')}\n) VALUES\n${values}\n` +
`ON DUPLICATE KEY UPDATE\n` +
columns.filter((column) => column !== 'id').map((column) => `  ${column} = VALUES(${column})`).join(',\n') + `;\n\n` +
`-- Verify after running:\n` +
`-- SELECT COUNT(*) AS total_observations, SUM(is_draft = 1) AS draft_observations FROM patient_observations;\n`;
fs.writeFileSync(output, sql, 'utf8');
fs.writeFileSync(report, JSON.stringify({
  source_delete_events: blocks.length,
  unique_complete_rows: rows.length,
  field_counts: Object.fromEntries(fieldCounts),
  observation_id_min: Number(rows[0][0]),
  observation_id_max: Number(rows.at(-1)[0]),
}, null, 2) + '\n');
console.log(JSON.stringify(JSON.parse(fs.readFileSync(report, 'utf8')), null, 2));
