"""Entry point for the Students and Rooms data processing utility."""

import json
import psycopg2

import argparse
import sys
from pathlib import Path
from typing import Any

from src.config import load_db_config
from src.database import DataBaseManager
from src.exporter import DataExporter, JsonExporter, XmlExporter
from src.loader import JsonLoader

ANALYTICAL_QUERIES: dict[str, str] = {
    "rooms_student_count": "sql/rooms_student_count.sql",
    "smallest_avg_age_rooms": "sql/smallest_avg_age_rooms.sql",
    "rooms_biggest_age_gap": "sql/rooms_biggest_age_gap.sql",
    "rooms_different_sex_students": "sql/rooms_different_sex_students.sql"
}

def parse_args() -> argparse.Namespace:
    """ Parse command-line interface arguments.

    Returns:
        Passed args namespace containing students path, rooms path, output path and output format.
    """

    parser = argparse.ArgumentParser(
        description = "Load students and rooms data into PostgreSql and export analytical reports"
    )
    parser.add_argument(
        "--students",
        type = str,
        default = "data/students.json",
        help = "Path to the students.json file (default: data/students.json)."
    )
    parser.add_argument(
        "--rooms",
        type = str,
        default = "data/rooms.json",
        help = "Path to the rooms.json file (default: data/rooms.json)."
    )
    parser.add_argument(
        "--format",
        type = str.lower,
        choices = ["json", "xml"],
        required = True,
        help = "Output report format (json or xml)."
    )
    parser.add_argument(
        "--output",
        type = str,
        default = None,
        help = "Custom output file path (default: output/result.<format>)."
    )
    return parser.parse_args()

def get_exporter(output_format: str) -> DataExporter:
    """Function returning the appropriate exporter instance for the chosen format.
    
    Args:
        output_format: Targer format (xml or json)
    
    Returns:
        An instance of DataExporter subclass.
    
    Raises:
        ValueError: If an unsupported format is provided.
    """

    exporters: dict[str, DataExporter] = {
        "json": JsonExporter(),
        "xml": XmlExporter()
    }
    if output_format not in exporters:
        raise ValueError(f"Unsupported file format: {output_format}")
    return exporters[output_format]

def main():
    """Run the ETL (Extract, Transform, Load) and analytical reporting pipeline."""

    args = parse_args()

    output_path = args.output or f"output/result.{args.format}"

    try:
        # 1) Load input JSON files
        loader = JsonLoader()
        rooms_data = loader.load(args.rooms)
        students_data = loader.load(args.students)

        # 2) Connect to PostgreSQL, initialize schema, load data, run analytics
        db_config = load_db_config().to_dict()
        results: dict[str, list[dict[str, Any]]] = {}

        with DataBaseManager(db_config) as db:
            db.execute_sql_file("sql/schema.sql")
            db.clear_tables()

            # Insert rooms first to not get an error on foreing key constraints on students.room
            db.insert_rooms(rooms_data)
            db.insert_students(students_data)

            # Apply indexes after bulk loading for optimal insert perfomance
            db.execute_sql_file("sql/indexes.sql")

            # Execute analytical queries
            for query_name, path in ANALYTICAL_QUERIES.items():
                results[query_name] = db.fetch_query(path)
        
        # 3) Export aggregated results to the requested format
        exporter = get_exporter(args.format)
        exporter.export(results, output_path)

        print(f"Success! Report exported to {Path(output_path).resolve()}")

    except FileNotFoundError as exc:
        print(f"File error: {exc}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON format in input file: {exc}", file=sys.stderr)
        sys.exit(1)
    except (KeyError, ValueError) as exc:
        print(f"Data validation error: {exc}", file=sys.stderr)
        sys.exit(1)
    except psycopg2.OperationalError as exc:
        print(f"Database connection error (is Docker running?): {exc}", file=sys.stderr)
        sys.exit(1)
    except psycopg2.Error as exc:
        print(f"Database query error: {exc}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"I/O error: {exc}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
