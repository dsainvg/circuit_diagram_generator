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
