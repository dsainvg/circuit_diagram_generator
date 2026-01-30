"""Module for circuit layout and positioning logic"""

class LayoutManager:
    """Handles chip positioning and layout calculations"""
    
    @staticmethod
    def intelligent_chip_placement(chip_instances, datasheets=None):
        """
        Intelligently place chips based on their layer information.
        Same layer chips stack vertically, different layers arrange horizontally.
        """
        # Group chips by layer
        layers = {}
        for chip_id, chip_data in chip_instances.items():
            layer = chip_data['layer']
            if layer not in layers:
                layers[layer] = []
            layers[layer].append((chip_id, chip_data))
        
        chip_positions = {}
        
        # Layout parameters
        layer_spacing_x = 400  # Horizontal spacing between layers
        base_chip_spacing = 20   # Minimum spacing between chips
        start_x = 250
        start_y = 100
        
        # Calculate chip heights
        gate_height = 80
        gate_spacing = 20
        
        def calculate_chip_height(chip_data):
            # Check if it's a custom IC
            if chip_data.get('is_custom_ic', False):
                total_pins = chip_data.get('total_pins', 14)
                if total_pins == 8:
                    ic_height = 140
                elif total_pins == 14:
                    ic_height = 220
                else:
                    ic_height = 240
                display_height = int(ic_height * 1.5)  # Scale factor
                return display_height + 130  # Add box padding (50 top + 80 bottom)
            else:
                # Regular gate-based chip - calculate based on actual number of gates
                chip_type = chip_data.get('chip_type')
                num_gates = 1
                if datasheets and chip_type in datasheets:
                    num_gates = len(datasheets[chip_type])
                chip_height = max(160, 80 + num_gates * (gate_height + gate_spacing))
                return chip_height
        
        # Place chips layer by layer
        canvas_width = start_x
        canvas_height = start_y
        
        for layer in sorted(layers.keys()):
            chips_in_layer = layers[layer]
            layer_x = start_x + layer * layer_spacing_x
            current_y = start_y
            prev_chip_height = 0
            
            # Stack chips vertically within the same layer
            for idx, (chip_id, chip_data) in enumerate(chips_in_layer):
                # Calculate current chip height
                chip_height = calculate_chip_height(chip_data)
                
                # Add spacing BEFORE positioning (except for first chip)
                if idx > 0:
                    # Use 15% of previous chip's height as spacing
                    spacing = int(prev_chip_height * 0.15)
                    current_y += spacing
                
                # Now position the chip
                chip_positions[chip_id] = {'x': layer_x, 'y': current_y}
                
                # Move current_y down by chip height for next iteration
                current_y += chip_height
                
                # Store for next iteration
                prev_chip_height = chip_height
                
                # Track maximum dimensions
                canvas_width = max(canvas_width, layer_x + 300)
                canvas_height = max(canvas_height, current_y)
        
        # Add padding
        canvas_width += 100
        canvas_height += 100
        
        return chip_positions, canvas_width, canvas_height
