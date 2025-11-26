"""
Fundas - Schema definitions for structured outputs

This module provides schema classes for defining output data types,
enabling structured outputs via OpenRouter's JSON Schema support.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime, date
import json


class DataType(Enum):
    """Supported data types for schema columns."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "number"
    BOOLEAN = "boolean"
    DATE = "date"  # Will be converted from string
    DATETIME = "datetime"  # Will be converted from string
    JSON = "json"  # Nested JSON object
    ARRAY = "array"  # Array of items


class Column:
    """
    Define a column with a specific data type for structured output.

    Args:
        name: Column name
        dtype: Data type (DataType enum or string shorthand)
        description: Optional description to guide the AI
        required: Whether this column is required (default: True)
        nullable: Whether null values are allowed (default: False)
        enum_values: Optional list of allowed values
        date_format: Format string for date/datetime parsing
            (default: ISO format)
        array_item_type: For ARRAY type, the type of items in the array
        default: Default value if not provided

    Examples:
        >>> Column("name", DataType.STRING, description="Person's full name")
        >>> Column("age", "integer", required=True)
        >>> Column("price", DataType.FLOAT, nullable=True)
        >>> Column(
        ...     "created_at",
        ...     DataType.DATETIME,
        ...     date_format="%Y-%m-%d %H:%M:%S",
        ... )
        >>> Column(
        ...     "status", DataType.STRING, enum_values=["active", "inactive"]
        ... )
    """

    def __init__(
        self,
        name: str,
        dtype: Union[DataType, str],
        description: Optional[str] = None,
        required: bool = True,
        nullable: bool = False,
        enum_values: Optional[List[Any]] = None,
        date_format: Optional[str] = None,
        array_item_type: Optional[Union[DataType, str]] = None,
        default: Optional[Any] = None,
    ):
        self.name = name
        self.dtype = self._parse_dtype(dtype)
        self.description = description
        self.required = required
        self.nullable = nullable
        self.enum_values = enum_values
        self.date_format = date_format
        self.array_item_type = (
            self._parse_dtype(array_item_type) if array_item_type else None
        )
        self.default = default

    def _parse_dtype(self, dtype: Union[DataType, str]) -> DataType:
        """Parse dtype from string or DataType enum."""
        if isinstance(dtype, DataType):
            return dtype

        dtype_lower = dtype.lower()
        type_mapping = {
            "str": DataType.STRING,
            "string": DataType.STRING,
            "text": DataType.STRING,
            "int": DataType.INTEGER,
            "integer": DataType.INTEGER,
            "float": DataType.FLOAT,
            "number": DataType.FLOAT,
            "double": DataType.FLOAT,
            "decimal": DataType.FLOAT,
            "bool": DataType.BOOLEAN,
            "boolean": DataType.BOOLEAN,
            "date": DataType.DATE,
            "datetime": DataType.DATETIME,
            "timestamp": DataType.DATETIME,
            "json": DataType.JSON,
            "object": DataType.JSON,
            "dict": DataType.JSON,
            "array": DataType.ARRAY,
            "list": DataType.ARRAY,
        }

        if dtype_lower in type_mapping:
            return type_mapping[dtype_lower]
        else:
            raise ValueError(
                f"Unknown data type: {dtype}. "
                f"Supported types: {list(type_mapping.keys())}"
            )

    def to_json_schema(self) -> Dict[str, Any]:
        """Convert column definition to JSON Schema format."""
        schema: Dict[str, Any] = {}

        # Map our types to JSON Schema types
        type_mapping = {
            DataType.STRING: "string",
            DataType.INTEGER: "integer",
            DataType.FLOAT: "number",
            DataType.BOOLEAN: "boolean",
            DataType.DATE: "string",  # Dates are strings in JSON
            DataType.DATETIME: "string",  # Datetimes are strings in JSON
            DataType.JSON: "object",
            DataType.ARRAY: "array",
        }

        json_type = type_mapping.get(self.dtype, "string")

        if self.nullable:
            schema["type"] = [json_type, "null"]
        else:
            schema["type"] = json_type

        if self.description:
            schema["description"] = self.description

        # Add format hints for date types
        if self.dtype == DataType.DATE:
            schema["description"] = (
                schema.get("description", "") + " (Format: YYYY-MM-DD)"
            ).strip()
        elif self.dtype == DataType.DATETIME:
            schema["description"] = (
                schema.get("description", "") + " (Format: ISO 8601 datetime)"
            ).strip()

        if self.enum_values:
            schema["enum"] = self.enum_values

        if self.dtype == DataType.ARRAY and self.array_item_type:
            item_type = type_mapping.get(self.array_item_type, "string")
            schema["items"] = {"type": item_type}

        return schema

    def convert_value(self, value: Any) -> Any:
        """Convert a value to the appropriate Python type."""
        if value is None:
            if self.nullable:
                return None
            elif self.default is not None:
                return self.default
            return None

        try:
            if self.dtype == DataType.STRING:
                return str(value)

            elif self.dtype == DataType.INTEGER:
                if isinstance(value, str):
                    # Handle strings with commas, spaces, etc.
                    value = value.replace(",", "").replace(" ", "").strip()
                return int(float(value))

            elif self.dtype == DataType.FLOAT:
                if isinstance(value, str):
                    value = value.replace(",", "").replace(" ", "").strip()
                return float(value)

            elif self.dtype == DataType.BOOLEAN:
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    return value.lower() in ("true", "yes", "1", "on", "t", "y")
                return bool(value)

            elif self.dtype == DataType.DATE:
                if isinstance(value, date):
                    return value
                if isinstance(value, datetime):
                    return value.date()
                if isinstance(value, str):
                    if self.date_format:
                        return datetime.strptime(value, self.date_format).date()
                    # Try common formats
                    for fmt in [
                        "%Y-%m-%d",
                        "%d/%m/%Y",
                        "%m/%d/%Y",
                        "%Y/%m/%d",
                        "%d-%m-%Y",
                        "%m-%d-%Y",
                    ]:
                        try:
                            return datetime.strptime(value, fmt).date()
                        except ValueError:
                            continue
                    # Last resort: try pandas
                    try:
                        import pandas as pd

                        return pd.to_datetime(value).date()
                    except Exception:
                        pass
                return value

            elif self.dtype == DataType.DATETIME:
                if isinstance(value, datetime):
                    return value
                if isinstance(value, str):
                    if self.date_format:
                        return datetime.strptime(value, self.date_format)
                    # Try common formats
                    for fmt in [
                        "%Y-%m-%dT%H:%M:%S",
                        "%Y-%m-%dT%H:%M:%SZ",
                        "%Y-%m-%d %H:%M:%S",
                        "%Y-%m-%dT%H:%M:%S.%f",
                        "%Y-%m-%dT%H:%M:%S.%fZ",
                        "%d/%m/%Y %H:%M:%S",
                        "%m/%d/%Y %H:%M:%S",
                    ]:
                        try:
                            return datetime.strptime(value, fmt)
                        except ValueError:
                            continue
                    # Last resort: try pandas
                    try:
                        import pandas as pd

                        return pd.to_datetime(value).to_pydatetime()
                    except Exception:
                        pass
                return value

            elif self.dtype == DataType.JSON:
                if isinstance(value, dict):
                    return value
                if isinstance(value, str):
                    return json.loads(value)
                return value

            elif self.dtype == DataType.ARRAY:
                if isinstance(value, list):
                    if self.array_item_type:
                        # Convert each item in the array
                        item_col = Column("item", self.array_item_type)
                        return [item_col.convert_value(v) for v in value]
                    return value
                if isinstance(value, str):
                    # Try to parse as JSON array
                    try:
                        parsed = json.loads(value)
                        if isinstance(parsed, list):
                            return parsed
                    except json.JSONDecodeError:
                        # Split by comma
                        return [v.strip() for v in value.split(",")]
                return [value]

        except (ValueError, TypeError):
            # If conversion fails, return original value
            return value

        return value


