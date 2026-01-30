# Circuit Diagram Generator - User Guide

## Overview

The Circuit Diagram Generator creates SVG circuit diagrams from CSV input files. It supports various component types including logic gates, custom IC packages, displays, resistors, and capacitors.

## Input Files Required

The system requires three CSV files:

1. **chips.csv** - Defines all chip instances in your circuit
2. **connections.csv** - Defines all connections between components
3. **chip_datasheets.csv** - Defines chip types and their pin configurations

## File Formats

### 1. chips.csv

Defines individual chip instances in the circuit.

**Format:**
```csv
chip_id,chip_type,gate_num,layer
```

**Columns:**
- `chip_id`: Unique identifier for this chip instance (e.g., U1, U2, R1, C1)
- `chip_type`: Type of chip from datasheets (e.g., 4011, 74LS47, R10K, C100N)
- `gate_num`: Which gate/unit within the chip (usually 1 for single-gate chips)
- `layer`: Layer number for layout positioning (1, 2, 3, etc.)

**Example:**
```csv
chip_id,chip_type,gate_num,layer
U1,4011,1,1
U2,4011,2,1
R1,R10K,1,1
C1,C100N,1,2
U3,74LS47,1,2
```

### 2. connections.csv

Defines all connections between components, inputs, outputs, and displays.

**Format:**
```csv
from_chip,from_pin,to_chip,to_pin
```

**Connection Types:**

#### a) Input to Chip
```csv
from_chip,from_pin,to_chip,to_pin
input,A,U1,1
input,B,U1,2
```
- `from_chip`: `input` (keyword)
- `from_pin`: Input name (e.g., A, B, CLK, DATA)
- `to_chip`: Destination chip ID
- `to_pin`: Destination pin number

#### b) Chip to Chip
```csv
from_chip,from_pin,to_chip,to_pin
U1,3,U2,1
R1,2,C1,1
```
- `from_chip`: Source chip ID
- `from_pin`: Source pin number
- `to_chip`: Destination chip ID
- `to_pin`: Destination pin number

#### c) Chip to Output (LED)
```csv
from_chip,from_pin,to_chip,to_pin
U2,3,output,LED1
```
- `from_chip`: Source chip ID
- `from_pin`: Source pin number
- `to_chip`: `output` (keyword)
- `to_pin`: Output name (e.g., LED1, OUT, Q)

#### d) Chip to Display (7-segment)
```csv
from_chip,from_pin,to_chip,to_pin
U3,13,display,DISP1_a
U3,12,display,DISP1_b
U3,11,display,DISP1_c
```
- `from_chip`: Source chip ID
- `from_pin`: Source pin number
- `to_chip`: `display` (keyword)
- `to_pin`: Display name + segment (format: `DISPLAYNAME_segment`)
  - Segments: a, b, c, d, e, f, g (standard 7-segment labels)

**Complete Example:**
```csv
from_chip,from_pin,to_chip,to_pin
input,VCC,R1,1
R1,2,C1,1
C1,2,U1,1
input,A,U1,2
U1,3,U2,1
U2,3,output,LED1
U3,13,display,DISP1_a
U3,12,display,DISP1_b
```

### 3. chip_datasheets.csv

Defines chip types and their specifications.

**Format:**
```csv
chip_type,gate_num,input_pins,output_pin,gate_type,vcc_pin,gnd_pin,total_pins,description
```

**Columns:**
- `chip_type`: Chip type identifier (e.g., 4011, 74LS47, R10K)
- `gate_num`: Gate/unit number within this chip type
- `input_pins`: Input pin numbers (comma-separated in quotes for multiple: `"1,2"`)
- `output_pin`: Output pin number
- `gate_type`: Visual representation type (see Component Types below)
- `vcc_pin`: Power supply pin number
- `gnd_pin`: Ground pin number
- `total_pins`: Total number of pins on the package
- `description`: Human-readable description

**Component Types (gate_type):**

#### Standard Logic Gates
- `NAND2`: 2-input NAND gate
- `NOR2`: 2-input NOR gate
- `AND2`: 2-input AND gate
- `OR2`: 2-input OR gate
- `XOR2`: 2-input XOR gate
- `NOT1`: Inverter (1 input)

