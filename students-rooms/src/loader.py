"""Module for loading input data from external files"""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class DataLoader(ABC):
    """Abstract base class (ABC) for data loaders."""

    @abstractmethod 
    def load(self, filepath: str) -> list[dict[str, Any]]:
        """Load the data from file.

        Args: 
            filepath: Path to the input file.
            
        Returns:
            A list of dictionaries, containing parsed records.
        """
        pass


class JsonLoader(DataLoader):
    """Concrete implementation of DataLoader for reading JSON files (students.json and rooms.json)."""

    def load(self, filepath: str) -> list[dict[str, Any]]:
        """ Read and parse a JSON file containing a list of objects.
        
        Args:
            filepath: path to the JSON file.
            
        Returns:
            A list of dictionaries, containing parsed records from JSON file.
        """
        # creating an instance of Path
        path = Path(filepath)

        # Verifying that the path leads to an existing file
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {filepath}")

        # if the file exists, reads it using UTF-8 encoding 
        with path.open(mode="r", encoding="utf-8") as file:
            data = json.load(file)

        # Ensure that the json file is a list of records
        if not isinstance(data, list):
            raise ValueError(f"Expected a list of objects in file: {filepath}")
        
        return data