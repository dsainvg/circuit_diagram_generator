# Circuit Diagram Generator - Development Guidelines

## Code Quality Standards

### Documentation Patterns
- **Module-level docstrings**: Every Python file starts with triple-quoted module description
  ```python
  """Module for rendering SVG components"""
  ```
- **Class docstrings**: All classes have descriptive docstrings explaining their purpose
  ```python
  """Handles rendering of SVG elements for chips, inputs, and outputs"""
  ```
- **Method docstrings**: Public methods include clear descriptions of functionality
  ```python
  """Load SVG content from DB folder for a specific gate type"""
  ```

### Naming Conventions (5/5 files follow these patterns)
- **Classes**: PascalCase with descriptive names (`SVGCircuitGenerator`, `LayoutManager`)
- **Methods**: snake_case with action verbs (`load_data`, `create_chip_svg`, `intelligent_chip_placement`)
- **Variables**: snake_case with descriptive names (`chip_positions`, `gate_types`, `canvas_width`)
- **Constants**: UPPER_CASE for configuration values (`gate_height = 80`, `gate_spacing = 20`)
- **File names**: snake_case matching primary class purpose (`svg_renderer.py`, `data_loader.py`)

### Code Structure Standards
- **Single responsibility**: Each class handles one specific aspect (rendering, data loading, layout)
- **Consistent indentation**: 4-space indentation throughout all files
- **Line length**: Reasonable line lengths with logical breaks for readability
- **Import organization**: Standard library imports first, then local module imports

## Architectural Patterns

### Modular Design Pattern (Used in all 5 files)
- **Separation of concerns**: Each module handles distinct functionality
- **Dependency injection**: Classes accept dependencies in constructors
  ```python
  def __init__(self, symbol_manager, datasheets):
      self.symbol_manager = symbol_manager
      self.datasheets = datasheets
  ```

### Data Structure Patterns
- **Dictionary-based storage**: Consistent use of dictionaries for structured data
  ```python
  self.chips = {}
  self.pin_positions = {}
  chip_positions[chip_id] = {'x': layer_x, 'y': current_y}
  ```
- **List comprehensions**: Used for data transformation and filtering
  ```python
  input_pins = [int(p.strip()) for p in row['input_pins'].split(',')]
  ```

### Error Handling Patterns (4/5 files implement)
- **Graceful degradation**: Handle missing files with warnings
  ```python
  if not os.path.exists(svg_file):
      print(f"Warning: {svg_file} not found")
      return None
  ```
- **Try-catch blocks**: Wrap file operations and XML parsing
  ```python
  try:
      with open(svg_file, 'r', encoding='utf-8') as f:
          content = f.read()
  except Exception as e:
      print(f"Error loading {svg_file}: {e}")
  ```

## Implementation Patterns

### File I/O Patterns (3/5 files use these)
- **Context managers**: Always use `with` statements for file operations
  ```python
  with open(self.output_file, 'w', encoding='utf-8') as f:
      f.write(svg_content)
  ```
- **Explicit encoding**: Specify UTF-8 encoding for text files
- **CSV handling**: Use `csv.DictReader` for structured data parsing

### String Building Patterns (4/5 files implement)
- **List accumulation**: Build complex strings using list append and join
  ```python
  svg_parts = []
  svg_parts.append(f'<rect x="{x}" y="{y}" width="{width}"...')
  return '\n'.join(svg_parts)
  ```
- **F-string formatting**: Consistent use of f-strings for string interpolation
- **Multi-line strings**: Use triple quotes for complex string templates

### Mathematical Calculations (3/5 files use these patterns)
- **Coordinate transformations**: Scale from viewBox coordinates to canvas coordinates
  ```python
  scale_x = gate_width / 512
  pin_x = gate_x + pos['x'] * scale_x
  ```
- **Dimension calculations**: Dynamic sizing based on content
  ```python
  box_height = max(160, 80 + num_gates * (gate_height + gate_spacing))
  ```

## API Usage Patterns

### XML/SVG Processing (2/5 files implement)
- **ElementTree usage**: Standard pattern for XML parsing
  ```python
  import xml.etree.ElementTree as ET
  tree = ET.fromstring(content)
  path_elem = tree.find('.//{http://www.w3.org/2000/svg}path')
  ```
- **Namespace handling**: Graceful fallback for XML namespaces
- **Attribute extraction**: Safe attribute access with defaults

### CSV Processing (1/5 files implements)
- **DictReader pattern**: Standard approach for CSV parsing
  ```python
  with open(csv_file, 'r') as f:
      reader = csv.DictReader(f)
      for row in reader:
          # Process row data
  ```

### Static Method Usage (3/5 files use)
- **Utility functions**: Mark pure functions as static methods
  ```python
  @staticmethod
  def load_datasheets(datasheet_csv):
  ```

## Common Code Idioms

### Dictionary Operations (5/5 files use extensively)
- **Safe key access**: Check existence before accessing nested dictionaries
  ```python
  if chip_type in datasheets and gate_num in datasheets[chip_type]:
  ```
- **Dictionary comprehensions**: For data transformation
- **Nested dictionary initialization**: Pattern for hierarchical data

### List Processing (4/5 files implement)
- **Enumeration**: Use `enumerate()` for index-value pairs
  ```python
  for idx, output_data in enumerate(outputs):
  ```
- **Sorting**: Sort dictionary keys for consistent ordering
  ```python
  for gate_num in sorted(all_gates.keys()):
  ```

### Conditional Logic Patterns
- **Early returns**: Exit functions early on invalid conditions
  ```python
  if not outputs:
      return ""
  ```
- **Ternary operations**: Use for simple conditional assignments
- **Guard clauses**: Validate inputs at function start

## Configuration and Constants

### Magic Number Elimination (5/5 files follow)
- **Named constants**: Replace magic numbers with descriptive variables
  ```python
  gate_height = 80
  gate_spacing = 20
  input_size = 40
  ```
- **Calculation transparency**: Show how dimensions are derived
- **Consistent spacing**: Use same spacing values across related components