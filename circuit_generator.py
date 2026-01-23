import csv
import os
import xml.etree.ElementTree as ET

class SVGCircuitGenerator:
    def __init__(self, chips_csv, connections_csv, datasheet_csv, output_file="circuit_diagram.svg", db_folder="DB"):
        self.chips_csv = chips_csv
        self.connections_csv = connections_csv
        self.datasheet_csv = datasheet_csv
        self.output_file = output_file
        self.db_folder = db_folder
        self.chips = {}
        self.connections = []
        self.datasheets = {}
        self.chip_positions = {}
        self.chip_spacing_x = 250
        self.chip_spacing_y = 200
        self.chips_per_row = 3
        self.gate_symbols = {}
        
    def load_datasheets(self):
        """Load chip datasheet information from CSV file"""
        with open(self.datasheet_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                chip_type = row['chip_type']
                gate_num = int(row['gate_num'])
                
                if chip_type not in self.datasheets:
                    self.datasheets[chip_type] = {}
                
                self.datasheets[chip_type][gate_num] = {
                    'input_pins': [int(p.strip()) for p in row['input_pins'].split(',')],
                    'output_pin': int(row['output_pin']),
                    'gate_type': row['gate_type'],
                    'vcc_pin': int(row['vcc_pin']),
                    'gnd_pin': int(row['gnd_pin']),
                    'total_pins': int(row['total_pins'])
                }
    
    def load_chips(self):
        """Load chip definitions from CSV file"""
        with open(self.chips_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                chip_id = row['chip_id']
                chip_type = row['chip_type']
                gate_num = int(row['gate_num'])
                
                # Get datasheet info for this specific gate
                if chip_type in self.datasheets and gate_num in self.datasheets[chip_type]:
                    datasheet = self.datasheets[chip_type][gate_num]
                    self.chips[chip_id] = {
                        'chip_type': chip_type,
                        'gate_num': gate_num,
                        'gate_type': datasheet['gate_type'],
                        'input_pins': datasheet['input_pins'],
                        'output_pin': datasheet['output_pin'],
                        'vcc_pin': datasheet['vcc_pin'],
                        'gnd_pin': datasheet['gnd_pin'],
                        'total_pins': datasheet['total_pins']
                    }
                else:
                    raise ValueError(f"Datasheet not found for {chip_type} gate {gate_num}")
    
    def load_connections(self):
        """Load connections from CSV file"""
        with open(self.connections_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.connections.append({
                    'from_chip': row['from_chip'],
                    'from_pin': int(row['from_pin']),
                    'to_chip': row['to_chip'],
                    'to_pin': int(row['to_pin'])
                })
    
    def load_gate_svg(self, gate_type):
        """Load SVG content from DB folder for a specific gate type"""
        svg_file = os.path.join(self.db_folder, f"{gate_type}.svg")
        if not os.path.exists(svg_file):
            print(f"Warning: {svg_file} not found")
            return None
        
        try:
            with open(svg_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ET.fromstring(content)
            
            # Extract the path element content
            ns = {'svg': 'http://www.w3.org/2000/svg'}
            # Try with namespace first, then without
            path_elem = tree.find('.//{http://www.w3.org/2000/svg}path')
            if path_elem is None:
                path_elem = tree.find('.//path')
            
            if path_elem is not None:
                return {
                    'path': path_elem.get('d'),
                    'fill': path_elem.get('fill', '#000000')
                }
            else:
                print(f"Warning: No path found in {svg_file}")
        except Exception as e:
            print(f"Error loading {svg_file}: {e}")
        
        return None
    
    def create_svg_defs(self):
        """Create reusable SVG symbol definitions from DB folder SVGs"""
        defs = ['  <defs>']
        
        # Get unique gate types from loaded chips
        gate_types = set(chip['gate_type'] for chip in self.chips.values())
        
        for gate_type in gate_types:
            svg_data = self.load_gate_svg(gate_type)
            if svg_data:
                self.gate_symbols[gate_type] = svg_data
                # Create symbol with viewBox matching original SVG (0 0 512 512)
                # Add stroke to make lines thicker and more visible
                defs.append(f'    <symbol id="{gate_type}" viewBox="0 0 512 512">')
                defs.append(f'      <path fill="{svg_data["fill"]}" stroke="{svg_data["fill"]}" stroke-width="8" stroke-linejoin="round" d="{svg_data["path"]}"/>')
                defs.append('    </symbol>')
        
        defs.append('  </defs>')
        return '\n'.join(defs)
    
    def get_pin_positions(self, gate_type, num_inputs):
        """Get standardized pin positions for gate inputs and output based on SVG viewBox 0 0 512 512"""
        # Input pins are on the left side around y=150-350 depending on number of inputs
        # Output pin is on the right side around y=256
        
        input_positions = []
        if num_inputs == 1:
            input_positions = [{'x': 16, 'y': 256}]  # Single input centered
        elif num_inputs == 2:
            input_positions = [
                {'x': 16, 'y': 160},  # Top input
                {'x': 16, 'y': 352}   # Bottom input
            ]
        elif num_inputs == 3:
            input_positions = [
                {'x': 16, 'y': 160},   # Top input
                {'x': 16, 'y': 256},   # Middle input
                {'x': 16, 'y': 352}    # Bottom input
            ]
        elif num_inputs == 4:
            input_positions = [
                {'x': 16, 'y': 160},   # Top input
                {'x': 16, 'y': 224},   # Upper middle
                {'x': 16, 'y': 288},   # Lower middle
                {'x': 16, 'y': 352}    # Bottom input
            ]
        
        # Output pin position (right side, centered)
        output_position = {'x': 496, 'y': 256}
        
        return input_positions, output_position
    
    def calculate_positions(self):
        """Calculate positions for all chips in a grid layout"""
        chip_ids = list(self.chips.keys())
        for idx, chip_id in enumerate(chip_ids):
            row = idx // self.chips_per_row
            col = idx % self.chips_per_row
            x = 50 + col * self.chip_spacing_x
            y = 50 + row * self.chip_spacing_y
            self.chip_positions[chip_id] = {'x': x, 'y': y}
    
    def create_chip_svg(self, chip_id, chip_data, x, y):
        """Create SVG for a chip showing all gates of that chip type"""
        svg_parts = []
        chip_type = chip_data['chip_type']
        
        # Get all gates for this chip type
        all_gates = self.datasheets.get(chip_type, {})
        num_gates = len(all_gates)
        
        # Calculate chip box dimensions based on number of gates
        gate_width = 80
        gate_height = 80
        gate_spacing = 20
        box_width = 220
        box_height = max(160, 80 + num_gates * (gate_height + gate_spacing))
        
        # Chip container box
        svg_parts.append(f'    <rect x="{x}" y="{y}" width="{box_width}" height="{box_height}" '
                        f'fill="none" stroke="black" stroke-width="2" rx="5"/>')
        
        # Chip name at top
        svg_parts.append(f'    <text x="{x + box_width//2}" y="{y + 25}" '
                        f'font-family="Arial" font-size="16" font-weight="bold" '
                        f'text-anchor="middle" fill="black">{chip_type}</text>')
        
        # Draw all gates for this chip
        gate_y_start = y + 50
        for gate_num in sorted(all_gates.keys()):
            gate_data = all_gates[gate_num]
            gate_type = gate_data['gate_type']
            input_pins = gate_data['input_pins']
            output_pin = gate_data['output_pin']
            
            gate_y = gate_y_start + (gate_num - 1) * (gate_height + gate_spacing)
            gate_x = x + box_width // 2 - gate_width // 2
            
            # Create a group for this gate with all its elements
            svg_parts.append(f'    <g>')
            
            # Gate symbol
            svg_parts.append(f'      <use href="#{gate_type}" x="{gate_x}" y="{gate_y}" '
                            f'width="{gate_width}" height="{gate_height}"/>')
            
            # Get pin positions in the gate coordinate system
            input_positions, output_position = self.get_pin_positions(gate_type, len(input_pins))
            
            # Scale factor from SVG viewBox (512) to actual gate size
            scale_x = gate_width / 512
            scale_y = gate_height / 512
            
            # Add input pin numbers
            for i, pin in enumerate(input_pins):
                if i < len(input_positions):
                    pos = input_positions[i]
                    # Transform from gate coordinates to canvas coordinates
                    pin_x = gate_x + pos['x'] * scale_x
                    pin_y = gate_y + pos['y'] * scale_y
                    
                    # Pin number to the left of the gate
                    svg_parts.append(f'      <text x="{pin_x - 5}" y="{pin_y - 2}" '
                                   f'font-family="Arial" font-size="12" font-weight="bold" '
                                   f'text-anchor="end" fill="blue">{pin}</text>')
            
            # Add output pin number
            out_x = gate_x + output_position['x'] * scale_x
            out_y = gate_y + output_position['y'] * scale_y
            svg_parts.append(f'      <text x="{out_x + 5}" y="{out_y - 2}" '
                            f'font-family="Arial" font-size="12" font-weight="bold" '
                            f'text-anchor="start" fill="green">{output_pin}</text>')
            
            # Gate label (letter)
            gate_letters = ['A', 'B', 'C', 'D', 'E', 'F']
            if gate_num <= len(gate_letters):
                letter = gate_letters[gate_num - 1]
                svg_parts.append(f'      <text x="{gate_x + gate_width // 2}" y="{gate_y + gate_height + 15}" '
                                f'font-family="Arial" font-size="13" font-weight="bold" '
                                f'text-anchor="middle" fill="black">{letter}</text>')
            
            svg_parts.append(f'    </g>')
        
        # VCC and GND at bottom
        svg_parts.append(f'    <text x="{x + 10}" y="{y + box_height - 10}" '
                        f'font-family="Arial" font-size="12" fill="red">VCC:{chip_data["vcc_pin"]}</text>')
        svg_parts.append(f'    <text x="{x + box_width - 10}" y="{y + box_height - 10}" '
                        f'font-family="Arial" font-size="12" text-anchor="end" fill="gray">GND:{chip_data["gnd_pin"]}</text>')
        
        return '\n'.join(svg_parts)
    
    def generate_circuit(self):
        """Generate the complete SVG circuit diagram"""
        self.load_datasheets()
        self.load_chips()
        self.load_connections()
        
        if not self.chips:
            raise ValueError("No chips loaded")
        
        # Group chips by chip_type to avoid duplicates
        unique_chips = {}
        for chip_id, chip_data in self.chips.items():
            chip_type = chip_data['chip_type']
            if chip_type not in unique_chips:
                unique_chips[chip_type] = chip_data
        
        # Calculate actual chip heights to determine canvas size
        max_chip_height = 0
        for chip_type, chip_data in unique_chips.items():
            all_gates = self.datasheets.get(chip_type, {})
            num_gates = len(all_gates)
            gate_height = 80
            gate_spacing = 20
            box_height = max(160, 80 + num_gates * (gate_height + gate_spacing))
            max_chip_height = max(max_chip_height, box_height)
        
        # Calculate positions for unique chip types
        chip_list = list(unique_chips.items())
        for idx, (chip_type, chip_data) in enumerate(chip_list):
            row = idx // self.chips_per_row
            col = idx % self.chips_per_row
            x = 50 + col * self.chip_spacing_x
            y = 50 + row * self.chip_spacing_y
            self.chip_positions[chip_type] = {'x': x, 'y': y}
        
        # Calculate canvas size based on actual chip dimensions
        num_chips = len(unique_chips)
        num_rows = (num_chips + self.chips_per_row - 1) // self.chips_per_row
        canvas_width = self.chips_per_row * self.chip_spacing_x + 100
        canvas_height = 50 + num_rows * max(self.chip_spacing_y, max_chip_height + 50)
        
        # Start building SVG
        svg_parts = []
        svg_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
        svg_parts.append(f'<svg width="{canvas_width}" height="{canvas_height}" '
                        f'xmlns="http://www.w3.org/2000/svg" version="1.1">')
        
        # Add defs with reusable gate symbols
        svg_parts.append(self.create_svg_defs())
        
        # Add title
        svg_parts.append('  <text x="20" y="30" font-family="Arial" font-size="20" '
                        'font-weight="bold" fill="black">Circuit Diagram</text>')
        
        # Add all unique chip types
        for chip_type, chip_data in unique_chips.items():
            pos = self.chip_positions[chip_type]
            svg_parts.append(self.create_chip_svg(chip_type, chip_data, pos['x'], pos['y']))
        
        # Close SVG
        svg_parts.append('</svg>')
        
        # Write to file
        svg_content = '\n'.join(svg_parts)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"SVG circuit diagram saved to: {self.output_file}")
        return svg_content


if __name__ == "__main__":
    generator = SVGCircuitGenerator(
        chips_csv="chips.csv",
        connections_csv="connections.csv",
        datasheet_csv="chip_datasheets.csv",
        output_file="circuit_diagram.svg"
    )
    generator.generate_circuit()
