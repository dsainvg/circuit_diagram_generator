# Circuit Diagram Generator - Development Guidelines

## Code Quality Standards

### Documentation Patterns
- **Module docstrings**: Every Python file starts with triple-quoted module description
- **Class docstrings**: All classes have descriptive docstrings explaining their purpose
- **Method docstrings**: Public methods include docstrings with parameter and return descriptions
- **Inline comments**: Complex algorithms include step-by-step explanations (especially in channel_router.py)

### Code Formatting and Structure
- **Consistent indentation**: 4-space indentation throughout all Python files
- **Line length**: Generally kept under 100 characters with logical line breaks
- **Blank lines**: Strategic use of blank lines to separate logical sections
- **Import organization**: Standard library imports first, then third-party, then local modules

### Naming Conventions
- **Classes**: PascalCase (e.g., `SVGRenderer`, `ChannelRouter`, `DataLoader`)
- **Methods/Functions**: snake_case (e.g., `load_datasheets`, `create_chip_svg`, `route_net`)
- **Variables**: snake_case with descriptive names (e.g., `chip_positions`, `canvas_width`, `gate_height`)
- **Constants**: UPPER_SNAKE_CASE for configuration values (e.g., `USE_PYQT`)
- **Private methods**: Leading underscore (e.g., `_create_svg_path`, `_find_pixel_escape`)

## Architectural Patterns

### Manager Pattern Implementation
- **Dedicated managers**: Separate manager classes for distinct responsibilities
  - `DataLoader`: CSV file processing and validation
  - `SVGSymbolManager`: Symbol library management
  - `LayoutManager`: Chip positioning algorithms
  - `ChannelRouter`: Wire routing and pathfinding
  - `SVGRenderer`: Final SVG generation

### Dependency Injection
- **Constructor injection**: Managers passed to main orchestrator in constructor
- **Optional dependencies**: Router can be injected or created on-demand in SVGRenderer
- **Configuration through parameters**: Canvas dimensions, spacing, and other settings passed as parameters

### Error Handling Strategies
- **Graceful degradation**: Multiple fallback strategies in routing algorithms
- **Validation with feedback**: Input validation with descriptive error messages
- **Exception handling**: Try-catch blocks for file operations and library imports
- **Fallback mechanisms**: Alternative rendering approaches when primary methods fail

## Data Processing Patterns

### CSV Processing Standards
- **DictReader usage**: Consistent use of `csv.DictReader` for column-based access
- **Type conversion**: Explicit conversion of string data to appropriate types (int, float)
- **Data validation**: Checking for required fields and valid data ranges
- **Structured return**: Methods return structured dictionaries or tuples with clear schemas

### State Management
- **Centralized state**: Main generator class holds all circuit data
- **Position tracking**: `pin_positions` dictionary maintains coordinate mappings
- **Grid state**: Router maintains grid occupancy and wire placement state
- **Immutable data flow**: Data loaded once and passed through processing pipeline

## Rendering and Graphics Patterns

### SVG Generation Approach
- **String concatenation**: Direct SVG markup generation using string operations
- **Template patterns**: Consistent SVG element structure with parameter substitution
- **Coordinate systems**: 2D Cartesian coordinates with consistent origin handling
- **Scaling calculations**: Proportional scaling from symbol viewBox to actual dimensions

### Symbol Management
- **Reusable definitions**: SVG `<defs>` section for symbol reuse
- **Inline fallbacks**: Direct path rendering when symbol references fail
- **Coordinate transformation**: Proper scaling and translation for symbol placement
- **Color management**: Consistent color schemes with net-based wire coloring

## Algorithm Implementation Patterns

### Routing Algorithms
- **A* pathfinding**: Grid-based pathfinding with heuristic optimization
- **Multi-strategy approach**: Primary algorithm with fallback strategies
- **Obstacle avoidance**: Strict boundary checking with escape mechanisms
- **Path optimization**: Post-processing to remove redundant waypoints and cycles

### Layout Algorithms
- **Layer-based placement**: Horizontal layers with vertical stacking within layers
- **Dynamic sizing**: Canvas dimensions calculated based on content requirements
- **Spacing calculations**: Consistent spacing formulas for visual balance
- **Collision detection**: Boundary checking to prevent overlapping elements

## Configuration and Extensibility

### Parameterization Patterns
- **Constructor parameters**: Key settings passed during object initialization
- **Default values**: Sensible defaults with override capability
- **Configuration constants**: Named constants for spacing, sizing, and visual parameters
- **File path flexibility**: Configurable input and output file paths

### Extension Points
- **Symbol library**: Easy addition of new gate types through SVG files
- **Routing strategies**: Pluggable routing algorithms with common interface
- **Output formats**: Multiple export formats through converter modules
- **Data sources**: Extensible data loading for different input formats

## Testing and Validation Patterns

### Input Validation
- **File existence checks**: Verify input files exist before processing
- **Data integrity**: Validate CSV structure and required fields
- **Range checking**: Ensure numeric values are within expected ranges
- **Relationship validation**: Verify connections reference valid chips and pins

### Error Reporting
- **Descriptive messages**: Clear error descriptions with context information
- **Progress feedback**: Status messages during long-running operations
- **Failure tracking**: Collection and reporting of failed operations
- **Debug information**: Detailed logging for troubleshooting complex routing issues

## Performance Optimization

### Efficiency Strategies
- **Symbol caching**: Load and cache SVG symbols once for reuse
- **Grid optimization**: Efficient grid-based algorithms for spatial operations
- **Path reuse**: Encourage wire path sharing for same-net connections
- **Memory management**: Minimal object creation during rendering operations

### Scalability Considerations
- **Dynamic canvas sizing**: Automatic adjustment for circuit complexity
- **Efficient data structures**: Appropriate data structures for different operations
- **Algorithmic complexity**: Consideration of performance for large circuits
- **Resource cleanup**: Proper cleanup of graphics resources and file handles