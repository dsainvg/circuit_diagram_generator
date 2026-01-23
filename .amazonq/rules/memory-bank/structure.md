# Circuit Diagram Generator - Project Structure

## Directory Structure

```
circuit_diagram_generator/
├── .amazonq/rules/memory-bank/     # Documentation and rules
├── DB/                             # SVG symbol library
│   ├── AND2.svg, AND3.svg, AND4.svg
│   ├── OR2.svg, OR3.svg, OR4.svg
│   ├── NAND2.svg, NAND3.svg, NAND4.svg
│   ├── NOR2.svg, NOR3.svg, NOR4.svg
│   ├── NOT1.svg, XOR2.svg, NXOR2.svg
│   └── LED.svg
├── circuit_generator.py            # Main orchestrator class
├── data_loader.py                  # CSV data parsing and validation
├── svg_symbol_manager.py           # SVG symbol loading and management
├── layout_manager.py               # Chip positioning and layout algorithms
├── svg_renderer.py                 # SVG generation and rendering
├── chips.csv                       # Circuit chip definitions
├── connections.csv                 # Inter-chip connections
├── chip_datasheets.csv            # IC pinout and gate specifications
├── circuit_diagram.svg            # Generated output file
└── README.md                       # User documentation
```

## Core Components and Relationships

### 1. Main Orchestrator (`circuit_generator.py`)
- **SVGCircuitGenerator**: Central coordinator class
- **Responsibilities**: Workflow orchestration, data integration, output generation
- **Dependencies**: All other modules (data_loader, svg_symbol_manager, layout_manager, svg_renderer)
- **Key Methods**: `load_data()`, `generate_circuit()`, `calculate_chip_height()`

### 2. Data Management Layer
- **DataLoader** (`data_loader.py`): CSV parsing and data validation
- **Input Processing**: Handles chips.csv, connections.csv, chip_datasheets.csv
- **Data Structures**: Converts CSV data into Python dictionaries and lists
- **Validation**: Ensures data integrity and completeness

### 3. Symbol Management (`svg_symbol_manager.py`)
- **SVGSymbolManager**: Manages reusable SVG gate symbols
- **Symbol Library**: Loads and caches SVG definitions from DB/ folder
- **Reusability**: Creates SVG `<defs>` sections for efficient rendering
- **Gate Types**: Supports all standard logic gates and visual elements

### 4. Layout Engine (`layout_manager.py`)
- **LayoutManager**: Calculates optimal chip positioning
- **Algorithms**: Intelligent placement to minimize wire crossings
- **Canvas Sizing**: Determines optimal diagram dimensions
- **Spatial Optimization**: Arranges components for visual clarity

### 5. Rendering Engine (`svg_renderer.py`)
- **SVGRenderer**: Generates final SVG markup
- **Component Rendering**: Creates chip instances, input/output boxes
- **Visual Styling**: Applies consistent formatting and styling
- **Pin Management**: Tracks pin positions for connection routing

## Architectural Patterns

### Modular Design
- **Separation of Concerns**: Each module handles a specific aspect of diagram generation
- **Loose Coupling**: Modules interact through well-defined interfaces
- **Single Responsibility**: Each class has a focused, specific purpose

### Data Flow Architecture
1. **Input Stage**: CSV files → DataLoader → Structured data
2. **Processing Stage**: Data + Symbols → LayoutManager → Positioned components
3. **Rendering Stage**: Positioned components → SVGRenderer → SVG output
4. **Orchestration**: SVGCircuitGenerator coordinates all stages

### Configuration-Driven Design
- **CSV Configuration**: Circuit topology defined in external files
- **Symbol Library**: Gate symbols stored as reusable SVG files
- **Datasheet Mapping**: IC specifications in structured CSV format

### Extensibility Points
- **New Gate Types**: Add SVG files to DB/ folder
- **IC Support**: Extend chip_datasheets.csv with new IC types
- **Layout Algorithms**: Modify LayoutManager for different positioning strategies
- **Output Formats**: Extend SVGRenderer for additional output types