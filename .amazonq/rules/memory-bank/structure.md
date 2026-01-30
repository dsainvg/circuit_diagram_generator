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
│   ├── IC14.svg, IC16.svg          # IC package symbols
│   └── LED.svg                     # Output indicator
├── outputs/                        # Generated diagram outputs
├── *.py                           # Core Python modules
├── *.csv                          # Circuit definition files
└── *.md                           # Documentation files
```

## Core Components and Relationships

### Main Orchestrator
- **circuit_generator.py**: Primary entry point and workflow coordinator
  - Initializes all subsystem managers
  - Orchestrates the complete generation pipeline
  - Handles file I/O and error management

### Data Management Layer
- **data_loader.py**: CSV file parsing and data validation
  - Loads chip definitions from chips.csv
  - Processes connection data from connections.csv
  - Integrates datasheet information from chip_datasheets.csv
  - Validates data integrity and relationships

### Symbol and Asset Management
- **svg_symbol_manager.py**: SVG symbol library management
  - Loads and caches gate symbols from DB/ folder
  - Creates reusable SVG definitions
  - Manages symbol scaling and positioning

### Layout and Positioning
- **layout_manager.py**: Intelligent chip placement algorithms
  - Calculates optimal chip positions on canvas
  - Minimizes connection crossings
  - Handles canvas sizing and spacing

### Routing System
- **channel_router.py**: Advanced wire routing algorithms
  - Implements multiple routing strategies
  - Handles connection conflicts and optimization
  - Manages channel allocation and spacing

### Rendering Engine
- **svg_renderer.py**: SVG generation and visual output
  - Creates final SVG markup
  - Renders chips, connections, and annotations
  - Handles styling and visual formatting

### Format Conversion
- **svg_to_png.py**: Output format conversion utilities
  - Converts SVG to PNG using cairosvg
  - Handles image quality and sizing options

## Architectural Patterns

### Modular Design
- **Separation of Concerns**: Each module handles a specific aspect of diagram generation
- **Manager Pattern**: Dedicated manager classes for different subsystems
- **Pipeline Architecture**: Sequential processing stages with clear interfaces

### Data Flow Architecture
1. **Input Stage**: CSV files → DataLoader → Structured data
2. **Processing Stage**: Layout calculation → Symbol management → Routing
3. **Rendering Stage**: SVG generation → Format conversion → Output files

### Component Interactions
- **Loose Coupling**: Modules communicate through well-defined interfaces
- **Dependency Injection**: Managers are injected into the main orchestrator
- **State Management**: Centralized state in the main generator class

## Configuration Files

### Circuit Definition Files
- **chips.csv**: IC chip specifications and properties
- **connections.csv**: Inter-chip connection definitions  
- **chip_datasheets.csv**: Detailed IC pin mappings and gate arrangements

### Symbol Library
- **DB/ folder**: SVG symbol definitions for all supported gate types
- Standardized naming convention matching gate_type field in chips.csv
- Scalable vector graphics for high-quality rendering

## Output Structure
- **circuit_diagram.svg**: Primary SVG output file
- **outputs/ folder**: Directory for generated diagrams and variants
- **PNG conversion**: Optional raster format output for documentation