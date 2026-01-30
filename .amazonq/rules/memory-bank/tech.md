# Circuit Diagram Generator - Technology Stack

## Programming Languages and Versions

### Primary Language
- **Python 3.x**: Core implementation language
  - Object-oriented design with class-based architecture
  - Standard library usage for file I/O and data processing
  - Type hints and docstrings for code documentation

## Core Dependencies

### Required Packages
- **cairosvg**: SVG to PNG conversion library
  - Handles rasterization of vector graphics
  - Provides high-quality image output
- **Pillow (PIL)**: Python Imaging Library
  - Image processing and manipulation
  - Format conversion support

### Standard Library Modules
- **csv**: CSV file parsing and processing
- **os**: File system operations and path handling
- **math**: Mathematical calculations for positioning and routing
- **xml.etree.ElementTree**: XML/SVG parsing and manipulation (if used)

## Build System and Development

### Installation
```bash
pip install cairosvg pillow
```

### Development Commands
```bash
# Generate circuit diagram
python circuit_generator.py

# Run with custom files
python circuit_generator.py --chips custom_chips.csv --connections custom_connections.csv
```

### File Formats and Standards
- **Input**: CSV files with specific column schemas
- **Output**: SVG 1.1 compliant vector graphics
- **Symbols**: SVG symbol library in DB/ folder
- **Encoding**: UTF-8 for all text files

## Architecture Technologies

### Design Patterns
- **Manager Pattern**: Separate managers for different subsystems
- **Factory Pattern**: Symbol creation and management
- **Strategy Pattern**: Multiple routing algorithms in channel_router
- **Pipeline Pattern**: Sequential data processing stages

### Data Processing
- **CSV Processing**: Native Python csv module for data ingestion
- **Data Validation**: Custom validation logic for circuit integrity
- **Caching**: In-memory caching of loaded symbols and processed data

### Graphics and Rendering
- **SVG Generation**: Direct XML string construction for SVG output
- **Coordinate Systems**: 2D Cartesian coordinates for positioning
- **Vector Graphics**: Scalable symbols and connection paths
- **Channel Routing**: Grid-based routing algorithms for wire placement

## Development Environment

### File Structure Requirements
- **DB/ folder**: Must contain all required SVG symbol files
- **CSV files**: Must follow documented schema formats
- **Output directory**: Configurable output location for generated files

### Configuration Management
- **Hardcoded defaults**: Default file names and paths in main script
- **Parameter injection**: Constructor-based configuration for managers
- **CSV-driven configuration**: Circuit topology defined in data files

### Error Handling
- **Validation**: Input data validation with descriptive error messages
- **Graceful degradation**: Fallback routing strategies for complex layouts
- **File I/O protection**: Exception handling for file operations

## Performance Considerations

### Optimization Strategies
- **Symbol reuse**: SVG definitions prevent symbol duplication
- **Efficient routing**: Multiple algorithm strategies for optimal performance
- **Memory management**: Minimal object creation during rendering

### Scalability
- **Canvas sizing**: Dynamic canvas adjustment based on circuit complexity
- **Connection handling**: Efficient algorithms for large numbers of connections
- **Symbol library**: Extensible symbol system for new gate types