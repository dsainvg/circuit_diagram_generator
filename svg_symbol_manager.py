"""Module for SVG symbol and gate handling"""
import os
import xml.etree.ElementTree as ET

class SVGSymbolManager:
    """Manages loading and handling of SVG gate symbols"""
    
    def __init__(self, db_folder="DB"):
        self.db_folder = db_folder
        self.gate_symbols = {}
    
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
                fill = path_elem.get('fill', '#000000')
                stroke = path_elem.get('stroke', fill)
                stroke_width = path_elem.get('stroke-width', '8')
                
                return {
                    'path': path_elem.get('d'),
                    'fill': fill,
                    'stroke': stroke,
                    'stroke_width': stroke_width
                }
            else:
                print(f"Warning: No path found in {svg_file}")
        except Exception as e:
            print(f"Error loading {svg_file}: {e}")
        
        return None
    
    def load_full_ic_svg(self, ic_type):
        """Load full IC SVG content for custom chips (IC14, IC16)"""
        svg_file = os.path.join(self.db_folder, f"{ic_type}.svg")
        if not os.path.exists(svg_file):
            print(f"Warning: {svg_file} not found")
            return None
        
        try:
            with open(svg_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse to extract viewBox and inner content
            tree = ET.fromstring(content)
            viewBox = tree.get('viewBox', '0 0 512 512')
            
            # Get all child elements as string
            inner_content = []
            for child in tree:
                inner_content.append(ET.tostring(child, encoding='unicode'))
            
            return {
                'viewBox': viewBox,
                'content': '\n'.join(inner_content)
            }
        except Exception as e:
            print(f"Error loading {svg_file}: {e}")
        
        return None
    
    @staticmethod
    def get_ic_pin_positions(ic_type, total_pins):
        """Get pin positions for IC8, IC14 and IC16 chips based on viewBox"""
        pin_positions = {}
        
        if ic_type == 'IC8' or total_pins == 8:
            # IC8: viewBox="0 0 140 140", pins at y: 30,55,80,105 (spacing 25)
            # Standard DIP-8: pins 1-4 on left, pins 8-5 on right (counterclockwise)
            left_pins = [1, 2, 3, 4]
            right_pins = [8, 7, 6, 5]
            
            for i, pin in enumerate(left_pins):
                pin_positions[pin] = {'x': 0, 'y': 30 + i * 25}
            
            for i, pin in enumerate(right_pins):
                pin_positions[pin] = {'x': 140, 'y': 30 + i * 25}
                
        elif ic_type == 'IC14' or total_pins == 14:
            # IC14: viewBox="0 0 140 220", pins at y: 30,55,80,105,130,155,180 (spacing 25)
            # Standard DIP-14: pins 1-7 on left, pins 14-8 on right (counterclockwise)
            # Pin 7 (GND) at bottom-left, Pin 14 (VCC) at bottom-right
            left_pins = [1, 2, 3, 4, 5, 6, 7]
            right_pins = [14, 13, 12, 11, 10, 9, 8]
            
            # Place GND and VCC at the same Y position
            for i, pin in enumerate(left_pins):
                pin_positions[pin] = {'x': 0, 'y': 30 + i * 25}
            
            for i, pin in enumerate(right_pins):
                # Align pin 14 (VCC) with pin 7 (GND) vertically
                pin_positions[pin] = {'x': 140, 'y': 30 + (6 - i) * 25}
                
        elif ic_type == 'IC16' or total_pins == 16:
            # IC16: viewBox="0 0 140 240", pins at y: 30,55,80,105,130,155,180,205 (spacing 25)
            # Standard DIP-16: pins 1-8 on left, pins 16-9 on right (counterclockwise)
            # Pin 8 (GND) at bottom-left, Pin 16 (VCC) at bottom-right
            left_pins = [1, 2, 3, 4, 5, 6, 7, 8]
            right_pins = [16, 15, 14, 13, 12, 11, 10, 9]
            
            # Place GND and VCC at the same Y position
            for i, pin in enumerate(left_pins):
                pin_positions[pin] = {'x': 0, 'y': 30 + i * 25}
            
            for i, pin in enumerate(right_pins):
                # Align pin 16 (VCC) with pin 8 (GND) vertically
                pin_positions[pin] = {'x': 140, 'y': 30 + (7 - i) * 25}
        
        return pin_positions
    
    def create_svg_defs(self, gate_types):
        """Create reusable SVG symbol definitions from DB folder SVGs"""
        defs = ['  <defs>']
        
        for gate_type in gate_types:
            # For IC packages (IC8, IC14, IC16), load full SVG content
            if gate_type in ['IC8', 'IC14', 'IC16']:
                svg_content = self.load_full_ic_svg(gate_type)
                if svg_content:
                    # Store for later use
                    self.gate_symbols[gate_type] = {'full_svg': svg_content}
                    # Create symbol with the full IC package content
                    defs.append(f'    <symbol id="{gate_type}" viewBox="{svg_content["viewBox"]}">')
                    defs.append(svg_content['content'])
                    defs.append('    </symbol>')
            else:
                # For regular gates, load path only
                svg_data = self.load_gate_svg(gate_type)
                if svg_data:
                    self.gate_symbols[gate_type] = svg_data
                    # Create symbol with viewBox matching original SVG (0 0 512 512)
                    # Add stroke to make lines thicker and more visible
                    fill = svg_data.get('fill', '#000000')
                    stroke = svg_data.get('stroke', fill)
                    stroke_width = svg_data.get('stroke_width', '8')
                    
                    defs.append(f'    <symbol id="{gate_type}" viewBox="0 0 512 512">')
                    defs.append(f'      <path fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" stroke-linejoin="round" d="{svg_data["path"]}"/>')
                    defs.append('    </symbol>')
        
        defs.append('  </defs>')
        return '\n'.join(defs)
    
    @staticmethod
    def get_pin_positions(gate_type, num_inputs):
        """Get standardized pin positions for gate inputs and output based on SVG viewBox 0 0 512 512"""
        # Input pins are on the left side around y=150-350 depending on number of inputs
        # Output pin is on the right side around y=256
        
        input_positions = []
        
        # Special handling for MUX gates which have different pin layouts
        if gate_type == 'MUX2':
            # MUX2: 2 data inputs on left, select at bottom (in actual SVG)
            input_positions = [
                {'x': 64, 'y': 200},   # Input A (top)
                {'x': 64, 'y': 328}    # Input B (bottom)
            ]
            output_position = {'x': 384, 'y': 264}
            return input_positions, output_position
            
        elif gate_type == 'MUX4':
            # MUX4: 4 data inputs on left, selects at bottom (in actual SVG)
            input_positions = [
                {'x': 96, 'y': 136},   # Input I0
                {'x': 96, 'y': 226},   # Input I1
                {'x': 96, 'y': 316},   # Input I2
                {'x': 96, 'y': 406}    # Input I3
            ]
            output_position = {'x': 416, 'y': 264}
            return input_positions, output_position
        
        # Standard gate pin positions
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
    @staticmethod
    def get_mux_info(chip_type):
        """Get MUX-specific information for select pins that are shared across gates
        Returns: dict with 'select_pins', 'enable_pins', 'pin_labels' for the chip"""
        mux_info = {
            '74LS153': {
                'select_pins': [2, 14],  # S1, S0
                'select_labels': {2: 'S1', 14: 'S0'},
                'enable_pins': {1: 'E_a', 15: 'E_b'},  # Gate-specific enables
                'gate_enable_map': {1: 1, 2: 15},  # gate_num -> enable_pin
                'description': 'Dual 4:1 MUX'
            },
            '74LS157': {
                'select_pins': [1],  # A/B (S)
                'select_labels': {1: 'A/B'},
                'enable_pins': {15: 'G'},  # Common enable for all gates
                'gate_enable_map': {},  # No per-gate enable
                'description': 'Quad 2:1 MUX'
            }
        }
        return mux_info.get(chip_type, None)