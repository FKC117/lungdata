from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connections


class Command(BaseCommand):
    help = "Snapshot the legacy MySQL schema into a markdown report."

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            default="legacy",
            help="Database connection name to inspect. Defaults to 'legacy'.",
        )
        parser.add_argument(
            "--output",
            default="LEGACY_SCHEMA_SNAPSHOT.md",
            help="Output markdown filename, relative to BASE_DIR unless absolute.",
        )

    def handle(self, *args, **options):
        database = options["database"]
        output = Path(options["output"])
        if not output.is_absolute():
            output = Path(settings.BASE_DIR) / output

        connection = connections[database]
        schema_name = connection.settings_dict["NAME"]

        tables = self.fetch_tables(connection)
        columns = self.fetch_columns(connection, schema_name)
        foreign_keys = self.fetch_foreign_keys(connection, schema_name)

        report = self.render_report(schema_name, tables, columns, foreign_keys)
        output.write_text(report, encoding="utf-8")

        self.stdout.write(self.style.SUCCESS(f"Legacy schema snapshot written to {output}"))

    def fetch_tables(self, connection):
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            return [row[0] for row in cursor.fetchall()]

    def fetch_columns(self, connection, schema_name):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY, EXTRA
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s
                ORDER BY TABLE_NAME, ORDINAL_POSITION
                """,
                [schema_name],
            )
            rows = cursor.fetchall()
        grouped = {}
        for table_name, column_name, column_type, is_nullable, column_key, extra in rows:
            grouped.setdefault(table_name, []).append(
                {
                    "name": column_name,
                    "type": column_type,
                    "nullable": is_nullable,
                    "key": column_key,
                    "extra": extra,
                }
            )
        return grouped

    def fetch_foreign_keys(self, connection, schema_name):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = %s AND REFERENCED_TABLE_NAME IS NOT NULL
                ORDER BY TABLE_NAME, COLUMN_NAME
                """,
                [schema_name],
            )
            rows = cursor.fetchall()
        grouped = {}
        for table_name, column_name, ref_table, ref_column in rows:
            grouped.setdefault(table_name, []).append(
                {
                    "column": column_name,
                    "ref_table": ref_table,
                    "ref_column": ref_column,
                }
            )
        return grouped

    def render_report(self, schema_name, tables, columns, foreign_keys):
        lines = [
            f"# Legacy Schema Snapshot",
            "",
            f"Schema: `{schema_name}`",
            "",
            f"Table count: `{len(tables)}`",
            "",
        ]

        for table in tables:
            lines.append(f"## `{table}`")
            lines.append("")
            lines.append("### Columns")
            lines.append("")
            lines.append("| Column | Type | Nullable | Key | Extra |")
            lines.append("| --- | --- | --- | --- | --- |")
            for column in columns.get(table, []):
                lines.append(
                    f"| `{column['name']}` | `{column['type']}` | `{column['nullable']}` | `{column['key']}` | `{column['extra']}` |"
                )
            lines.append("")
            lines.append("### Foreign Keys")
            lines.append("")
            if foreign_keys.get(table):
                for fk in foreign_keys[table]:
                    lines.append(
                        f"- `{fk['column']}` -> `{fk['ref_table']}.{fk['ref_column']}`"
                    )
            else:
                lines.append("- None")
            lines.append("")

        return "\n".join(lines)
