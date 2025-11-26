# Schema & Typed Output

Fundas supports defining schemas for structured output with type enforcement. This ensures your extracted data has the correct data types.

## Basic Schema Usage

```python
import fundas as fd
from fundas import Schema, Column, DataType

# Define a schema
schema = Schema([
    Column("item", DataType.STRING, description="Product name"),
    Column("price", DataType.FLOAT, description="Price in USD"),
    Column("quantity", DataType.INTEGER),
    Column("in_stock", DataType.BOOLEAN),
])

# Extract with schema
df = fd.read_pdf("invoice.pdf", prompt="Extract items", schema=schema)

# DataFrame has proper types
print(df.dtypes)
# item        object
# price      float64
# quantity     Int64
# in_stock      bool
```

## DataType Reference

| DataType | Python Type | Notes |
|----------|-------------|-------|
| `STRING` | str | Default text type |
| `INTEGER` | int | Uses nullable Int64 in pandas |
| `FLOAT` | float | Numeric decimal values |
| `BOOLEAN` | bool | True/False values |
| `DATE` | date | Date without time |
| `DATETIME` | datetime | Full timestamp |
| `JSON` | dict | Nested objects |
| `ARRAY` | list | List of values |

## Column Options

The `Column` class supports several options:

```python
Column(
    name="column_name",        # Required: column name
    dtype=DataType.STRING,     # Required: data type
    description="Help text",   # Optional: guides AI extraction
    required=True,             # Optional: is column required (default: True)
    nullable=False,            # Optional: allow null values (default: False)
    enum_values=["A", "B"],    # Optional: restrict to specific values
    date_format="%Y-%m-%d",    # Optional: custom date parsing format
    array_item_type=DataType.STRING,  # Optional: for ARRAY type
    default="N/A",             # Optional: default value if not found
)
```

## Schema Options

```python
schema = Schema(
    columns=[...],           # List of Column objects
    name="extracted_data",   # Schema name (used in API request)
    strict=True,             # Enforce strict schema compliance
)
```

## Shorthand Dict Format

For simple schemas, use dict format:

```python
schema = Schema({
    "name": "string",
    "price": "float",
    "quantity": "integer",
})
```

Type string mappings:
- `"str"`, `"string"`, `"text"` → STRING
- `"int"`, `"integer"` → INTEGER
- `"float"`, `"number"`, `"double"`, `"decimal"` → FLOAT
- `"bool"`, `"boolean"` → BOOLEAN
- `"date"` → DATE
- `"datetime"`, `"timestamp"` → DATETIME
- `"json"`, `"object"`, `"dict"` → JSON
- `"array"`, `"list"` → ARRAY

## Date/DateTime Formats

Dates are parsed automatically from common formats:
- `YYYY-MM-DD` (ISO format)
- `DD/MM/YYYY`, `MM/DD/YYYY`
- `YYYY/MM/DD`

For custom formats:

```python
Column("date", DataType.DATE, date_format="%d-%b-%Y")  # e.g., "15-Jan-2024"
```

## Enum Values

Restrict column values to specific options:

```python
Column(
    "status",
    DataType.STRING,
    enum_values=["active", "inactive", "pending"]
)
```

## Array Columns

For columns containing lists:

```python
Column(
    "tags",
    DataType.ARRAY,
    array_item_type=DataType.STRING
)
```

## Nullable Columns

Allow null values:

```python
Column("optional_field", DataType.STRING, nullable=True)
```

## Default Values

Provide defaults for missing data:

```python
Column("category", DataType.STRING, default="Uncategorized")
```

## JSON Schema Output

Schemas are converted to JSON Schema format for the API:

```python
schema = Schema([
    Column("name", DataType.STRING, description="Product name"),
    Column("price", DataType.FLOAT),
])

print(schema.to_json_schema())
# {
#   "type": "object",
#   "properties": {
#     "name": {"type": "array", "items": {"type": "string", ...}},
#     "price": {"type": "array", "items": {"type": "number"}}
#   },
#   "required": ["name", "price"],
#   "additionalProperties": false
# }
```

## Schema Methods

| Method | Description |
|--------|-------------|
| `get_column_names()` | List of column names |
| `get_column(name)` | Get Column by name |
| `to_json_schema()` | Convert to JSON Schema |
| `to_response_format()` | Format for OpenRouter API |
| `convert_data(data)` | Convert dict values to proper types |

## Column Value Conversion

The `convert_value()` method handles type conversion:

```python
col = Column("price", DataType.FLOAT)
col.convert_value("123.45")  # Returns: 123.45
col.convert_value("1,234")   # Returns: 1234.0 (handles commas)
```

## Complete Example

```python
import fundas as fd
from fundas import Schema, Column, DataType

# Define schema with various types
schema = Schema([
    Column("product", DataType.STRING, description="Product name"),
    Column("price", DataType.FLOAT, description="Price in dollars"),
    Column("quantity", DataType.INTEGER),
    Column("available", DataType.BOOLEAN),
    Column("order_date", DataType.DATE),
    Column("category", DataType.STRING, enum_values=["Electronics", "Clothing", "Food"]),
    Column("tags", DataType.ARRAY, array_item_type=DataType.STRING),
])

# Extract with schema
df = fd.read_pdf(
    "orders.pdf",
    prompt="Extract order information",
    schema=schema
)

# Data is properly typed
print(df.info())
```
