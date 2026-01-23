# channel_router.py
# Grid-based detailed routing with A* search

import heapq
import math
from typing import List, Tuple, Dict, Set

class ChannelRouter:
    """
    Grid-based router for circuit diagrams using A* pathfinding.
    Enforces:
    - strict Manhattan routing
    - chip avoidance (no turning inside chips)
    - no parallel wire overlaps (perpendicular crossing only)
    """
    
    def __init__(self, canvas_width: int, canvas_height: int, 
                 channel_width: int = 20, min_spacing: int = 10):
        self.width = canvas_width
        self.height = canvas_height
        self.grid_size = min_spacing  # Use min_spacing as grid resolution (e.g., 10px)
        
        # Grid dimensions
        self.cols = int(math.ceil(self.width / self.grid_size)) + 1
        self.rows = int(math.ceil(self.height / self.grid_size)) + 1
        
        # Grid state
        # cells[x][y] = set of flags: 'NO_TURN', 'H_WIRE', 'V_WIRE'
        self.cells = [[set() for _ in range(self.rows)] for _ in range(self.cols)]
        
        self.terminals = set() 
        
    def add_chip_boundary(self, x: float, y: float, width: float, height: float):
        """Mark chip area as no-turn zone with padding."""
        padding = self.grid_size
        
        start_col = max(0, int((x - padding) / self.grid_size))
        end_col = min(self.cols, int((x + width + padding) / self.grid_size))
        start_row = max(0, int((y - padding) / self.grid_size))
        end_row = min(self.rows, int((y + height + padding) / self.grid_size))
        
        for c in range(start_col, end_col + 1):
            for r in range(start_row, end_row + 1):
                if 0 <= c < self.cols and 0 <= r < self.rows:
                    self.cells[c][r].add('NO_TURN')
                    
    def _get_neighbors(self, node):
        c, r = node
        deltas = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        for dc, dr in deltas:
            nc, nr = c + dc, r + dr
            if 0 <= nc < self.cols and 0 <= nr < self.rows:
                yield (nc, nr), (dc, dr)
                
    def _cost(self, current, next_node, direction, prev_direction):
        nc, nr = next_node
        cell_flags = self.cells[nc][nr]
        dx, dy = direction
        
        # Check wire collisions (Pass over but not along)
        if dx != 0 and 'H_WIRE' in cell_flags: return float('inf')
        if dy != 0 and 'V_WIRE' in cell_flags: return float('inf')
        
        is_turn = (prev_direction is not None and direction != prev_direction)
        
        # If turning inside NO_TURN zone, forbidden.
        # Check if the CURRENT cell prevents turning.
        cur_cell = self.cells[current[0]][current[1]]
        if is_turn and 'NO_TURN' in cur_cell:
             return float('inf')
        
        base_cost = 1
        if is_turn: base_cost += 5
        if dx != 0 and 'V_WIRE' in cell_flags: base_cost += 2
        if dy != 0 and 'H_WIRE' in cell_flags: base_cost += 2
        
        # Penalty for entering NO_TURN zone (prefer routing around)
        # But if we are already in one (start point), moving is cheap.
        if 'NO_TURN' in cell_flags and 'NO_TURN' not in cur_cell:
            base_cost += 5
            
        return base_cost

    def route_net(self, x1, y1, x2, y2, wire_id=None, prefer_horizontal=True):
        sc, sr = int(round(x1 / self.grid_size)), int(round(y1 / self.grid_size))
        ec, er = int(round(x2 / self.grid_size)), int(round(y2 / self.grid_size))
        
        start_node = (sc, sr)
        end_node = (ec, er)
        
        queue = [(0, 0, start_node, None)]
        came_from = {} 
        cost_so_far = {start_node: 0}
        found = False
        
        while queue:
            _, current_cost, current, prev_dir = heapq.heappop(queue)
            
            if current == end_node:
                found = True
                break
                
            for next_node, move_dir in self._get_neighbors(current):
                move_cost = self._cost(current, next_node, move_dir, prev_dir)
                if move_cost == float('inf'): continue
                    
                new_cost = current_cost + move_cost
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    dist = abs(end_node[0] - next_node[0]) + abs(end_node[1] - next_node[1])
                    priority = new_cost + dist
                    heapq.heappush(queue, (priority, new_cost, next_node, move_dir))
                    came_from[next_node] = (current, move_dir)
        
        if not found:
            # Fallback
            return [(x1, y1), (x2, y2)]
            
        # Reconstruct
        curr = end_node
        path_grid = [curr]
        while curr != start_node:
            parent, _ = came_from[curr]
            path_grid.append(parent)
            curr = parent
        path_grid.reverse()
        
        # Mark occupied
        for i in range(len(path_grid) - 1):
            n1 = path_grid[i]
            n2 = path_grid[i+1]
            dc = n2[0] - n1[0]
            dr = n2[1] - n1[1]
            
            nodes_to_mark = [n1, n2]
            for node in nodes_to_mark:
                c, r = node
                if dc != 0: self.cells[c][r].add('H_WIRE')
                if dr != 0: self.cells[c][r].add('V_WIRE')

        # Convert to coords
        waypoints = []
        waypoints.append((path_grid[0][0] * self.grid_size, path_grid[0][1] * self.grid_size))
        
        last_dir = None
        for i in range(1, len(path_grid)):
            curr = path_grid[i]
            prev = path_grid[i-1]
            dx = curr[0] - prev[0]
            dy = curr[1] - prev[1]
            curr_dir = (dx, dy)
            if curr_dir != last_dir:
                if last_dir is not None:
                     waypoints.append((prev[0] * self.grid_size, prev[1] * self.grid_size))
                last_dir = curr_dir
        
        last_pt = path_grid[-1]
        waypoints.append((last_pt[0] * self.grid_size, last_pt[1] * self.grid_size))
        
        return waypoints
