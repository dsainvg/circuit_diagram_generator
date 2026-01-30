"""Module for rendering SVG components"""

class SVGRenderer:
    """Handles rendering of SVG elements for chips, inputs, and outputs"""
    
    def __init__(self, symbol_manager, datasheets, router=None):
        self.symbol_manager = symbol_manager
        self.datasheets = datasheets
        self.pin_positions = {}
        self.router = router

    def render_connections_channel(self, connections, chip_positions, canvas_dims, chip_instances=None):
        """
        Render connections with channel-based routing.
        Allows perpendicular crossings, minimal turns.
        """
        if not self.router:
            from channel_router import ChannelRouter
            self.router = ChannelRouter(
                canvas_dims[0], 
                canvas_dims[1],
                channel_width=20,
                min_spacing=10
            )
        
        # Mark all chip areas
        gate_height = 80
        gate_spacing = 20
        
        for chip_id, pos in chip_positions.items():
            width = 220
            height = 200 # Defaults
            
            if chip_instances and chip_id in chip_instances:
                 chip_data = chip_instances[chip_id]
                 chip_type = chip_data['chip_type'] if isinstance(chip_data, dict) else chip_data.chip_type
                 # Depending on how chip_instances is structured (dict of dicts usually)
                 
                 # Check structure from layout_manager or circuit_generator
                 # In layout_manager: chip_data is a dict with 'layer', 'chip_type', etc.
                 if isinstance(chip_data, dict):
                    chip_type = chip_data.get('chip_type')
                 
                 if chip_type and chip_type in self.datasheets:
                     num_gates = len(self.datasheets[chip_type])
                     height = max(160, 80 + num_gates * (gate_height + gate_spacing))
            
            self.router.add_chip_boundary(pos['x'], pos['y'], width=width, height=height)

        # Build Net Graph for Coloring
        # We group all connected pins into logical keys and assign one color per net
        adj = {}
        def add_edge_to_graph(n1, n2):
            if n1 not in adj: adj[n1] = []
            if n2 not in adj: adj[n2] = []
            adj[n1].append(n2)
            adj[n2].append(n1)
            
        for connection in connections:
            if isinstance(connection, dict):
                s = (connection.get('from_chip'), connection.get('from_pin'))
                d = (connection.get('to_chip'), connection.get('to_pin'))
            else:
                s = (connection[0], connection[1])
                d = (connection[2], connection[3])
            add_edge_to_graph(s, d)
            
        pin_to_color = {}
        visited_nodes = set()
        
        available_colors = [
            "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231", 
            "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe", 
            "#008080", "#e6beff", "#9a6324", "#fffac8", "#800000", 
            "#aaffc3", "#808000", "#ffd8b1", "#000075", "#808080"
        ]
        color_idx = 0
        
        # Find Connected Components (Nets)
        for node in adj:
            if node not in visited_nodes:
                current_color = available_colors[color_idx % len(available_colors)]
                color_idx += 1
                
                # BFS
                queue = [node]
                visited_nodes.add(node)
                while queue:
                    curr = queue.pop(0)
                    pin_to_color[curr] = current_color
                    for neighbor in adj[curr]:
                        if neighbor not in visited_nodes:
                            visited_nodes.add(neighbor)
                            queue.append(neighbor)
        
        svg_paths = []
        failed = []
        routed_count = 0
        
        # Route each connection
        for wire_id, connection in enumerate(connections):
            # Handle dictionary or tuple
            if isinstance(connection, dict):
                from_chip = connection.get('from_chip')
                from_pin = connection.get('from_pin')
                to_chip = connection.get('to_chip')
                to_pin = connection.get('to_pin')
            else:
                from_chip, from_pin, to_chip, to_pin = connection
                
            # Determine color from pre-calculated Net Color
            source_key = (from_chip, from_pin)
            wire_color = pin_to_color.get(source_key, "#000000") # Default black if issue
            
            # Net ID for routing overlap logic (Using color is a good proxy for "Same Net")
            # Or construct specific net key
            net_id = wire_color 

            # Get pin positions
            start_pos = None
            end_pos = None
            
            # Find start position
            if from_chip == 'input':
                if 'input' in self.pin_positions and from_pin in self.pin_positions['input']:
                    start_pos = self.pin_positions['input'][from_pin]
            elif from_chip in self.pin_positions and from_pin in self.pin_positions[from_chip]:
                start_pos = self.pin_positions[from_chip][from_pin]
                
            # Find end position
            if to_chip == 'output':
                if 'output' in self.pin_positions and to_pin in self.pin_positions['output']:
                    end_pos = self.pin_positions['output'][to_pin]
            elif to_chip in self.pin_positions and to_pin in self.pin_positions[to_chip]:
                end_pos = self.pin_positions[to_chip][to_pin]
            
            if not start_pos:
                failed.append((wire_id, connection, f"Source pin not found: {from_chip}.{from_pin}"))
                continue
            
            if not end_pos:
                failed.append((wire_id, connection, f"Target pin not found: {to_chip}.{to_pin}"))
                continue
            
            x1 = start_pos['x']
            y1 = start_pos['y']
            x2 = end_pos['x']
            y2 = end_pos['y']
            
            # Prefer horizontal routing for cleaner diagrams
            waypoints = self.router.route_net(
                x1, y1, x2, y2,
                wire_id=wire_id,
                net_id=net_id,
                prefer_horizontal=True
            )
            
            if waypoints:
                svg_path = self._create_svg_path(waypoints, wire_id, color=wire_color)
                svg_paths.append(svg_path)
                routed_count += 1
            else:
                failed.append((wire_id, connection, "Channel routing failed"))
        
        print(f"✓ Routed {routed_count}/{len(connections)} connections")
        if failed:
            print(f"✗ Failed: {len(failed)} connections")
            for f in failed:
                print(f"  - {f[2]}")
        
        return '\n'.join(svg_paths), failed
    
    def _create_svg_path(self, waypoints, wire_id, color=None):
        """Create SVG path from waypoints."""
        if not waypoints:
            return ""
        
        path_data = f"M {waypoints[0][0]} {waypoints[0][1]}"
        for x, y in waypoints[1:]:
            path_data += f" L {x} {y}"
        
        # Default colors if not provided (though now it should always be provided)
        if not color:
            colors = [
                "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
                "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
            ]
            color = colors[wire_id % len(colors)]
        
        return (f'<path id="wire-{wire_id}" d="{path_data}" '
                f'stroke="{color}" fill="none" stroke-width="2.5" '
                f'stroke-linecap="round" stroke-linejoin="round"/>')
        
    def create_custom_ic_svg(self, chip_id, chip_data, x, y):
        """Create SVG for a custom IC chip (IC14/IC16) with multiple I/O"""
        svg_parts = []
        chip_type = chip_data['chip_type']
        
        # Initialize pin positions storage for this chip
        self.pin_positions[chip_id] = {}
        
        # Determine IC type and dimensions
        total_pins = chip_data.get('total_pins', 14)
        if total_pins == 8:
            ic_display_type = 'IC8'
        elif total_pins == 14:
            ic_display_type = 'IC14'
        else:
            ic_display_type = 'IC16'
        
        # Load the IC SVG
        ic_svg_data = self.symbol_manager.load_full_ic_svg(ic_display_type)
        
        if not ic_svg_data:
            return self.create_chip_svg(chip_id, chip_data, x, y)  # Fallback
        
        # Extract SVG viewBox dimensions from the loaded data
        viewBox = ic_svg_data['viewBox']
        ic_svg_content = ic_svg_data['content']
        
        # Parse viewBox to get dimensions
        viewBox_parts = viewBox.split()
        ic_width = float(viewBox_parts[2]) if len(viewBox_parts) >= 3 else 140
        if total_pins == 8:
            ic_height = float(viewBox_parts[3]) if len(viewBox_parts) >= 4 else 140
        elif total_pins == 14:
            ic_height = float(viewBox_parts[3]) if len(viewBox_parts) >= 4 else 220
        else:
            ic_height = float(viewBox_parts[3]) if len(viewBox_parts) >= 4 else 240
        
        # Scale factor for display
        scale = 1.5
        display_width = ic_width * scale
        display_height = ic_height * scale
        
        # Calculate box dimensions (add padding around IC)
        box_padding = 30
        box_width = display_width + box_padding * 2
        box_height = display_height + 80  # Extra space for title and VCC/GND labels
        
        # Chip container box
        svg_parts.append(f'    <rect x="{x}" y="{y}" width="{box_width}" height="{box_height}" '
                        f'fill="none" stroke="black" stroke-width="2" rx="5"/>')
        
        # Register boundary with router to prevent wires from passing through
        if self.router:
            self.router.add_chip_boundary(x, y, box_width, box_height)
        
        # Chip name at top
        svg_parts.append(f'    <text x="{x + box_width//2}" y="{y + 25}" '
                        f'font-family="Arial" font-size="16" font-weight="bold" '
                        f'text-anchor="middle" fill="black">{chip_type}</text>')
        
        # Adjust IC position to center it in the box with space for title
        ic_x = x + box_padding
        ic_y = y + 50
        
        # Embed IC SVG at adjusted position (content is already parsed as string)
        svg_parts.append(f'    <g transform="translate({ic_x}, {ic_y}) scale({scale})">')
        svg_parts.append('      ' + ic_svg_content)
        svg_parts.append('    </g>')
        
        # Get pin positions and register them
        pin_positions = self.symbol_manager.get_ic_pin_positions(ic_display_type, total_pins)
        
        # Get all pins from datasheet
        all_gates = self.datasheets.get(chip_type, {})
        all_pins = set()
        vcc_pin = None
        gnd_pin = None
        
        for gate_data in all_gates.values():
            all_pins.update(gate_data['input_pins'])
            all_pins.add(gate_data['output_pin'])
            vcc_pin = gate_data['vcc_pin']
            gnd_pin = gate_data['gnd_pin']
        
        # Register all pin positions (scaled to actual position with adjusted IC placement)
        for pin, pos in pin_positions.items():
            actual_x = ic_x + pos['x'] * scale
            actual_y = ic_y + pos['y'] * scale
            self.pin_positions[chip_id][pin] = {'x': actual_x, 'y': actual_y}
            
            # Add pin labels
            if pin in all_pins:
                # I/O pin - show in green or blue
                color = '#4CAF50' if pin in [g['output_pin'] for g in all_gates.values()] else '#2196F3'
                label_x = actual_x - 12 if pin <= (total_pins // 2) else actual_x + 12
                anchor = 'end' if pin <= (total_pins // 2) else 'start'
                svg_parts.append(f'    <text x="{label_x}" y="{actual_y + 4}" font-family="Arial" '
                                f'font-size="10" font-weight="bold" text-anchor="{anchor}" fill="{color}">{pin}</text>')
            elif pin == vcc_pin:
                # VCC pin
                label_x = actual_x + 12
                svg_parts.append(f'    <text x="{label_x}" y="{actual_y + 4}" font-family="Arial" '
                                f'font-size="10" font-weight="bold" text-anchor="start" fill="#FF5722">VCC</text>')
            elif pin == gnd_pin:
                # GND pin
                label_x = actual_x - 12
                svg_parts.append(f'    <text x="{label_x}" y="{actual_y + 4}" font-family="Arial" '
                                f'font-size="10" font-weight="bold" text-anchor="end" fill="#607D8B">GND</text>')
        
        # VCC and GND labels at bottom of box (like regular chips)
        if vcc_pin and gnd_pin:
            svg_parts.append(f'    <text x="{x + 10}" y="{y + box_height - 10}" '
                            f'font-family="Arial" font-size="12" fill="red">VCC:{vcc_pin}</text>')
            svg_parts.append(f'    <text x="{x + box_width - 70}" y="{y + box_height - 10}" '
                            f'font-family="Arial" font-size="12" fill="blue">GND:{gnd_pin}</text>')
        
        return '\n'.join(svg_parts)
    
    def create_chip_svg(self, chip_id, chip_data, x, y):
        """Create SVG for a chip showing all gates of that chip type"""
        svg_parts = []
        chip_type = chip_data['chip_type']
        
        # Check if this is a custom IC chip (non-gate chip)
        if chip_data.get('is_custom_ic', False):
            return self.create_custom_ic_svg(chip_id, chip_data, x, y)
        
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
            
            # Gate symbol (Inlined for compatibility)
            sym_data = self.symbol_manager.gate_symbols.get(gate_type)
            if sym_data:
                sx = gate_width / 512
                sy = gate_height / 512
                fill = sym_data.get("fill", "black")
                stroke = sym_data.get("stroke", fill)
                stroke_width = sym_data.get("stroke_width", "8")
                
                svg_parts.append(f'      <g transform="translate({gate_x}, {gate_y}) scale({sx}, {sy})">')
                svg_parts.append(f'        <path d="{sym_data["path"]}" fill="{fill}" '
                                f'stroke="{stroke}" stroke-width="{stroke_width}" stroke-linejoin="round"/>')
                svg_parts.append(f'      </g>')
            else:
                # Fallback to use if not found (should not happen)
                svg_parts.append(f'      <use xlink:href="#{gate_type}" x="{gate_x}" y="{gate_y}" '
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
        
        # VCC and GND at bottom (skip for passive components like resistors/capacitors)
        # Check if this is a passive component
        first_gate = list(all_gates.values())[0]
        is_passive = first_gate['gate_type'] in ['RESISTOR', 'CAPACITOR']
        
        if not is_passive:
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
        
        # Register boundary with router if available
        if self.router:
            self.router.add_chip_boundary(x, y, box_width, box_height)

        # Initialize proper storage if not exists
        if 'output' not in self.pin_positions:
            self.pin_positions['output'] = {}

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
            led_center_y = output_y + output_size // 2
            
            # Calculate rotated tip position (originally at 366/512 from top)
            # After 180 flip, it's at (1 - 366/512) from top
            tip_offset = (1.0 - 366/512) * output_size
            
            # Register connection point (at the tip of the base, now at top)
            target_x = led_center_x
            target_y = output_y + tip_offset
            self.pin_positions['output'][output_data["name"]] = {'x': target_x, 'y': target_y}

            # LED/Lightbulb icon from DB folder - Rotated 180 (Inlined)
            sym_data = self.symbol_manager.gate_symbols.get("LED")
            if sym_data:
                sx = output_size / 512
                sy = output_size / 512
                svg_parts.append(f'    <g transform="rotate(180, {led_center_x}, {led_center_y})">')
                svg_parts.append(f'      <g transform="translate({output_x}, {output_y}) scale({sx}, {sy})">')
                svg_parts.append(f'        <path d="{sym_data["path"]}" fill="{sym_data.get("fill", "black")}" '
                                f'stroke="{sym_data.get("fill", "black")}" stroke-width="8" stroke-linejoin="round"/>')
                svg_parts.append(f'      </g>')
                svg_parts.append(f'    </g>')
            else:
                svg_parts.append(f'    <use xlink:href="#LED" x="{output_x}" y="{output_y}" '
                                f'width="{output_size}" height="{output_size}" '
                                f'transform="rotate(180, {led_center_x}, {led_center_y})"/>')
            
            # Output label below lightbulb
            svg_parts.append(f'    <text x="{led_center_x}" y="{output_y + output_size + 15}" '
                            f'font-family="Arial" font-size="12" font-weight="bold" '
                            f'text-anchor="middle" fill="green">{output_data["name"]}</text>')
            
            # (Yellow line removed)
            
        return '\n'.join(svg_parts)
    
    def create_display_module(self, x, y, displays):
        """Create 7-segment displays for circuit outputs"""
        if not displays:
            return ""
        
        svg_parts = []
        
        # Calculate box dimensions based on number of displays
        display_width = 80
        display_height = 140
        display_spacing = 30
        box_width = 200
        box_height = 80 + len(displays) * (display_height + display_spacing)
        
        # Display container box
        svg_parts.append(f'    <rect x="{x}" y="{y}" width="{box_width}" height="{box_height}" '
                        f'fill="none" stroke="black" stroke-width="2" rx="5"/>')
        
        # Register boundary with router if available
        if self.router:
            self.router.add_chip_boundary(x, y, box_width, box_height)

        # Initialize proper storage if not exists
        if 'display' not in self.pin_positions:
            self.pin_positions['display'] = {}

        # Title
        svg_parts.append(f'    <text x="{x + box_width//2}" y="{y + 25}" '
                        f'font-family="Arial" font-size="16" font-weight="bold" '
                        f'text-anchor="middle" fill="black">DISPLAYS</text>')
        
        # Draw each display as a 7-segment
        display_y_start = y + 60
        for idx, display_data in enumerate(displays):
            display_y = display_y_start + idx * (display_height + display_spacing)
            display_x = x + (box_width - display_width) // 2
            display_center_x = display_x + display_width // 2
            display_center_y = display_y + display_height // 2
            
            # Load 7-segment SVG
            seg_svg_data = self.symbol_manager.load_full_ic_svg("7Segment")
            if not seg_svg_data:
                # Try to load it with load_gate_svg if not already loaded
                sym_data = self.symbol_manager.load_gate_svg("7Segment")
                if sym_data:
                    self.symbol_manager.gate_symbols["7Segment"] = sym_data
            
            # Calculate scale to fit display dimensions
            if seg_svg_data:
                # Parse viewBox to get dimensions
                viewBox_parts = seg_svg_data['viewBox'].split()
                svg_width = float(viewBox_parts[2]) if len(viewBox_parts) >= 3 else 535.15647
                svg_height = float(viewBox_parts[3]) if len(viewBox_parts) >= 4 else 894.135
                scale_x = display_width / svg_width
                scale_y = display_height / svg_height
                scale = min(scale_x, scale_y)
            else:
                scale = 0.15
            
            # Register connection points for each segment (a-g) and dp
            # For 7-segment: a=top, b=top-right, c=bottom-right, d=bottom, e=bottom-left, f=top-left, g=middle
            segments = display_data.get('segments', ['a', 'b', 'c', 'd', 'e', 'f', 'g'])
            
            # Position connection points on the left side of the display
            segment_spacing = display_height / (len(segments) + 1)
            for seg_idx, segment in enumerate(segments):
                conn_x = display_x - 10
                conn_y = display_y + segment_spacing * (seg_idx + 1)
                segment_name = f"{display_data['name']}_{segment}"
                self.pin_positions['display'][segment_name] = {'x': conn_x, 'y': conn_y}
                
                # Draw small circle for connection point
                svg_parts.append(f'    <circle cx="{conn_x}" cy="{conn_y}" r="3" '
                                f'fill="#2196F3" stroke="black" stroke-width="1"/>')
                # Label
                svg_parts.append(f'    <text x="{conn_x - 8}" y="{conn_y + 4}" '
                                f'font-family="Arial" font-size="9" font-weight="bold" '
                                f'text-anchor="end" fill="#2196F3">{segment}</text>')
            
            if seg_svg_data:
                # Render 7-segment display using full SVG content
                svg_parts.append(f'    <g transform="translate({display_x}, {display_y}) scale({scale})">')
                svg_parts.append('      ' + seg_svg_data['content'])
                svg_parts.append(f'    </g>')
            else:
                # Fallback rectangle
                svg_parts.append(f'    <rect x="{display_x}" y="{display_y}" width="{display_width}" height="{display_height}" '
                                f'fill="#333" stroke="#ff4a00" stroke-width="2" rx="5"/>')
            
            # Display label below
            svg_parts.append(f'    <text x="{display_center_x}" y="{display_y + display_height + 20}" '
                            f'font-family="Arial" font-size="12" font-weight="bold" '
                            f'text-anchor="middle" fill="#ff4a00">{display_data["name"]}</text>')
        
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
        
        # Register boundary with router if available to prevent turns inside
        if self.router:
            self.router.add_chip_boundary(x, y, box_width, box_height)

        # Initialize proper storage if not exists
        if 'input' not in self.pin_positions:
            self.pin_positions['input'] = {}

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
                            f'fill="none" stroke="black" stroke-width="2"/>')
            
            # Input label inside square
            svg_parts.append(f'    <text x="{input_x + input_size//2}" y="{input_y + input_size//2 + 5}" '
                            f'font-family="Arial" font-size="16" font-weight="bold" '
                            f'text-anchor="middle" fill="black">{input_data["name"]}</text>')
            
            # Register connection point (right edge of input square)
            conn_x = input_x + input_size
            conn_y = input_y + input_size//2
            self.pin_positions['input'][input_data["name"]] = {'x': conn_x, 'y': conn_y}
        
        return '\n'.join(svg_parts)
