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
                return {
                    'path': path_elem.get('d'),
                    'fill': path_elem.get('fill', '#000000')
                }
            else:
                print(f"Warning: No path found in {svg_file}")
        except Exception as e:
            print(f"Error loading {svg_file}: {e}")
        
        return None
    
    def create_svg_defs(self, gate_types):
        """Create reusable SVG symbol definitions from DB folder SVGs"""
        defs = ['  <defs>']
        
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
    
    @staticmethod
    def get_pin_positions(gate_type, num_inputs):
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
