# Students and Rooms ETL

A command-line ETL utility built with Python and PostgreSQL for ingesting student and room datasets from JSON files, executing analytical SQL queries, and exporting aggregated reports in JSON or XML formats.

## Project Structure

```text
students-rooms/
├── data/                   				# Input JSON datasets (rooms.json, students.json)
├── output/                 				# Generated analytical reports (result.json / result.xml)
├── sql/                    				# DDL schema creation and analytical SELECT queries
│   ├── indexes.sql							# SQL script containing indexes for queries
│   ├── rooms_biggest_age_gap.sql			
│   ├── rooms_different_sex_students.sql	
│   ├── rooms_student_count.sql
│   ├── schema.sql							# SQL script containing tables schema
│   └── smallest_avg_age_rooms.sql
├── src/
│   ├── config.py           				# Immutable database configuration loader
│   ├── database.py         				# PostgreSQL connection context manager and query executor
│   ├── exporter.py         				# JSON and XML report exporters
│   └── loader.py           				# JSON file reader and data loader
├── docker-compose.yml      				# PostgreSQL container configuration
├── main.py                 				# CLI entry point
└── requirements.txt        				# Python dependencies
```

## Prerequisites

- **Python**: 3.10 or higher
- **Docker & Docker Compose**: For running the PostgreSQL database instance

## Setup & Installation

1. **Clone the repository and navigate to the project directory:**
   ```bash
   git clone [https://github.com/yliyaa09102007-oss/students-rooms.git](https://github.com/yliyaa09102007-oss/students-rooms.git)
   cd students-rooms
   ```

2. **Start the PostgreSQL container:**
   ```bash
   docker-compose up -d
   ```

3. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The utility reads PostgreSQL connection settings from environment variables. If not set, it falls back to the default values matching `docker-compose.yml`:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DB_HOST` | PostgreSQL server host | `localhost` |
| `DB_PORT` | PostgreSQL server port | `5432` |
| `DB_NAME` | Target database name | `rooms_db` |
| `DB_USER` | Database user | `de` |
| `DB_PASSWORD` | Database password | `secret` |

## Usage

Run the ETL pipeline via `main.py`, specifying paths to the input files and the desired output format (`json` or `xml`):

```bash
python main.py --students data/students.json --rooms data/rooms.json --format json
```

To export the report in XML format:

```bash
python main.py --students data/students.json --rooms data/rooms.json --format xml
```

Generated reports will be saved in the `output/` directory.