#### Custom IC Packages
- `IC8`: 8-pin DIP package (dual inline package)
- `IC14`: 14-pin DIP package
- `IC16`: 16-pin DIP package

Use these for complex ICs like decoders, multiplexers, timers, etc.

#### Passive Components
- `RESISTOR`: Resistor symbol (zigzag line)
- `CAPACITOR`: Capacitor symbol (parallel plates)

**Examples:**

```csv
chip_type,gate_num,input_pins,output_pin,gate_type,vcc_pin,gnd_pin,total_pins,description
4011,1,"1,2",3,NAND2,14,7,14,Quad 2-input NAND
4011,2,"5,6",4,NAND2,14,7,14,Quad 2-input NAND
4011,3,"8,9",10,NAND2,14,7,14,Quad 2-input NAND
4011,4,"12,13",11,NAND2,14,7,14,Quad 2-input NAND
74LS47,1,"1,2,6",13,IC16,16,8,16,BCD to 7-Segment Decoder
555,1,"2,5",3,IC8,8,1,8,Timer IC
R10K,1,1,2,RESISTOR,3,3,2,10K Resistor
C100N,1,1,2,CAPACITOR,3,3,2,100nF Capacitor
```

**Notes for Multi-Gate Chips:**
- Define each gate separately with its own `gate_num`
- All gates share the same `vcc_pin`, `gnd_pin`, and `total_pins`
- Example: 4011 has 4 NAND gates, so define rows with gate_num 1-4

**Notes for Passive Components:**
- Set `vcc_pin` and `gnd_pin` to 3 (or any value > total_pins) to indicate no power pins
- VCC/GND labels won't be displayed for RESISTOR and CAPACITOR types

## Component Type Selection Guide

### When to use Standard Gates (NAND2, OR2, etc.):
- Simple logic gates with clear gate symbols
- When you want traditional gate representation
- Multiple gates from the same chip package (e.g., quad NAND)

### When to use IC Packages (IC8, IC14, IC16):
- Complex chips (decoders, multiplexers, counters, timers)
- When you want to show the full DIP package with pin numbers
- Custom chips with many input/output pins
- When physical pin layout matters

### When to use Passive Components (RESISTOR, CAPACITOR):
- Resistors and capacitors
- Any two-terminal passive component
- No power supply needed

## Running the Generator

### Method 1: Python Script
```python
from circuit_generator import SVGCircuitGenerator

generator = SVGCircuitGenerator(
    chips_csv="I-O/chips.csv",
    connections_csv="I-O/connections.csv",
    datasheet_csv="I-O/chip_datasheets.csv",
    output_file="I-O/outputs/circuit_diagram.svg"
)
generator.generate_circuit()
```

### Method 2: Command Line
```bash
python -c "from circuit_generator import SVGCircuitGenerator; g = SVGCircuitGenerator('I-O/chips.csv', 'I-O/connections.csv', 'I-O/chip_datasheets.csv', 'I-O/outputs/circuit.svg'); g.generate_circuit()"
```

## Complete Examples

### Example 1: Simple RC Circuit with Logic Gate

**chips.csv:**
```csv
chip_id,chip_type,gate_num,layer
R1,R10K,1,1
C1,C100N,1,2
U1,4011,1,1
```

**connections.csv:**
```csv
from_chip,from_pin,to_chip,to_pin
input,VCC,R1,1
R1,2,C1,1
C1,2,U1,1
input,GND,U1,2
U1,3,output,OUT
```

**chip_datasheets.csv:**
```csv
chip_type,gate_num,input_pins,output_pin,gate_type,vcc_pin,gnd_pin,total_pins,description
4011,1,"1,2",3,NAND2,14,7,14,Quad 2-input NAND
R10K,1,1,2,RESISTOR,3,3,2,10K Resistor
C100N,1,1,2,CAPACITOR,3,3,2,100nF Capacitor
```

### Example 2: 7-Segment Display with Decoder

**chips.csv:**
```csv
chip_id,chip_type,gate_num,layer
U1,74LS47,1,1
```

**connections.csv:**
```csv
from_chip,from_pin,to_chip,to_pin
input,A,U1,1
input,B,U1,2
U1,13,display,DISP1_a
U1,12,display,DISP1_b
U1,11,display,DISP1_c
U1,10,display,DISP1_d
U1,9,display,DISP1_e
U1,15,display,DISP1_f
U1,14,display,DISP1_g
```

