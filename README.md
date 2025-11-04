# MISMO XML to JSON Parser

Parses MISMO XML files to JSON format with optional structured loan data extraction.

## Features

- ✅ Command-line interface with flexible arguments
- ✅ Parses XML to JSON while preserving structure
- ✅ Removes XML namespaces for cleaner output
- ✅ Handles XML attributes and duplicate elements
- ✅ Optional structured MISMO loan data extraction
- ✅ Comprehensive test suite

## Installation

### Prerequisites
- Python 3.6 or higher

### Setup

1. **Clone or download this repository**

2. **Install dependencies (optional, for testing)**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Convert an XML file to JSON (output will be `input.json`):
```bash
python main.py input.xml
```

### Specify Output File

Convert with custom output filename:
```bash
python main.py input.xml -o output.json
```

### Generate Structured Output

Create both raw and structured JSON versions:
```bash
python main.py input.xml --structured
```
This creates:
- `input.json` - Complete JSON conversion
- `input_structured.json` - Organized loan data sections

### Custom Structured Output Path

Specify custom paths for both outputs:
```bash
python main.py data.xml -o result.json --structured --structured-output loan_data.json
```

### Command-Line Options

```
positional arguments:
  input                 Input XML file path

optional arguments:
  -h, --help            Show help message and exit
  -o, --output          Output JSON file path (default: replaces .xml with .json)
  -s, --structured      Also create a structured version with extracted loan data
  --structured-output   Custom path for structured output (default: adds _structured suffix)
```

### Examples

```bash
# Simple conversion
python main.py mortgage_data.xml

# Custom output
python main.py mortgage_data.xml -o parsed_mortgage.json

# With structured extraction
python main.py mortgage_data.xml -s

# Everything custom
python main.py mortgage_data.xml -o raw.json -s --structured-output structured.json
```

## What It Does

### Basic Parsing
- Converts XML elements to JSON objects
- Preserves XML attributes under `@attributes` key
- Handles duplicate XML elements as JSON arrays
- Removes XML namespace prefixes for cleaner output

### Structured MISMO Data Extraction
When using the `--structured` flag, the parser extracts and organizes MISMO-specific loan data into these sections:
- **message_info** - Version and metadata
- **deal_info** - Deal-level information
- **collaterals** - Property and collateral details
- **loans** - Loan terms and details
- **parties** - Borrowers, lenders, and other parties
- **relationships** - Relationships between entities

## Testing

Run the test suite:
```bash
pytest test_parser.py -v
```

Run tests with coverage:
```bash
pytest test_parser.py --cov=main --cov-report=html
```

### Test Coverage
The test suite includes:
- XML parsing with various structures
- Namespace handling
- Attribute preservation
- Duplicate element handling
- MISMO loan data extraction
- Error handling for invalid files
- Command-line interface validation

## Project Structure

```
MISMO-Parse/
├── main.py              # Main parser script
├── test_parser.py       # Comprehensive test suite
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── .gitignore          # Git ignore rules (includes *.xml)
```

## Troubleshooting

- **"Input file not found"**: Check that the file path is correct
- **Parsing errors**: Ensure your XML file is valid and well-formed
- **Permission errors**: Verify read/write permissions in the directory
- **Import errors**: Install dependencies with `pip install -r requirements.txt`

## Development

### Code Style
Format code with black:
```bash
black main.py test_parser.py
```

Check code quality:
```bash
flake8 main.py test_parser.py
```
