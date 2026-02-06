# Circuit Diagram Generator

This tool generates circuit diagrams from CSV files and outputs a single PNG image.

## CSV File Formats

### chips.csv
Defines the IC chips used in the circuit:

| Column | Description | Example |
|--------|-------------|---------|
| chip_id | Unique identifier for the chip | U1, U2, U3 |
| chip_type | IC chip model number | 7408, 7432, 7404 |
| gate_type | Type of gate (matches SVG filename) | AND2, OR2, NOT1 |
| num_gates | Number of gates in the chip | 4, 6 |
| vcc_pin | Power supply pin number | 14 |
| gnd_pin | Ground pin number | 7 |
| total_pins | Total number of pins on the chip | 14 |

**Common IC Chips:**
- 7408: Quad 2-input AND gates (4 gates, 14 pins, VCC=14, GND=7)
- 7432: Quad 2-input OR gates (4 gates, 14 pins, VCC=14, GND=7)
- 7404: Hex inverters (6 NOT gates, 14 pins, VCC=14, GND=7)
- 7400: Quad 2-input NAND gates (4 gates, 14 pins, VCC=14, GND=7)
- 7486: Quad 2-input XOR gates (4 gates, 14 pins, VCC=14, GND=7)
- 74LS153: Dual 4-to-1 multiplexers (2 MUX4 gates, 16 pins, VCC=16, GND=8)
- 74LS157: Quad 2-to-1 multiplexers (4 MUX2 gates, 16 pins, VCC=16, GND=8)

### connections.csv
Defines the connections between chips:

| Column | Description | Example |
|--------|-------------|---------|
| from_chip | Source chip ID | U1 |
| from_pin | Output pin number on source chip | 3 |
| to_chip | Destination chip ID | U2 |
| to_pin | Input pin number on destination chip | 1 |

## Available Gate Types (SVG files in DB folder)

- AND2, AND3, AND4: 2, 3, 4-input AND gates
- OR2, OR3, OR4: 2, 3, 4-input OR gates
- NAND2, NAND3, NAND4: 2, 3, 4-input NAND gates
- NOR2, NOR3, NOR4: 2, 3, 4-input NOR gates
- NOT1: Inverter (NOT gate)
- XOR2: 2-input XOR gate
- NXOR2: 2-input XNOR gate
- MUX2: 2-to-1 Multiplexer
- MUX4: 4-to-1 Multiplexer

## Multiplexer (MUX) Support

The circuit generator supports MUX2 and MUX4 gates with special handling for select and enable pins.

### Supported MUX Chips

#### 74LS153 - Dual 4-to-1 Multiplexer
- 2 independent MUX4 gates per chip
- Shared select pins: S0 (pin 14) and S1 (pin 2)
- Individual enable pins: E_a (pin 1) for MUX A, E_b (pin 15) for MUX B
- Pin configuration:
  - Gate 1 (MUX A): Inputs I0-I3 (pins 6,5,4,3), Output (pin 7)
  - Gate 2 (MUX B): Inputs I0-I3 (pins 10,11,12,13), Output (pin 9)

#### 74LS157 - Quad 2-to-1 Multiplexer
- 4 independent MUX2 gates per chip
- Shared select pin: A/B (pin 1)
- Shared enable pin: G (pin 15)
- Pin configuration:
  - Gate 1: Inputs A,B (pins 2,3), Output (pin 4)
  - Gate 2: Inputs A,B (pins 5,6), Output (pin 7)
  - Gate 3: Inputs A,B (pins 14,13), Output (pin 12)
  - Gate 4: Inputs A,B (pins 11,10), Output (pin 9)

### Using MUX Gates in chip_datasheets.csv

MUX gates require special entries for SELECT and ENABLE pins:

```csv
chip_type,gate_num,input_pins,output_pin,gate_type,vcc_pin,gnd_pin,total_pins,description
74LS153,1,"6,5,4,3",7,MUX4,16,8,16,Dual 4-to-1 Multiplexer A
74LS153,2,"10,11,12,13",9,MUX4,16,8,16,Dual 4-to-1 Multiplexer B
74LS153,3,2,2,SELECT,16,8,16,Select S1 (shared)
74LS153,4,14,14,SELECT,16,8,16,Select S0 (shared)
74LS153,5,1,1,ENABLE,16,8,16,Enable E_a for Gate 1
74LS153,6,15,15,ENABLE,16,8,16,Enable E_b for Gate 2
```

**Important Notes:**
- **SELECT pins** are rendered as connection points (purple circles) aligned vertically inside the chip box below the gates. These can be connected from your connections.csv file.
- **ENABLE pins** are rendered as text labels (like VCC/GND) at the bottom of the chip. These are informational only and should NOT be connected in connections.csv.
- Each MUX gate shows its data input pins (2 for MUX2, 4 for MUX4) on the left side and output on the right side.

### Example MUX Usage

**chips.csv:**
```csv
chip_id,chip_type,gate_num,layer
U1,74LS153,1,1
U1,74LS153,2,1
U2,74LS157,1,2
U2,74LS157,2,2
```

**connections.csv:**
```csv
from_chip,from_pin,to_chip,to_pin
INPUT,A,U1,6
INPUT,B,U1,5
INPUT,S0,U1,14
INPUT,S1,U1,2
U1,7,OUTPUT,OUT1
INPUT,X,U2,2
INPUT,Y,U2,3
INPUT,SEL,U2,1
U2,4,OUTPUT,OUT2
```

**Note:** Do NOT connect to ENABLE pins (pins 1, 15 for 74LS153 or pin 15 for 74LS157) - these are display-only labels.

## Installation

Install required dependencies:
```bash
pip install cairosvg pillow
```

## Usage

1. Create or edit `chips.csv` with your chip definitions
2. Create or edit `connections.csv` with your connections
3. Run the generator:
```bash
python circuit_generator.py
```

The output will be saved as `circuit_diagram.png`.

## Example

The provided example files create a circuit with:
- U1: AND gate (7408)
- U2: OR gate (7432)
- U3: NOT gate (7404)
- U4: NAND gate (7400)
- U5: XOR gate (7486)

With connections showing the signal flow between the chips.
