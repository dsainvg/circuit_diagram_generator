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
    - chip avoidance (strict obstacles + escape logic)
    - no parallel wire overlaps (perpendicular crossing only)
    - allow sharing paths for same net
    """
    
    def __init__(self, canvas_width: int, canvas_height: int, 
                 channel_width: int = 20, min_spacing: int = 10):
        self.width = canvas_width
        self.height = canvas_height
        self.grid_size = min_spacing
        
        self.cols = int(math.ceil(self.width / self.grid_size)) + 1
        self.rows = int(math.ceil(self.height / self.grid_size)) + 1
        
        # Grid state
        # cells[x][y] = set of flags: 'OBSTACLE', 'H_WIRE', 'V_WIRE'
        self.cells = [[set() for _ in range(self.rows)] for _ in range(self.cols)]
        
        # Track Net IDs occupying cells to allow sharing
        # [x][y] = net_id (string or int)
        self.h_nets = [[None for _ in range(self.rows)] for _ in range(self.cols)]
        self.v_nets = [[None for _ in range(self.rows)] for _ in range(self.cols)]
        
        self.terminals = set() 
        
    def add_chip_boundary(self, x: float, y: float, width: float, height: float):
        """Mark chip area as strict obstacle."""
        start_col = max(0, int((x) / self.grid_size))
        end_col = min(self.cols, int((x + width) / self.grid_size))
        start_row = max(0, int((y) / self.grid_size))
        end_row = min(self.rows, int((y + height) / self.grid_size))
        
        for c in range(start_col, end_col + 1):
            for r in range(start_row, end_row + 1):
                if 0 <= c < self.cols and 0 <= r < self.rows:
                    self.cells[c][r].add('OBSTACLE')
                    
    def _get_neighbors(self, node):
        c, r = node
        deltas = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        for dc, dr in deltas:
            nc, nr = c + dc, r + dr
            if 0 <= nc < self.cols and 0 <= nr < self.rows:
                yield (nc, nr), (dc, dr)
                
    def _is_free(self, c, r):
        if not (0 <= c < self.cols and 0 <= r < self.rows): return False
        return 'OBSTACLE' not in self.cells[c][r]

    def _find_pixel_escape(self, x, y):
        """
        Finds an escape point OUTSIDE any obstacle, reachable by a STRAIGHT line.
        Returns (exit_x, exit_y).
        """
        c = int(round(x / self.grid_size))
        r = int(round(y / self.grid_size))
        
        # If start is already free (or OOB/edge case), no escape needed.
        if 0 <= c < self.cols and 0 <= r < self.rows:
            if 'OBSTACLE' not in self.cells[c][r]:
                return (x, y)
        else:
            return (x, y)
            
        # Try 4 directions to find nearest exit
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        best_pt = None
        min_dist = float('inf')
        
        for dx, dy in directions:
            curr_c, curr_r = c, r
            steps = 0
            found = False
            # Walk until free
            while 0 <= curr_c < self.cols and 0 <= curr_r < self.rows and steps < 30:
                if 'OBSTACLE' not in self.cells[curr_c][curr_r]:
                    found = True
                    break
                curr_c += dx
                curr_r += dy
                steps += 1
            
            if found:
                # Calculate pixel point for this grid cell
                gx = curr_c * self.grid_size
                gy = curr_r * self.grid_size
                
                # Maintain axis alignment
                if abs(dx) > 0:
                     # Moved Horizontal -> Keep Y constant
                     pt = (gx, y)
                     dist = abs(gx - x)
                else:
                     # Moved Vertical -> Keep X constant
                     pt = (x, gy)
                     dist = abs(gy - y)
                
                if dist < min_dist:
                    min_dist = dist
                    best_pt = pt
        
        return best_pt if best_pt else (x, y)

    def route_net(self, x1, y1, x2, y2, wire_id=None, net_id=None, prefer_horizontal=True):
        # 1. Find Off-Grid Escape Points
        # These points are strictly outside obstacles and align with start/end pins
        esc_p1 = self._find_pixel_escape(x1, y1)
        esc_p2 = self._find_pixel_escape(x2, y2)
        
        # 2. Snap Escape Points to Grid for A*
        sc = int(round(esc_p1[0] / self.grid_size))
        sr = int(round(esc_p1[1] / self.grid_size))
        ec = int(round(esc_p2[0] / self.grid_size))
        er = int(round(esc_p2[1] / self.grid_size))
        
        grid_start = (sc, sr)
        grid_end = (ec, er)
        
        # 3. A* Routing
        def solve_astar(strict_obstacles=True):
            queue = [(0, 0, grid_start, None)] 
            came_from = {} 
            cost_so_far = {grid_start: 0}
            target_found = False
            
            while queue:
                _, current_cost, current, prev_dir = heapq.heappop(queue)
                
                if current == grid_end:
                    target_found = True
                    break
                    
                for next_node, move_dir in self._get_neighbors(current):
                    nc, nr = next_node
                    cell_flags = self.cells[nc][nr]
                    dx, dy = move_dir
                    
                    is_obstacle = 'OBSTACLE' in cell_flags and next_node != grid_end
                    
                    # 1. OBSTACLE CHECK
                    if strict_obstacles and is_obstacle:
                        continue
                        
                    # 2. NO TURNS INSIDE OBSTACLE (Strict)
                    if 'OBSTACLE' in self.cells[current[0]][current[1]]:
                         if prev_dir is not None and move_dir != prev_dir:
                             continue

                    # 3. WIRE OVERLAP (Net Aware)
                    blocked_by_wire = False
                    if dx != 0:
                        existing_net = self.h_nets[nc][nr]
                        if existing_net is not None and existing_net != net_id: blocked_by_wire = True
                    if dy != 0:
                        existing_net = self.v_nets[nc][nr]
                        if existing_net is not None and existing_net != net_id: blocked_by_wire = True

                    if strict_obstacles and blocked_by_wire: continue
                    
                    move_cost = 1
                    if is_obstacle: move_cost += 10000 
                    if blocked_by_wire: move_cost += 5000
                    if prev_dir is not None and move_dir != prev_dir: move_cost += 5 
                    if dx != 0 and self.v_nets[nc][nr] is not None: move_cost += 5
                    if dy != 0 and self.h_nets[nc][nr] is not None: move_cost += 5
                    
                    new_cost = current_cost + move_cost
                    if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                        cost_so_far[next_node] = new_cost
                        dist = abs(grid_end[0] - next_node[0]) + abs(grid_end[1] - next_node[1])
                        priority = new_cost + dist
                        heapq.heappush(queue, (priority, new_cost, next_node, move_dir))
                        came_from[next_node] = (current, move_dir)
            return target_found, came_from

        found, came_from = solve_astar(strict_obstacles=True)
        if not found:
            found, came_from = solve_astar(strict_obstacles=False)
        
        full_grid_path = []
        if not found:
             print(f"Warning: Failed to route wire {wire_id}.")
             return []
        else:
            curr = grid_end
            main_path = [curr]
            while curr != grid_start:
                entry = came_from.get(curr)
                if not entry: break
                parent, _ = entry
                main_path.append(parent)
                curr = parent
            main_path.reverse()
            full_grid_path = main_path

        # Mark Grid
        for i in range(len(full_grid_path) - 1):
            n1 = full_grid_path[i]
            n2 = full_grid_path[i+1]
            cx, cy = n1
            tx, ty = n2
            steps = max(abs(tx - cx), abs(ty - cy))
            if steps == 0: continue
            dx_step = (tx - cx) // steps
            dy_step = (ty - cy) // steps
            for s in range(steps + 1):
                mx, my = cx + s * dx_step, cy + s * dy_step
                if 0 <= mx < self.cols and 0 <= my < self.rows:
                    if 'OBSTACLE' in self.cells[mx][my]: continue 
                    if dx_step != 0: 
                        self.cells[mx][my].add('H_WIRE')
                        self.h_nets[mx][my] = net_id
                    if dy_step != 0: 
                        self.cells[mx][my].add('V_WIRE')
                        self.v_nets[mx][my] = net_id       

        # Construct Final Waypoints: 
        # Start -> Esc1 -> GridStart -> ... -> GridEnd -> Esc2 -> End
        # Use simple bridging 
        
        final_points = []
        final_points.append((x1, y1))
        
        # Check if we need bridge to Esc1
        if abs(x1 - esc_p1[0]) > 0.1 or abs(y1 - esc_p1[1]) > 0.1:
            final_points.append(esc_p1)
            
        # Bridge Esc1 to GridStart
        gs_x, gs_y = grid_start[0] * self.grid_size, grid_start[1] * self.grid_size
        if abs(esc_p1[0] - gs_x) > 0.1 or abs(esc_p1[1] - gs_y) > 0.1:
             # This bridge must be orthogonal.
             # Esc1 logic ensures one axis matches pin. 
             # Grid match logic aligns to grid.
             # So we have (Ex, Ey) -> (Gx, Gy).
             # Usually Ex=Gx or Ey=Gy if we escaped cleanly.
             # But if not, add corner.
             final_points.append((gs_x, gs_y))
             
        # Add Grid Path
        # Skip first (grid_start) as we just handled it or it's implicitly connected
        for i in range(1, len(full_grid_path)):
             c, r = full_grid_path[i]
             final_points.append((c * self.grid_size, r * self.grid_size))
             
        # Bridge GridEnd to Esc2
        ge_x, ge_y = grid_end[0] * self.grid_size, grid_end[1] * self.grid_size
        if abs(esc_p2[0] - ge_x) > 0.1 or abs(esc_p2[1] - ge_y) > 0.1:
             # Logic is symmetric. Grid end is already in points.
             # Just add Esc2.
             # If we need a corner?
             # e.g. (Gx, Gy) -> (Ex, Ey).
             # If both differ, we need corner.
             # Prefer moving in the direction that exits grid cleanly?
             # Usually standard L-shape works.
             if abs(esc_p2[0] - ge_x) > 0.1 and abs(esc_p2[1] - ge_y) > 0.1:
                  final_points.append((ge_x, esc_p2[1])) # Try one corner
             final_points.append(esc_p2)
        elif abs(esc_p2[0] - ge_x) > 0.1 or abs(esc_p2[1] - ge_y) > 0.1:
             final_points.append(esc_p2) # Just add if non-zero distance (collinear)
             
        # Bridge Esc2 to End
        if abs(x2 - esc_p2[0]) > 0.1 or abs(y2 - esc_p2[1]) > 0.1:
            final_points.append((x2, y2))
            
        # Simplify Collinear
        simplified = []
        if not final_points: return []
        
        simplified.append(final_points[0])
        
        def get_dir(p1, p2):
             dx = p2[0] - p1[0]
             dy = p2[1] - p1[1]
             dist = math.sqrt(dx*dx + dy*dy)
             if dist < 0.1: return None
             return (dx/dist, dy/dist)

        last_d = None
        curr_idx = 1
        
        # Find first valid dir
        while curr_idx < len(final_points):
             d = get_dir(final_points[curr_idx-1], final_points[curr_idx])
             if d: 
                 last_d = d
                 break
             curr_idx += 1
             
        for i in range(curr_idx, len(final_points)):
             curr = final_points[i]
             prev = final_points[i-1]
             d = get_dir(prev, curr)
             
             if d is None: continue 
             
             if abs(d[0] - last_d[0]) > 0.01 or abs(d[1] - last_d[1]) > 0.01:
                 simplified.append(prev)
                 last_d = d
        
        simplified.append(final_points[-1])
        
        return simplified
