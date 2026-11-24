"""Module for exporting query results into json and xml files"""

import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from decimal import Decimal
from pathlib import Path
from typing import Any

class DataExporter(ABC):
    """Abstract base class (ABC) defining the interface of result exporters."""

    @abstractmethod
    def export(self, data: dict[str, list[dict[str, Any]]], filepath: str) -> None:
        """Export query results into a file
        
        Args:
            data: Dictionary mapping query names to lists of result row dictionaries.
            filepath: Destination path for the output file
        """

        pass

class JsonExporter(DataExporter):
    """Concrete implementation of DataExporter for making formatter JSON files."""

    @staticmethod
    def _json_serializer(obj: Any) -> Any:
        """Handle non-standart JSON types (Decimal) returned by PostgreSQL
        Args:
            obj: Object that json.dump cannot serialize directly.
        
        Returns:
            A json-compatible representation (float if Decimal, str for others)
        """

        if isinstance(obj, Decimal):
            return float(obj)
        return str(obj)
    
    def export(self, data: dict[str, list[dict[str, Any]]], filepath: str) -> None:
        """Export query results into a UTF-8 encoded json file.
        
        Args:
            data: Dictionary mapping query names to lists of result row dictionaries.
            filepath: Destination path for the JSON output file
        """

        path = Path(filepath)
        #automatically create parent dictionaries (output/) if they do not exist
        path.parent.mkdir(parents = True, exist_ok = True)

        with path.open(mode = "w", encoding = "utf-8") as file:
            json.dump(
                data,
                file,
                indent = 4, 
                ensure_ascii = False,
                default = self._json_serializer
            )
class XmlExporter(DataExporter):
    """Concrete implementation of DataExporter for making formatted XML files."""

    def export(self, data: dict[str, list[dict[str, Any]]], filepath: str) -> None:
        """Build an XML tree from query results and write it to an XML file.
        
        Args:
            data: Dictionary mapping query names to lists of result row dictionaries.
            filepath: Destination path for the XML output file.
        """

        path = Path(filepath)
        #automatically create parent dictionaries (output/) if they do not exist
        path.parent.mkdir(parents = True, exist_ok = True)

        root = ET.Element("results")

        for query_name, rows in data.items():
            # Create a section element for each analytical query
            section_elem = ET.SubElement(root, query_name)

            for row in rows:
                item_elem = ET.SubElement(section_elem, "item")
                for k, v in row.items():
                    field_elem = ET.SubElement(item_elem, str(k))
                    field_elem.text = "" if v is None else str(v)
        
        # Format the XML tree with 4-space indent 
        tree = ET.ElementTree(root)
        ET.indent(tree, space = "    ", level = 0)
        tree.write(path, encoding = "utf-8", xml_declaration = True)
