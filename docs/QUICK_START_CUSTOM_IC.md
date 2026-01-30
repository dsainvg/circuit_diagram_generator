# Quick Start Guide - Custom IC Chips

## Example: Creating a Custom Decoder Chip

### Step 1: Define in Datasheet
Add to `chip_datasheets.csv`:
```csv
MY_DECODER,1,"1,2,3,4",10,IC14,14,7,14,4-input to 1-output Decoder
```

**Fields:**
- `chip_type`: MY_DECODER
- `gate_num`: 1 (can have multiple functional blocks)
- `input_pins`: "1,2,3,4" (comma-separated)
- `output_pin`: 10
- `gate_type`: **IC14** (use IC14 for 14-pin, IC16 for 16-pin)
- `vcc_pin`: 14
- `gnd_pin`: 7
- `total_pins`: 14
- `description`: Text description

### Step 2: Add to Chips List
Add to `chips.csv`:
```csv
U5,MY_DECODER,1,2,true
```

**Fields:**
- `chip_id`: U5 (unique identifier)
- `chip_type`: MY_DECODER (matches datasheet)
- `gate_num`: 1 (which functional block)
- `layer`: 2 (for layout positioning)
- `is_custom_ic`: **true** (critical - marks as custom IC)

### Step 3: Create Connections
Add to `connections.csv`:
```csv
input,A,U5,1
input,B,U5,2
input,C,U5,3
input,D,U5,4
U5,10,output,DECODED_OUT
```

### Step 4: Generate Circuit
```bash
python circuit_generator.py
```

## Pin Position Reference

### IC14 (14-pin DIP)
```
       ┌─────┐
    1 ─┤  ●  ├─ 14 (VCC typical)
    2 ─┤     ├─ 13
    3 ─┤     ├─ 12
    4 ─┤     ├─ 11
    5 ─┤     ├─ 10
    6 ─┤     ├─ 9
    7 ─┤     ├─ 8
      (GND)  └─────┘
```
Y-positions: 30, 55, 80, 105, 130, 155, 180

### IC16 (16-pin DIP)
```
       ┌─────┐
    1 ─┤  ●  ├─ 16 (VCC typical)
    2 ─┤     ├─ 15
    3 ─┤     ├─ 14
    4 ─┤     ├─ 13
    5 ─┤     ├─ 12
    6 ─┤     ├─ 11
    7 ─┤     ├─ 10
    8 ─┤     ├─ 9
      (GND)  └─────┘
```
Y-positions: 30, 55, 80, 105, 130, 155, 180, 205

## Common Use Cases

### Multi-Input Logic
```csv
# 8-input OR gate as custom IC
CUSTOM_OR8,1,"1,2,3,4,5,6,7,8",13,IC14,14,7,14,8-input OR gate
```

### Multiplexer
```csv
# 4:1 MUX with select lines
MUX_4TO1,1,"1,2,3,4,11,12",8,IC14,14,7,14,4-to-1 Multiplexer
```

### Decoder
```csv
# 3:8 Decoder (3 inputs, 8 outputs - use multiple gates)
DECODER_3TO8,1,"1,2,3",15,IC16,16,8,16,3-to-8 Decoder
```

### Custom Processor Module
```csv
# Mini ALU with multiple I/O
ALU_MODULE,1,"1,2,3,4,5,6",13,IC16,16,8,16,2-bit ALU Module
```

## Color Code Reference

- **Blue (#2196F3)**: Input pins
- **Green (#4CAF50)**: Output pins
- **Red/Orange (#FF5722)**: VCC power pin
- **Gray (#607D8B)**: GND ground pin

## Tips

1. **Maximum Pins**: IC14 has 14 pins, IC16 has 16 pins (2 reserved for VCC/GND)
2. **Pin Numbering**: Follow standard DIP numbering (1-7/8 on left, counterclockwise)
3. **Layer Assignment**: Use different layers for horizontal spacing in layout
4. **Multiple Blocks**: Use gate_num for multiple functional blocks in same chip type
5. **Connections**: Can connect any pin - system handles routing automatically

## Example: Complete Circuit

```csv
# chip_datasheets.csv
74LS00,1,"1,2",3,NAND2,14,7,14,Quad 2-input NAND
CUSTOM_MUX,1,"1,2,3,4",13,IC14,14,7,14,4-input Multiplexer

# chips.csv
U1,74LS00,1,0,false
U2,CUSTOM_MUX,1,1,true

# connections.csv
input,A,U1,1
input,B,U1,2
U1,3,U2,1
input,C,U2,2
input,D,U2,3
input,E,U2,4
U2,13,output,RESULT
```

This creates a circuit with a NAND gate feeding into a custom 4-input multiplexer!