**chip_datasheets.csv:**
```csv
chip_type,gate_num,input_pins,output_pin,gate_type,vcc_pin,gnd_pin,total_pins,description
74LS47,1,"1,2,6",13,IC16,16,8,16,BCD to 7-Segment Decoder
74LS47,2,"1,2,6",12,IC16,16,8,16,BCD to 7-Segment Decoder
74LS47,3,"1,2,6",11,IC16,16,8,16,BCD to 7-Segment Decoder
74LS47,4,"1,2,6",10,IC16,16,8,16,BCD to 7-Segment Decoder
74LS47,5,"1,2,6",9,IC16,16,8,16,BCD to 7-Segment Decoder
74LS47,6,"1,2,6",15,IC16,16,8,16,BCD to 7-Segment Decoder
74LS47,7,"1,2,6",14,IC16,16,8,16,BCD to 7-Segment Decoder
```

### Example 3: 555 Timer Circuit

**chips.csv:**
```csv
chip_id,chip_type,gate_num,layer
U1,555,1,1
```

**connections.csv:**
```csv
from_chip,from_pin,to_chip,to_pin
input,VCC,U1,8
input,GND,U1,1
input,TRIG,U1,2
input,CTRL,U1,5
U1,3,output,OUT
U1,6,output,THR
U1,7,output,DIS
```

**chip_datasheets.csv:**
```csv
chip_type,gate_num,input_pins,output_pin,gate_type,vcc_pin,gnd_pin,total_pins,description
555,1,"2,5",3,IC8,8,1,8,Timer IC
```

## Output

The generator creates an SVG file containing:
- **Input box**: All circuit inputs on the left
- **Chip boxes**: Each chip with its gates/symbols and pin numbers
- **Output box**: LED outputs on the right
- **Display module**: 7-segment displays on the right (below outputs)
- **Wire routing**: Automatically routed connections between components

## Tips and Best Practices

1. **Unique IDs**: Use unique chip_id for each instance (U1, U2, R1, C1, etc.)

2. **Pin Numbers**: Always verify pin numbers match the actual chip datasheet

3. **Layer Assignment**: Use different layers to help with horizontal positioning
   - Layer 1: Leftmost chips
   - Layer 2: Middle chips
   - Layer 3: Rightmost chips

4. **Display Naming**: Use format `DISPLAYNAME_segment` for displays
   - Example: DISP1_a, DISP1_b, DISP2_a, etc.

5. **Multiple Displays**: Can have multiple displays (DISP1, DISP2, etc.)
   - Each will render separately in the display module

6. **Passive Components**: Don't need VCC/GND connections
   - System automatically hides power labels for RESISTOR and CAPACITOR types

7. **Custom ICs**: For complex chips, use IC8/IC14/IC16 types
   - These render as DIP packages with visible pin layout
   - Better for chips with many pins or irregular pin assignments

## Troubleshooting

### "Source pin not found" errors
- Check that the pin number exists in the chip datasheet
- Verify the chip_id is defined in chips.csv
- Ensure gate_num matches between chips.csv and chip_datasheets.csv

### Components not visible
- Verify gate_type is defined and SVG file exists in DB/ folder
- Check that chip_type exists in chip_datasheets.csv

### No VCC/GND labels showing
- This is normal for RESISTOR and CAPACITOR types
- For other chips, verify vcc_pin and gnd_pin are set correctly

### Display not showing
- Verify display connections use format: `DISPLAYNAME_segment`
- Ensure segments are a-g (lowercase)
- Check that 7Segment.svg exists in DB/ folder

## File Locations

- **Input CSV files**: `I-O/` folder
- **Output SVG files**: `I-O/outputs/` folder
- **Component symbols**: `DB/` folder (.svg files)
- **Documentation**: `docs/` folder

## Adding New Component Types

To add a new component symbol:

1. Create SVG file in `DB/` folder (e.g., `DB/INDUCTOR.svg`)
2. Use viewBox "0 0 512 512" for consistency
3. Define the component in chip_datasheets.csv with the new gate_type
4. The system will automatically load and use it

SVG requirements:
- Must contain a `<path>` element with `d` attribute
- Can use `fill` and `stroke` attributes for styling
- Will be scaled to fit gate box (80x80 pixels by default)