class Schema:
    """
    Define a schema for structured output with typed columns.

    Args:
        columns: List of Column objects or dict of {name: dtype} pairs
        name: Optional schema name (used in API request)
        strict: Whether to enforce strict schema compliance (default: True)

    Examples:
        >>> schema = Schema([
        ...     Column("name", DataType.STRING, description="Product name"),
        ...     Column("price", DataType.FLOAT, description="Price in USD"),
        ...     Column("quantity", DataType.INTEGER),
        ...     Column("in_stock", DataType.BOOLEAN),
        ...     Column("created_at", DataType.DATETIME),
        ... ])

        >>> # Shorthand dict format
        >>> schema = Schema({
        ...     "name": "string",
        ...     "price": "float",
        ...     "quantity": "integer",
        ... })

        >>> # Using with read functions
        >>> df = fd.read_pdf("invoice.pdf", prompt="Extract items", schema=schema)
    """

    def __init__(
        self,
        columns: Union[List[Column], Dict[str, Union[str, DataType]]],
        name: str = "extracted_data",
        strict: bool = True,
    ):
        self.name = name
        self.strict = strict

        if isinstance(columns, dict):
            self.columns = [Column(name, dtype) for name, dtype in columns.items()]
        else:
            self.columns = columns

        # Create lookup dict for fast access
        self._column_map = {col.name: col for col in self.columns}

    def get_column_names(self) -> List[str]:
        """Get list of column names."""
        return [col.name for col in self.columns]

    def get_column(self, name: str) -> Optional[Column]:
        """Get column by name."""
        return self._column_map.get(name)

    def to_json_schema(self) -> Dict[str, Any]:
        """Convert schema to JSON Schema format for OpenRouter API."""
        properties = {}
        required = []

        for col in self.columns:
            # Each column is an array of values for DataFrame format
            col_schema = {
                "type": "array",
                "items": col.to_json_schema(),
                "description": f"Array of {col.name} values"
                + (f" - {col.description}" if col.description else ""),
            }
            properties[col.name] = col_schema

            if col.required:
                required.append(col.name)

        return {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        }

    def to_response_format(self) -> Dict[str, Any]:
        """Generate response_format for OpenRouter API."""
        return {
            "type": "json_schema",
            "json_schema": {
                "name": self.name,
                "strict": self.strict,
                "schema": self.to_json_schema(),
            },
        }

    def convert_data(self, data: Dict[str, List[Any]]) -> Dict[str, List[Any]]:
        """Convert data according to schema types."""
        converted = {}

        for col_name, values in data.items():
            col = self._column_map.get(col_name)
            if col:
                # Convert each value in the list
                converted[col_name] = [col.convert_value(v) for v in values]
            else:
                # Keep as-is if column not in schema
                converted[col_name] = values

        return converted

    def __repr__(self) -> str:
        cols_str = ", ".join(f"{col.name}:{col.dtype.value}" for col in self.columns)
        return f"Schema({cols_str})"
