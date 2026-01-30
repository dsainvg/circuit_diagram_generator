"""
Modular SVG Circuit Diagram Generator
Main orchestrator that uses separate modules for data loading, rendering, and layout
"""

from data_loader import DataLoader
from svg_symbol_manager import SVGSymbolManager
from layout_manager import LayoutManager
from svg_renderer import SVGRenderer
from channel_router import ChannelRouter

class SVGCircuitGenerator:
    """Main class that orchestrates the circuit diagram generation"""
    
    def __init__(self, chips_csv, connections_csv, datasheet_csv, output_file="circuit_diagram.svg", db_folder="DB"):
        self.chips_csv = chips_csv
        self.connections_csv = connections_csv
        self.datasheet_csv = datasheet_csv
        self.output_file = output_file
        self.db_folder = db_folder
        
        # Initialize managers
        self.data_loader = DataLoader()
        self.symbol_manager = SVGSymbolManager(db_folder)
        self.layout_manager = LayoutManager()
        
        # Data storage
        self.chips = {}
        self.connections = []
        self.inputs = []
        self.outputs = []
        self.displays = []
        self.datasheets = {}
        self.chip_positions = {}
        
    def load_data(self):
        """Load all circuit data from CSV files"""
        self.datasheets = self.data_loader.load_datasheets(self.datasheet_csv)
        self.chips = self.data_loader.load_chips(self.chips_csv, self.datasheets)
        self.connections, self.inputs, self.outputs, self.displays = self.data_loader.load_connections(self.connections_csv)
        
        if not self.chips:
            raise ValueError("No chips loaded")
    
    def calculate_chip_height(self, chip_type):
        """Calculate height of a chip based on number of gates or IC type"""
        if chip_type in self.datasheets:
            # Check if it's a custom IC
            first_gate = list(self.datasheets[chip_type].values())[0]
            if first_gate.get('gate_type') in ['IC14', 'IC16']:
                # Custom IC chip - use IC dimensions with box padding
                total_pins = first_gate.get('total_pins', 14)
                ic_height = 220 if total_pins == 14 else 240
                display_height = int(ic_height * 1.5)  # Scale factor
                return display_height + 130  # Add box padding (50 top + 80 bottom)
            else:
                # Regular gate-based chip
                gate_height = 80
                gate_spacing = 20
                num_gates = len(self.datasheets[chip_type])
                return max(160, 80 + num_gates * (gate_height + gate_spacing))
        return 200
    
    def generate_circuit(self):
        """Generate the complete SVG circuit diagram"""
        # Load all data
        self.load_data()
        
        # Calculate input/output box dimensions
        input_box_height = 0
        if self.inputs:
            input_size = 40
            input_spacing = 15
            input_box_height = 60 + len(self.inputs) * (input_size + input_spacing)
        
        output_box_height = 0
        if self.outputs:
            output_size = 50
            output_spacing = 20
            output_box_height = 60 + len(self.outputs) * (output_size + output_spacing)
        
        # Calculate chip positions using layout manager
        self.chip_positions, canvas_width, canvas_height = self.layout_manager.intelligent_chip_placement(self.chips)
        
        # Add space for outputs box on the right
        if self.outputs:
            canvas_width += 400
        
        # Add space for display modules on the right
        if self.displays:
            canvas_width += 250
        
        # Adjust canvas height for inputs/outputs if needed
        # Add extra padding for fallback routing (Strategy 3 spills over bottom)
        canvas_height = max(canvas_height, input_box_height + 250, output_box_height + 100) + 500
        
        # Get unique gate types for symbol definitions
        gate_types = set(chip['gate_type'] for chip in self.chips.values())
        gate_types.add('LED')  # Add LED for outputs
        
        # Create SVG renderer
        # Initialize channel router
        self.router = ChannelRouter(
            canvas_width, 
            canvas_height,
            channel_width=20,
            min_spacing=10
        )
        
        renderer = SVGRenderer(self.symbol_manager, self.datasheets, self.router)
        
        # Start building SVG
        svg_parts = []
        svg_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
        svg_parts.append(f'<svg width="{canvas_width}" height="{canvas_height}" '
                        f'xmlns="http://www.w3.org/2000/svg" '
                        f'xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">')
        
        # Add defs with reusable gate symbols
        svg_parts.append(self.symbol_manager.create_svg_defs(gate_types))
        
        # Add title
        svg_parts.append('  <text x="20" y="30" font-family="Arial" font-size="20" '
                        'font-weight="bold" fill="black">Circuit Diagram</text>')
        
        # Add inputs box if inputs exist
        inputs_svg = ""
        if self.inputs:
            inputs_svg = renderer.create_inputs_box(50, 150, self.inputs) # This populates pin_positions['input']
            svg_parts.append(inputs_svg)
        
        # Add all chip instances
        for chip_id, chip_data in self.chips.items():
            pos = self.chip_positions[chip_id]
            svg_parts.append(renderer.create_chip_svg(chip_id, chip_data, pos['x'], pos['y']))
        
        # Store pin positions from renderer
        self.pin_positions = renderer.pin_positions

        # Pre-calculate outputs SVG to populate pin_positions['output']
        outputs_svg = ""
        if self.outputs:
            outputs_x = canvas_width - 350
            outputs_svg = renderer.create_outputs_box(outputs_x, 50, self.outputs)
        
        # Pre-calculate display modules SVG to populate pin_positions['display']
        displays_svg = ""
        if self.displays:
            # Position displays on far right, below outputs if they exist
            if self.outputs:
                displays_x = canvas_width - 230
                displays_y = 50 + output_box_height + 30
            else:
                displays_x = canvas_width - 230
                displays_y = 50
            displays_svg = renderer.create_display_module(displays_x, displays_y, self.displays)
        
        # Aggregate all connections for routing
        # DataLoader now returns ALL connections in self.connections list
        all_connections = self.connections
        
        # ROUTE CONNECTIONS with channel routing
        connections_svg, failed = renderer.render_connections_channel(
            all_connections,
            self.chip_positions,
            (canvas_width, canvas_height),
            chip_instances=self.chips
        )
        svg_parts.append(connections_svg)
        
        # Add outputs box if outputs exist (on the right side)
        if self.outputs and outputs_svg:
            svg_parts.append(outputs_svg)
        
        # Add display modules if displays exist (on the right side, below outputs)
        if self.displays and displays_svg:
            svg_parts.append(displays_svg)
        
        # Close SVG
        svg_parts.append('</svg>')
        
        # Write to file
        svg_content = '\n'.join(svg_parts)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"SVG circuit diagram saved to: {self.output_file}")
        return svg_content


if __name__ == "__main__":
    # Test with custom IC chips
    print("=== Testing Custom IC Chip Integration ===")
    generator = SVGCircuitGenerator(
        chips_csv="I-O/chips_custom_test.csv",
        connections_csv="I-O/connections_custom_test.csv",
        datasheet_csv="I-O/chip_datasheets.csv",
        output_file="I-O/outputs/circuit_diagram_custom.svg"
    )
    generator.generate_circuit()
    
    print("\n=== Testing Original Circuit ===")
    generator2 = SVGCircuitGenerator(
        chips_csv="I-O/chips.csv",
        connections_csv="I-O/connections.csv",
        datasheet_csv="I-O/chip_datasheets.csv",
        output_file="I-O/outputs/circuit_diagram.svg"
    )
    generator2.generate_circuit()
