"""Module for managing PostgreSql connection, schema and queries."""

from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import RealDictCursor, execute_values

class DataBaseManager:
    """Handles db operations including schema creation, inserts and analytics"""

    def __init__(self, db_config: dict[str, Any]) -> None:
        """Initializes the db manager with connection params
        
        Args:
            db_config: Dictionary that contains host, port, db name, user and password
        """
        self.db_config = db_config
        self.conn: PgConnection | None = None

    def __enter__(self) -> "DataBaseManager":
        """Opens a db connection when entering the context manager"""
        self.conn = psycopg2.connect(**self.db_config)
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Close a db connection when exiting the context manager
        
        Args:
            exc_type (Exception Type) - class of an exception if something failed inside 'with ...', or None
            exc_val (Exception Value) - class containing a text of exception, or None
            exc_tb (Exception Traceback) - an information about where did the exeption happen
        """
        
        if self.conn:
            #rolling back a transaction if an exception happened
            if exc_type is not None:
                self.conn.rollback()
            self.conn.close()

    def execute_sql_file(self, filepath: str) -> None:
        """Read and execute and SQL file (eg. schema.sql)
        
        Args:
            filepath: Path to the sql file
            
        Raises:
            FileNotFoundError: If an sql file does not exist
            RuntimeError: If the database connection is not established
        """
        if not self.conn:
            raise RuntimeError("Database connection is not open.")

        path = Path(filepath)
        if not path.is_file():
            raise FileNotFoundError(f"SQL file not found: {filepath}")
        
        sql_script = path.read_text(encoding = "utf-8")

        with self.conn.cursor() as cursor:
            cursor.execute(sql_script)
        self.conn.commit()

    def clear_tables(self) -> None:
        """Truncate existing records in students and rooms tables for idempotent runs"""
        if not self.conn:
            raise RuntimeError("Database connection is not open.")
        
        with self.conn.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE students, rooms RESTART IDENTITY CASCADE;")
        self.conn.commit()

    def insert_rooms(self, rooms: list[dict[str, Any]], page_size: int = 5000) -> None:
        """Batch insert rooms records into the db using execute_values
        
        Args:
            rooms: list of room dictionaries with 'id' and 'name' keys
            page_size: numbers of rows per batch INSERT statement
        """

        if not self.conn:
            raise RuntimeError("Database connection is not open.")
        
        if not rooms:
            return

        #Convert list of dicts into list of tuples matching table columns
        records = [
            (
                room["id"], 
                room["name"]
            ) 
            for room in rooms
        ]

        query = "INSERT INTO rooms (id, name) VALUES %s;"

        with self.conn.cursor() as cursor:
            execute_values(cursor, query, records, page_size=page_size)
        self.conn.commit()

    def insert_students(self, students: list[dict[str, Any]], page_size: int = 5000) -> None:
        """Batch insert students records into the db using execute_values
        
        Args:
            students: list of room dictionaries with 'id', 'name', 'birthday', 'room', 'sex' keys
            page_size: numbers of rows per batch INSERT statement
        """

        if not self.conn:
            raise RuntimeError("Database connection is not open.")
        
        if not students:
            return

        #Convert list of dicts into list of tuples matching table columns
        records = [
            (
                student["id"], 
                student["name"], 
                student["birthday"], 
                student["room"], 
                student["sex"]
            ) 
            for student in students
        ]
        
        query = "INSERT INTO students (id, name, birthday, room, sex) VALUES %s;"

        with self.conn.cursor() as cursor:
            execute_values(cursor, query, records, page_size=page_size)
        self.conn.commit()

    def fetch_query(self, filepath: str) -> list[dict[str, Any]]:
        """ Execute an analytical SQL query from a file and return rows as dictionaries.

        Args:
            filepath: Path to an sql file containing a SELECT query.
    
        Returns:
            A list of dictionaries where keys correspond to column names.
        """
        if not self.conn:
            raise RuntimeError("Database connection is not open.")
        
        path = Path(filepath)
        
        if not path.is_file():
            raise FileNotFoundError(f"SQL query file not found: {filepath}")
        
        sql_query = path.read_text(encoding = "utf-8")

        #RealDictCursor returns each row as a dict instead of a plain tuple
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql_query)
            results = cursor.fetchall()

        #Convert RealDictRow objects to standart Python dictionaries
        return [dict(row) for row in results]

