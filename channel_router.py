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
        # cells[x][y] = set of flags: 'OBSTACLE', 'H_WIRE', 'V_WIRE'
        self.cells = [[set() for _ in range(self.rows)] for _ in range(self.cols)]
        
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

    def _find_escape_path(self, start_c, start_r):
        """BFS to find path to nearest free cell. Returns (end_node, path_to_end)."""
        # If already free, return it
        if self._is_free(start_c, start_r): 
            return ((start_c, start_r), [(start_c, start_r)])
            
        q = [(start_c, start_r)]
        visited = { (start_c, start_r): None }
        
        found_exit = None
        
        # BFS
        while q:
            curr = q.pop(0)
            if self._is_free(curr[0], curr[1]):
                found_exit = curr
                break
            
            # Limit search depth roughly
            if len(visited) > 2000: continue 

            cx, cy = curr
            for dc, dr in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = cx + dc, cy + dr
                if 0 <= nx < self.cols and 0 <= ny < self.rows:
                    if (nx, ny) not in visited:
                        visited[(nx, ny)] = curr
                        q.append((nx, ny))
                        
        if not found_exit:
            # Should not happen unless map is full
            return ((start_c, start_r), [(start_c, start_r)])

        # Reconstruct path
        path = []
        curr = found_exit
        while curr is not None:
            path.append(curr)
            curr = visited[curr]
        path.reverse() # [Start, ..., Exit]
        return (found_exit, path)

    def route_net(self, x1, y1, x2, y2, wire_id=None, prefer_horizontal=True):
        sc, sr = int(round(x1 / self.grid_size)), int(round(y1 / self.grid_size))
        ec, er = int(round(x2 / self.grid_size)), int(round(y2 / self.grid_size))
        
        # 1. Escape Phase with PATHS
        esc_start, path_start = self._find_escape_path(sc, sr)
        esc_end, path_end = self._find_escape_path(ec, er)
        # path_end is [End, ..., Exit]. 
        
        # 2. Main Routing Phase: A* between escape points
        def solve_astar(strict_obstacles=True):
            queue = [(0, 0, esc_start, None)] 
            came_from = {} 
            cost_so_far = {esc_start: 0}
            target_found = False
            
            while queue:
                _, current_cost, current, prev_dir = heapq.heappop(queue)
                
                if current == esc_end:
                    target_found = True
                    break
                    
                for next_node, move_dir in self._get_neighbors(current):
                    nc, nr = next_node
                    cell_flags = self.cells[nc][nr]
                    dx, dy = move_dir
                    
                    # Strict vs Relaxed
                    is_obstacle = 'OBSTACLE' in cell_flags and next_node != esc_end
                    
                    if strict_obstacles and is_obstacle:
                        continue

                    # Wire Overlap Check - always strict about OTHER wires?
                    # Or should we relax that too? 
                    # Let's keep wires strict to avoiding shorts. 
                    # If blocked by wires, we might need to cross chips?
                    if dx != 0 and 'H_WIRE' in cell_flags: continue
                    if dy != 0 and 'V_WIRE' in cell_flags: continue
                    
                    # Cost function
                    move_cost = 1
                    
                    # Obstacle Penalty (in relaxed mode)
                    if is_obstacle:
                        move_cost += 10000 # Huge penalty to discourage crossing chips unless necessary
                    
                    # Bend Penalty
                    if prev_dir is not None and move_dir != prev_dir: move_cost += 5 
                    
                    # Crossing Penalty
                    if dx != 0 and 'V_WIRE' in cell_flags: move_cost += 5 
                    if dy != 0 and 'H_WIRE' in cell_flags: move_cost += 5
                    
                    new_cost = current_cost + move_cost
                    if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                        cost_so_far[next_node] = new_cost
                        dist = abs(esc_end[0] - next_node[0]) + abs(esc_end[1] - next_node[1])
                        priority = new_cost + dist
                        heapq.heappush(queue, (priority, new_cost, next_node, move_dir))
                        came_from[next_node] = (current, move_dir)
            return target_found, came_from

        # Try Strict Pass
        found, came_from = solve_astar(strict_obstacles=True)
        
        # If failed, Try Relaxed Pass
        if not found:
            # print(f"Info: A* strict failed for wire {wire_id}. Retrying with relaxed rules.")
            found, came_from = solve_astar(strict_obstacles=False)
        
        # 3. Path Reconstruction
        full_grid_path = []
        
        if not found:
             print(f"Warning: A* ALL attempts failed for wire {wire_id}.")
             full_grid_path = [(sc, sr), (ec, sr), (ec, er)]
        else:
            # Reconstruct Main A* Path
            curr = esc_end
            main_path = [curr]
            while curr != esc_start:
                entry = came_from.get(curr)
                if not entry: break
                parent, _ = entry
                main_path.append(parent)
                curr = parent
            main_path.reverse() # [EscStart, ..., EscEnd]
            
            # Combine: path_start + main_path + reversed(path_end)
            
            full_grid_path = []
            full_grid_path.extend(path_start)
            
            if main_path and main_path[0] == full_grid_path[-1]:
                full_grid_path.extend(main_path[1:])
            else:
                full_grid_path.extend(main_path)
                
            path_end_rev = list(reversed(path_end))
            if path_end_rev and path_end_rev[0] == full_grid_path[-1]:
                full_grid_path.extend(path_end_rev[1:])
            else:
                full_grid_path.extend(path_end_rev)

        # Mark occupied cells
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
                    if dx_step != 0: self.cells[mx][my].add('H_WIRE')
                    if dy_step != 0: self.cells[mx][my].add('V_WIRE')

        # Simplify to waypoints
        waypoints = []
        if not full_grid_path: return []

        waypoints.append((full_grid_path[0][0] * self.grid_size, full_grid_path[0][1] * self.grid_size))
        
        last_dir = None
        for i in range(1, len(full_grid_path)):
            curr = full_grid_path[i]
            prev = full_grid_path[i-1]
            dx = curr[0] - prev[0]
            dy = curr[1] - prev[1]
            
            if dx == 0 and dy == 0: continue
            
            curr_dir = (0, 0)
            if dx != 0: curr_dir = (1 if dx > 0 else -1, 0)
            if dy != 0: curr_dir = (0, 1 if dy > 0 else -1)
            
            if curr_dir != last_dir:
                if last_dir is not None:
                     waypoints.append((prev[0] * self.grid_size, prev[1] * self.grid_size))
                last_dir = curr_dir
        
        last_pt = full_grid_path[-1]
        waypoints.append((last_pt[0] * self.grid_size, last_pt[1] * self.grid_size))
        
        return waypoints
