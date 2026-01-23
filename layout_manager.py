"""Module for circuit layout and positioning logic"""

class LayoutManager:
    """Handles chip positioning and layout calculations"""
    
    @staticmethod
    def intelligent_chip_placement(chip_instances):
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
        chip_spacing_y = 300   # Vertical spacing between chips in same layer
        start_x = 250
        start_y = 100
        
        # Calculate chip heights
        gate_height = 80
        gate_spacing = 20
        
        def calculate_chip_height(chip_type, datasheets):
            if chip_type in datasheets:
                num_gates = len(datasheets[chip_type])
                return max(160, 80 + num_gates * (gate_height + gate_spacing))
            return 200
        
        # Place chips layer by layer
        canvas_width = start_x
        canvas_height = start_y
        
        for layer in sorted(layers.keys()):
            chips_in_layer = layers[layer]
            layer_x = start_x + layer * layer_spacing_x
            current_y = start_y
            
            # Stack chips vertically within the same layer
            for chip_id, chip_data in chips_in_layer:
                chip_positions[chip_id] = {'x': layer_x, 'y': current_y}
                
                # Update canvas dimensions
                chip_height = calculate_chip_height(chip_data['chip_type'], {})
                current_y += chip_height + chip_spacing_y
                
                # Track maximum dimensions
                canvas_width = max(canvas_width, layer_x + 300)
                canvas_height = max(canvas_height, current_y)
        
        # Add padding
        canvas_width += 100
        canvas_height += 100
        
        return chip_positions, canvas_width, canvas_height
