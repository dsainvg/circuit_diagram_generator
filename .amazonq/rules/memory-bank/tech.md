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

### Optional Dependencies
- **PyQt5**: Alternative SVG rendering backend
  - QSvgRenderer for SVG processing
  - QImage and QPainter for image generation
  - Fallback option when cairosvg is unavailable

### Standard Library Modules
- **csv**: CSV file parsing and processing
- **os**: File system operations and path handling
- **sys**: System-specific parameters and functions
- **math**: Mathematical calculations for positioning and routing
- **heapq**: Priority queue implementation for A* pathfinding
- **typing**: Type hints for better code documentation

## Build System and Development

### Installation
```bash
pip install cairosvg pillow
# Optional: pip install PyQt5
```

### Development Commands
```bash
# Generate circuit diagram (default configuration)
python circuit_generator.py

# Run with Windows batch file
run_circuit.bat

# Test custom IC integration
python circuit_generator.py --test custom

# Convert SVG to PNG
python svg_to_png.py
```

### File Formats and Standards
- **Input**: CSV files with specific column schemas
- **Output**: SVG 1.1 compliant vector graphics
- **Symbols**: SVG symbol library in DB/ folder
- **Encoding**: UTF-8 for all text files
- **Configuration**: Batch files for Windows automation

## Architecture Technologies

### Design Patterns
- **Manager Pattern**: Separate managers for different subsystems
- **Factory Pattern**: Symbol creation and management
- **Strategy Pattern**: Multiple routing algorithms in channel_router
- **Pipeline Pattern**: Sequential data processing stages

### Data Processing
- **CSV Processing**: Native Python csv module with DictReader
- **Data Validation**: Custom validation logic for circuit integrity
- **Caching**: In-memory caching of loaded symbols and processed data
- **Type Conversion**: Explicit string-to-numeric conversions

### Graphics and Rendering
- **SVG Generation**: Direct XML string construction for SVG output
- **Coordinate Systems**: 2D Cartesian coordinates for positioning
- **Vector Graphics**: Scalable symbols and connection paths
- **Channel Routing**: Grid-based routing algorithms with A* pathfinding
- **Multi-backend Support**: Flexible rendering with cairosvg or PyQt5

## Development Environment

### File Structure Requirements
- **DB/ folder**: Must contain all required SVG symbol files
- **I-O/ folder**: Input/output data and test configurations
- **docs/ folder**: Comprehensive documentation and guides
- **CSV files**: Must follow documented schema formats

### Configuration Management
- **Hardcoded defaults**: Default file names and paths in main script
- **Parameter injection**: Constructor-based configuration for managers
- **CSV-driven configuration**: Circuit topology defined in data files
- **Test configurations**: Multiple CSV sets for different scenarios

### Error Handling
- **Validation**: Input data validation with descriptive error messages
- **Graceful degradation**: Fallback routing strategies for complex layouts
- **File I/O protection**: Exception handling for file operations
- **Import fallbacks**: Multiple library options for SVG processing

## Performance Considerations

### Optimization Strategies
- **Symbol caching**: Load and cache SVG symbols once for reuse
- **Grid optimization**: Efficient grid-based algorithms for spatial operations
- **Path reuse**: Encourage wire path sharing for same-net connections
- **Memory management**: Minimal object creation during rendering

### Scalability
- **Dynamic canvas sizing**: Automatic adjustment based on circuit complexity
- **Efficient data structures**: Appropriate data structures for different operations
- **Algorithmic complexity**: A* pathfinding with heuristic optimization
- **Resource cleanup**: Proper cleanup of graphics resources and file handles

### Testing and Validation
- **Multiple test scenarios**: Comprehensive test suite with different circuit types
- **Output validation**: Generated diagrams stored for comparison
- **Performance monitoring**: Routing success rates and failure tracking
- **Cross-platform compatibility**: Windows batch files and Python portability