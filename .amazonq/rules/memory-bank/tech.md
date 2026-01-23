# Circuit Diagram Generator - Technology Stack

## Programming Languages and Versions

### Primary Language
- **Python 3.x**: Core implementation language
- **Standard Library**: Extensive use of built-in modules (csv, xml, math)
- **Object-Oriented Design**: Class-based architecture with inheritance

### Markup Languages
- **SVG 1.1**: Scalable Vector Graphics for diagram output
- **XML**: SVG symbol definitions and document structure
- **CSV**: Data input format for circuit specifications

## Dependencies and Libraries

### Required Dependencies
```bash
pip install cairosvg pillow
```

### Core Libraries
- **cairosvg**: SVG to PNG conversion (mentioned in README)
- **Pillow (PIL)**: Image processing and format conversion
- **csv** (built-in): CSV file parsing and data extraction
- **xml.etree.ElementTree** (built-in): XML/SVG parsing and manipulation

### Standard Library Modules
- **os**: File system operations and path handling
- **math**: Mathematical calculations for positioning
- **collections**: Data structure utilities
- **typing**: Type hints and annotations (if used)

## Build System and Development

### Project Structure
- **No build system required**: Pure Python implementation
- **Direct execution**: Run with `python circuit_generator.py`
- **Module imports**: Relative imports between project modules

### Development Commands

#### Basic Usage
```bash
# Generate circuit diagram
python circuit_generator.py

# With custom files (modify main block)
python -c "
from circuit_generator import SVGCircuitGenerator
gen = SVGCircuitGenerator('my_chips.csv', 'my_connections.csv', 'my_datasheets.csv')
gen.generate_circuit()
"
```

#### File Operations
```bash
# View generated SVG
# Open circuit_diagram.svg in web browser or SVG viewer

# Convert to PNG (requires cairosvg)
cairosvg circuit_diagram.svg -o circuit_diagram.png

# Validate CSV files
python -c "
from data_loader import DataLoader
loader = DataLoader()
chips = loader.load_chips('chips.csv', {})
print(f'Loaded {len(chips)} chips')
"
```

## Configuration Files

### Input Data Files
- **chips.csv**: Circuit component definitions
  - Format: chip_id, chip_type, gate_num, layer
  - Example: U1,4009,1,0
- **connections.csv**: Inter-component wiring
  - Format: from_chip, from_pin, to_chip, to_pin
  - Example: U1,2,U2,1
- **chip_datasheets.csv**: IC specifications and pinouts
  - Format: chip_type, gate_num, input_pins, output_pin, gate_type, vcc_pin, gnd_pin, total_pins, description

### Symbol Library
- **DB/ folder**: SVG gate symbol definitions
- **Naming convention**: {GATE_TYPE}{INPUT_COUNT}.svg
- **Examples**: AND2.svg, NAND3.svg, OR4.svg

## Output Formats

### Primary Output
- **SVG**: Scalable Vector Graphics (circuit_diagram.svg)
- **Advantages**: Scalable, editable, web-compatible
- **Structure**: XML-based with embedded symbols and styling

### Secondary Formats
- **PNG**: Raster image conversion (via cairosvg)
- **PDF**: Vector format conversion (via cairosvg)
- **Other formats**: Supported through cairosvg conversion

## Development Environment

### Recommended Setup
- **Python 3.7+**: Modern Python version with type hints support
- **IDE**: Any Python-compatible IDE (VS Code, PyCharm, etc.)
- **SVG Viewer**: Browser or dedicated SVG editor for output verification
- **CSV Editor**: Spreadsheet application for data file editing

### Testing and Validation
- **Manual Testing**: Run with sample CSV files
- **Visual Verification**: Check generated SVG output
- **Data Validation**: Verify CSV parsing and chip definitions
- **Symbol Testing**: Ensure all gate types render correctly