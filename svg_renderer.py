"""Module for rendering SVG components"""

class SVGRenderer:
    """Handles rendering of SVG elements for chips, inputs, and outputs"""
    
    def __init__(self, symbol_manager, datasheets):
        self.symbol_manager = symbol_manager
        self.datasheets = datasheets
        self.pin_positions = {}
    
    def create_chip_svg(self, chip_id, chip_data, x, y):
        """Create SVG for a chip showing all gates of that chip type"""
        svg_parts = []
        chip_type = chip_data['chip_type']
        
        # Initialize pin positions storage for this chip
        self.pin_positions[chip_id] = {}
        
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
            input_positions, output_position = self.symbol_manager.get_pin_positions(gate_type, len(input_pins))
            
            # Scale factor from SVG viewBox (512) to actual gate size
            scale_x = gate_width / 512
            scale_y = gate_height / 512
            
            # Add input pin numbers and store positions
            for i, pin in enumerate(input_pins):
                if i < len(input_positions):
                    pos = input_positions[i]
                    # Transform from gate coordinates to canvas coordinates
                    pin_x = gate_x + pos['x'] * scale_x
                    pin_y = gate_y + pos['y'] * scale_y
                    
                    # Store pin position for later use in connections
                    self.pin_positions[chip_id][pin] = {'x': pin_x, 'y': pin_y}
                    
                    # Pin number to the left of the gate
                    svg_parts.append(f'      <text x="{pin_x - 5}" y="{pin_y - 2}" '
                                   f'font-family="Arial" font-size="12" font-weight="bold" '
                                   f'text-anchor="end" fill="blue">{pin}</text>')
            
            # Add output pin number and store position
            out_x = gate_x + output_position['x'] * scale_x
            out_y = gate_y + output_position['y'] * scale_y
            
            # Store output pin position
            self.pin_positions[chip_id][output_pin] = {'x': out_x, 'y': out_y}
            
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
        svg_parts.append(f'    <text x="{x + box_width - 70}" y="{y + box_height - 10}" '
                        f'font-family="Arial" font-size="12" fill="blue">GND:{chip_data["gnd_pin"]}</text>')
        
        return '\n'.join(svg_parts)
    
    def create_outputs_box(self, x, y, outputs):
        """Create lightbulbs for all circuit outputs"""
        if not outputs:
            return ""
        
        svg_parts = []
        
        # Calculate box dimensions based on number of outputs
        output_size = 50
        output_spacing = 20
        box_width = 150
        box_height = 60 + len(outputs) * (output_size + output_spacing)
        
        # Output container box
        svg_parts.append(f'    <rect x="{x}" y="{y}" width="{box_width}" height="{box_height}" '
                        f'fill="none" stroke="black" stroke-width="2" rx="5"/>')
        
        # Title
        svg_parts.append(f'    <text x="{x + box_width//2}" y="{y + 25}" '
                        f'font-family="Arial" font-size="16" font-weight="bold" '
                        f'text-anchor="middle" fill="black">OUTPUTS</text>')
        
        # Draw each output as a lightbulb with label and connection
        output_y_start = y + 50
        for idx, output_data in enumerate(outputs):
            output_y = output_y_start + idx * (output_size + output_spacing)
            output_x = x + (box_width - output_size) // 2
            led_center_x = output_x + output_size // 2
            # LED bottom in viewBox is at y=366 out of 512, so actual bottom is at this offset
            led_bottom_y = output_y + (366 / 512) * output_size
            
            # LED/Lightbulb icon from DB folder
            svg_parts.append(f'    <use href="#LED" x="{output_x}" y="{output_y}" '
                            f'width="{output_size}" height="{output_size}"/>')
            
            # Output label below lightbulb
            svg_parts.append(f'    <text x="{led_center_x}" y="{output_y + output_size + 15}" '
                            f'font-family="Arial" font-size="12" font-weight="bold" '
                            f'text-anchor="middle" fill="green">{output_data["name"]}</text>')
            
            # Wire from bottom of LED to bottom of box (simple vertical line)
            box_bottom_y = y + box_height
            svg_parts.append(f'    <line x1="{led_center_x}" y1="{led_bottom_y}" '
                            f'x2="{led_center_x}" y2="{box_bottom_y}" '
                            f'stroke="yellow" stroke-width="2"/>')
            
        return '\n'.join(svg_parts)
    
    def create_inputs_box(self, x, y, inputs):
        """Create a box showing all circuit inputs"""
        if not inputs:
            return ""
        
        svg_parts = []
        
        # Calculate box dimensions based on number of inputs
        input_size = 40
        input_spacing = 15
        box_width = 120
        box_height = 60 + len(inputs) * (input_size + input_spacing)
        
        # Input container box
        svg_parts.append(f'    <rect x="{x}" y="{y}" width="{box_width}" height="{box_height}" '
                        f'fill="none" stroke="black" stroke-width="2" rx="5"/>')
        
        # Title
        svg_parts.append(f'    <text x="{x + box_width//2}" y="{y + 25}" '
                        f'font-family="Arial" font-size="16" font-weight="bold" '
                        f'text-anchor="middle" fill="black">INPUTS</text>')
        
        # Draw each input as a square with label
        input_y_start = y + 50
        for idx, input_data in enumerate(inputs):
            input_y = input_y_start + idx * (input_size + input_spacing)
            input_x = x + (box_width - input_size) // 2
            
            # Square for input
            svg_parts.append(f'    <rect x="{input_x}" y="{input_y}" width="{input_size}" height="{input_size}" '
                            f'fill="black"/>')
            
            # Input label inside square
            svg_parts.append(f'    <text x="{input_x + input_size//2}" y="{input_y + input_size//2 + 5}" '
                            f'font-family="Arial" font-size="16" font-weight="bold" '
                            f'text-anchor="middle" fill="blue">{input_data["name"]}</text>')
            
            # Connection line extending right
            svg_parts.append(f'    <line x1="{input_x + input_size}" y1="{input_y + input_size//2}" '
                            f'x2="{x + box_width + 20}" y2="{input_y + input_size//2}" '
                            f'stroke="yellow" stroke-width="2"/>')
        
        return '\n'.join(svg_parts)
