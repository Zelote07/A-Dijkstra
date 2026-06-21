import math
import time
import random
import heapq
from typing import List, Tuple, Set, Dict, Optional

# ========================================================
# 1. Custom Haversine Distance
# ========================================================
def haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = (math.sin(dphi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(dlam / 2.0) ** 2))
    return R * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


# ========================================================
# 2. Pathfinding Algorithms on Generic Graph Dictionary
# ========================================================

def run_dijkstra(
    graph: Dict[str, Dict[str, float]], 
    start: str, 
    target: str
) -> Tuple[Optional[List[str]], List[str], float]:
    t_start = time.perf_counter()
    pq: List[Tuple[float, str]] = [(0.0, start)]
    distances: Dict[str, float] = {start: 0.0}
    parents: Dict[str, Optional[str]] = {start: None}
    visited: Set[str] = set()
    explored_order: List[str] = []
    
    path = None
    while pq:
        dist, current = heapq.heappop(pq)
        
        if current == target:
            explored_order.append(current)
            break
            
        if current in visited:
            continue
        visited.add(current)
        explored_order.append(current)
        
        for neighbor, weight in graph.get(current, {}).items():
            if neighbor in visited:
                continue
            new_dist = dist + weight
            if new_dist < distances.get(neighbor, float('inf')):
                distances[neighbor] = new_dist
                parents[neighbor] = current
                heapq.heappush(pq, (new_dist, neighbor))
                
    if target in distances:
        path = []
        curr = target
        while curr is not None:
            path.append(curr)
            curr = parents[curr]
        path.reverse()
        
    duration_ms = (time.perf_counter() - t_start) * 1000.0
    return path, explored_order, duration_ms


def run_astar(
    graph: Dict[str, Dict[str, float]], 
    coords: Dict[str, Tuple[float, float]],
    start: str, 
    target: str,
    heuristic_type: str = 'great_circle'
) -> Tuple[Optional[List[str]], List[str], float]:
    t_start = time.perf_counter()
    target_coord = coords[target]
    
    # Configure A* heuristic
    if heuristic_type == 'euclidean':
        def heuristic(node: str) -> float:
            n_c = coords[node]
            dy = (n_c[0] - target_coord[0]) * 111000.0
            dx = (n_c[1] - target_coord[1]) * 111000.0 * math.cos(math.radians(target_coord[0]))
            return math.sqrt(dx**2 + dy**2)
    elif heuristic_type == 'weighted_manhattan':
        def heuristic(node: str) -> float:
            n_c = coords[node]
            dy = abs(n_c[0] - target_coord[0]) * 111000.0
            dx = abs(n_c[1] - target_coord[1]) * 111000.0 * math.cos(math.radians(target_coord[0]))
            return 3.0 * (dx + dy)
    else:  # 'great_circle' (Haversine)
        def heuristic(node: str) -> float:
            return haversine_distance(coords[node], target_coord)
            
    start_h = heuristic(start)
    pq: List[Tuple[float, float, str]] = [(start_h, 0.0, start)]
    g_scores: Dict[str, float] = {start: 0.0}
    parents: Dict[str, Optional[str]] = {start: None}
    visited: Set[str] = set()
    explored_order: List[str] = []
    
    path = None
    while pq:
        f, g, current = heapq.heappop(pq)
        
        if current == target:
            explored_order.append(current)
            break
            
        if current in visited:
            continue
        visited.add(current)
        explored_order.append(current)
        
        for neighbor, weight in graph.get(current, {}).items():
            if neighbor in visited:
                continue
            tentative_g = g + weight
            if tentative_g < g_scores.get(neighbor, float('inf')):
                g_scores[neighbor] = tentative_g
                parents[neighbor] = current
                f_score = tentative_g + heuristic(neighbor)
                heapq.heappush(pq, (f_score, tentative_g, neighbor))
                
    if target in g_scores:
        path = []
        curr = target
        while curr is not None:
            path.append(curr)
            curr = parents[curr]
        path.reverse()
        
    duration_ms = (time.perf_counter() - t_start) * 1000.0
    return path, explored_order, duration_ms


def run_dfs(
    graph: Dict[str, Dict[str, float]], 
    start: str, 
    target: str
) -> Tuple[Optional[List[str]], List[str], float]:
    t_start = time.perf_counter()
    stack: List[str] = [start]
    visited: Set[str] = set()
    parents: Dict[str, Optional[str]] = {start: None}
    explored_order: List[str] = []
    
    path = None
    while stack:
        current = stack.pop()
        
        if current == target:
            visited.add(current)
            explored_order.append(current)
            break
            
        if current in visited:
            continue
        visited.add(current)
        explored_order.append(current)
        
        # Sort neighbors to ensure deterministic traversal if needed
        neighbors = sorted(list(graph.get(current, {}).keys()))
        for neighbor in neighbors:
            if neighbor not in visited and neighbor not in parents:
                parents[neighbor] = current
                stack.append(neighbor)
                
    if target in visited:
        path = []
        curr = target
        while curr is not None:
            path.append(curr)
            curr = parents[curr]
        path.reverse()
        
    duration_ms = (time.perf_counter() - t_start) * 1000.0
    return path, explored_order, duration_ms


# ========================================================
# 3. Path Helpers
# ========================================================

def get_path_travel_time(path: List[str], graph: Dict[str, Dict[str, float]]) -> float:
    if not path or len(path) < 2:
        return 0.0
    total_time = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        total_time += graph.get(u, {}).get(v, 0.0)
    return total_time


def get_path_length_meters(path: List[str], G) -> float:
    if not path or len(path) < 2:
        return 0.0
    total_len = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        edge_data = G.get_edge_data(u, v)
        if edge_data:
            key = list(edge_data.keys())[0]
            total_len += edge_data[key].get('length', 0.0)
    return total_len


def get_path_geometry_coords(path: List[str], G) -> List[Tuple[float, float]]:
    if not path:
        return []
    coords = []
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i+1]
        edge_data = G.get_edge_data(u, v)
        if edge_data:
            key = list(edge_data.keys())[0]
            data = edge_data[key]
            if 'geometry' in data:
                # geometry contains points as (lon, lat)
                pts = [(lat, lon) for lon, lat in data['geometry'].coords]
                coords.extend(pts[:-1])
                continue
        coords.append((G.nodes[u]['y'], G.nodes[u]['x']))
    coords.append((G.nodes[path[-1]]['y'], G.nodes[path[-1]]['x']))
    return coords


# ========================================================
# 4. Monte Carlo Simulation for OSM Networks
# ========================================================

def run_osm_monte_carlo(
    G_osm,  # Relabeled graph with string nodes
    start_node: str,
    end_node: str,
    blocked_nodes: Set[str],
    trials_count: int,
    traffic_level: str,  # 'low', 'medium', 'heavy', 'extreme'
    closure_prob: float  # probability of link closure
) -> Dict:
    # 1. Clean nodes and extract coordinates
    coords = {}
    for n, n_data in G_osm.nodes(data=True):
        if n not in blocked_nodes:
            coords[n] = (n_data['y'], n_data['x'])

    # 2. Extract active edges and compute base travel times (length / speed_limit)
    active_edges = []
    for u, v, e_data in G_osm.edges(data=True):
        if u not in blocked_nodes and v not in blocked_nodes:
            length = e_data.get('length', 1.0)
            
            # Extract speed limit (default 50 km/h)
            speed_kph = 50.0
            if 'maxspeed' in e_data:
                try:
                    ms = e_data['maxspeed']
                    if isinstance(ms, list):
                        ms = ms[0]
                    # strip text like " km/h" or " mph"
                    ms_clean = str(ms).replace(' km/h', '').replace(' mph', '').strip()
                    val = float(ms_clean)
                    if 'mph' in str(ms):
                        speed_kph = val * 1.60934
                    else:
                        speed_kph = val
                except:
                    pass
            
            speed_ms = speed_kph / 3.6
            t_base = length / speed_ms
            active_edges.append((u, v, t_base))

    # Lognormal parameters mapping for travel time multiplier M = exp(x)
    # where x ~ N(mu, sigma).
    # Expected multiplier E(M) = exp(mu + sigma^2 / 2).
    # We define parameters to represent low/medium/heavy/extreme congestion:
    traffic_params = {
        'low':     {'mu': 0.02, 'sigma': 0.05},  # E(M) ~ 1.03
        'medium':  {'mu': 0.18, 'sigma': 0.15},  # E(M) ~ 1.21
        'heavy':   {'mu': 0.45, 'sigma': 0.30},  # E(M) ~ 1.64
        'extreme': {'mu': 0.75, 'sigma': 0.50}   # E(M) ~ 2.40
    }
    
    params = traffic_params.get(traffic_level, traffic_params['medium'])
    mu = params['mu']
    sigma = params['sigma']
    
    # 3. Pre-calculate Expected Weights for Static Router
    mean_multiplier = math.exp(mu + (sigma ** 2) / 2.0)
    expected_graph = {u: {} for u in coords}
    for u, v, t_base in active_edges:
        expected_time = t_base * mean_multiplier
        if v in expected_graph[u]:
            expected_graph[u][v] = min(expected_graph[u][v], expected_time)
        else:
            expected_graph[u][v] = expected_time
            
    # Calculate static path once on expected graph
    static_path, _, _ = run_dijkstra(expected_graph, start_node, end_node)
    
    # If static path cannot be found on expected graph, search is impossible
    if not static_path:
        return {"error": "Impossible de trouver un itinéraire sur le réseau moyen. Veuillez vérifier les obstacles."}

    # 4. Run Monte Carlo Simulation Loop
    trials_log = []
    
    for trial_idx in range(trials_count):
        # Generate realized travel times for this trial (accidents + congestion)
        realized_graph = {u: {} for u in coords}
        for u, v, t_base in active_edges:
            # Check if edge is randomly blocked (accident/road closure)
            if random.random() < closure_prob:
                continue
            
            # Compute realized travel time
            mult = random.lognormvariate(mu, sigma)
            realized_time = t_base * mult
            
            if v in realized_graph[u]:
                realized_graph[u][v] = min(realized_graph[u][v], realized_time)
            else:
                realized_graph[u][v] = realized_time
                
        # --- Model 1: Dynamic Dijkstra (Theoretical optimum with perfect real-time info) ---
        dyn_dijkstra_path, dyn_dijkstra_explored, dyn_dijkstra_time_ms = run_dijkstra(realized_graph, start_node, end_node)
        
        # --- Model 2: Dynamic A* (Haversine heuristic) ---
        dyn_astar_path, dyn_astar_explored, dyn_astar_time_ms = run_astar(
            realized_graph, coords, start_node, end_node, 'great_circle'
        )
        
        # --- Model 3: Static Routing (Calculated on expected graph, followed with local reroutes if blocked) ---
        static_travel_time_sec = 0.0
        static_path_valid = True
        static_realized_path = []
        
        if dyn_dijkstra_path is None:
            # Graph is disconnected, both models must fail
            static_travel_time_sec = float('inf')
            static_path_valid = False
        else:
            curr_node = start_node
            static_realized_path.append(curr_node)
            
            # Loop until destination is reached or path is declared failed
            while curr_node != end_node:
                # Find the next node in the pre-planned static path
                next_node = None
                try:
                    curr_pos_in_static = static_path.index(curr_node)
                    if curr_pos_in_static < len(static_path) - 1:
                        next_node = static_path[curr_pos_in_static + 1]
                except ValueError:
                    # Current node is not on the static path (we got rerouted earlier)
                    pass
                
                # If we are on the static path and the next segment is OPEN:
                if next_node and next_node in realized_graph[curr_node]:
                    static_travel_time_sec += realized_graph[curr_node][next_node]
                    curr_node = next_node
                    static_realized_path.append(curr_node)
                else:
                    # Reroute needed! Next edge is blocked or we diverged.
                    # Find shortest path from current node to end on the realized graph
                    reroute_path, _, _ = run_dijkstra(realized_graph, curr_node, end_node)
                    if reroute_path:
                        # Follow the reroute path to the end
                        for i in range(len(reroute_path) - 1):
                            u_r = reroute_path[i]
                            v_r = reroute_path[i+1]
                            static_travel_time_sec += realized_graph[u_r][v_r]
                            static_realized_path.append(v_r)
                        curr_node = end_node
                    else:
                        # Reroute failed, isolated
                        static_travel_time_sec = float('inf')
                        static_path_valid = False
                        break
                        
        # Save detailed logs (geometries only for the first 10 trials to prevent huge payloads)
        include_geom = (trial_idx < 10)
        
        trial_record = {
            'trial': trial_idx + 1,
            'dijkstra': {
                'success': dyn_dijkstra_path is not None,
                'travel_time_sec': get_path_travel_time(dyn_dijkstra_path, realized_graph) if dyn_dijkstra_path else None,
                'path_length_meters': get_path_length_meters(dyn_dijkstra_path, G_osm) if dyn_dijkstra_path else 0.0,
                'nodes_explored': len(dyn_dijkstra_explored),
                'computation_ms': dyn_dijkstra_time_ms,
                'path_geom': get_path_geometry_coords(dyn_dijkstra_path, G_osm) if (include_geom and dyn_dijkstra_path) else None
            },
            'astar': {
                'success': dyn_astar_path is not None,
                'travel_time_sec': get_path_travel_time(dyn_astar_path, realized_graph) if dyn_astar_path else None,
                'path_length_meters': get_path_length_meters(dyn_astar_path, G_osm) if dyn_astar_path else 0.0,
                'nodes_explored': len(dyn_astar_explored),
                'computation_ms': dyn_astar_time_ms,
                'path_geom': get_path_geometry_coords(dyn_astar_path, G_osm) if (include_geom and dyn_astar_path) else None
            },
            'static': {
                'success': static_path_valid,
                'travel_time_sec': static_travel_time_sec if static_path_valid else None,
                'path_length_meters': get_path_length_meters(static_realized_path, G_osm) if static_path_valid else 0.0,
                'nodes_explored': 0,  # Pre-calculated static path, no real-time nodes expanded (except small reroutes)
                'computation_ms': 0.0,
                'path_geom': get_path_geometry_coords(static_realized_path, G_osm) if (include_geom and static_path_valid) else None
            }
        }
        
        # Calculate optimality gap for Static and A*
        if trial_record['dijkstra']['success']:
            opt_time = trial_record['dijkstra']['travel_time_sec']
            
            if trial_record['astar']['success']:
                gap = ((trial_record['astar']['travel_time_sec'] - opt_time) / opt_time) * 100.0
                trial_record['astar']['optimality_gap_pct'] = round(gap, 3)
            else:
                trial_record['astar']['optimality_gap_pct'] = None
                
            if trial_record['static']['success']:
                gap = ((trial_record['static']['travel_time_sec'] - opt_time) / opt_time) * 100.0
                trial_record['static']['optimality_gap_pct'] = round(gap, 3)
            else:
                trial_record['static']['optimality_gap_pct'] = None
        else:
            trial_record['astar']['optimality_gap_pct'] = None
            trial_record['static']['optimality_gap_pct'] = None
            
        trials_log.append(trial_record)

    # 5. Compute Aggregated Statistics
    stats = {}
    for model in ['dijkstra', 'astar', 'static']:
        times = [r[model]['travel_time_sec'] for r in trials_log if r[model]['success']]
        nodes = [r[model]['nodes_explored'] for r in trials_log if r[model]['success']]
        comps = [r[model]['computation_ms'] for r in trials_log if r[model]['success']]
        gaps  = [r[model].get('optimality_gap_pct') for r in trials_log if r[model]['success'] and r[model].get('optimality_gap_pct') is not None]
        
        success_count = len(times)
        success_rate = (success_count / trials_count) * 100.0
        
        if success_count > 0:
            mean_time = sum(times) / success_count
            var_time = sum((x - mean_time) ** 2 for x in times) / max(1, success_count - 1)
            std_time = math.sqrt(var_time)
            
            # 95% Confidence Interval for travel time
            ci_half = 1.96 * (std_time / math.sqrt(success_count))
            ci_low = max(0.0, mean_time - ci_half)
            ci_high = mean_time + ci_half
            
            # 90th percentile of travel time
            sorted_times = sorted(times)
            p90_idx = min(success_count - 1, int(math.ceil(0.9 * success_count)) - 1)
            p90_time = sorted_times[p90_idx]
            
            mean_nodes = sum(nodes) / success_count
            mean_comp = sum(comps) / success_count
            mean_gap = sum(gaps) / len(gaps) if gaps else 0.0
        else:
            mean_time = std_time = ci_low = ci_high = p90_time = mean_nodes = mean_comp = mean_gap = 0.0
            
        stats[model] = {
            'success_rate_pct': round(success_rate, 2),
            'mean_travel_time_sec': round(mean_time, 2),
            'std_travel_time_sec': round(std_time, 2),
            'ci_95_sec': [round(ci_low, 2), round(ci_high, 2)],
            'p90_travel_time_sec': round(p90_time, 2),
            'mean_nodes_explored': round(mean_nodes, 1),
            'mean_computation_ms': round(mean_comp, 3),
            'mean_optimality_gap_pct': round(mean_gap, 2)
        }

    return {
        'static_expected_path_geom': get_path_geometry_coords(static_path, G_osm),
        'stats': stats,
        'trials': trials_log
    }


# ========================================================
# 5. Monte Carlo Simulation for Grid Networks
# ========================================================

def get_grid_neighbors(node: Tuple[int, int], rows: int, cols: int, obstacles: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
    r, c = node
    neighbors = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            if (nr, nc) not in obstacles:
                neighbors.append((nr, nc))
    return neighbors


def solve_grid_dijkstra(
    rows: int,
    cols: int,
    start: Tuple[int, int],
    end: Tuple[int, int],
    obstacles: Set[Tuple[int, int]]
) -> Tuple[Optional[List[Tuple[int, int]]], List[Tuple[int, int]], float]:
    t_start = time.perf_counter()
    pq = [(0.0, start)]
    distances = {start: 0.0}
    parents = {start: None}
    visited = set()
    explored_order = []
    
    path = None
    while pq:
        dist, current = heapq.heappop(pq)
        
        if current == end:
            explored_order.append(current)
            break
            
        if current in visited:
            continue
        visited.add(current)
        explored_order.append(current)
        
        for neighbor in get_grid_neighbors(current, rows, cols, obstacles):
            if neighbor in visited:
                continue
            new_dist = dist + 1.0
            if new_dist < distances.get(neighbor, float('inf')):
                distances[neighbor] = new_dist
                parents[neighbor] = current
                heapq.heappush(pq, (new_dist, neighbor))
                
    if end in distances:
        path = []
        curr = end
        while curr is not None:
            path.append(curr)
            curr = parents[curr]
        path.reverse()
        
    duration_ms = (time.perf_counter() - t_start) * 1000.0
    return path, explored_order, duration_ms


def solve_grid_astar(
    rows: int,
    cols: int,
    start: Tuple[int, int],
    end: Tuple[int, int],
    obstacles: Set[Tuple[int, int]],
    heuristic_type: str = 'manhattan'
) -> Tuple[Optional[List[Tuple[int, int]]], List[Tuple[int, int]], float]:
    t_start = time.perf_counter()
    
    if heuristic_type == 'euclidean':
        def heuristic(node: Tuple[int, int]) -> float:
            return float(math.sqrt((node[0] - end[0])**2 + (node[1] - end[1])**2))
    else:  # 'manhattan'
        def heuristic(node: Tuple[int, int]) -> float:
            return float(abs(node[0] - end[0]) + abs(node[1] - end[1]))
            
    start_h = heuristic(start)
    pq = [(start_h, 0.0, start)]
    g_scores = {start: 0.0}
    parents = {start: None}
    visited = set()
    explored_order = []
    
    path = None
    while pq:
        f, g, current = heapq.heappop(pq)
        
        if current == end:
            explored_order.append(current)
            break
            
        if current in visited:
            continue
        visited.add(current)
        explored_order.append(current)
        
        for neighbor in get_grid_neighbors(current, rows, cols, obstacles):
            if neighbor in visited:
                continue
            tentative_g = g + 1.0
            if tentative_g < g_scores.get(neighbor, float('inf')):
                g_scores[neighbor] = tentative_g
                parents[neighbor] = current
                f_score = tentative_g + heuristic(neighbor)
                heapq.heappush(pq, (f_score, tentative_g, neighbor))
                
    if end in g_scores:
        path = []
        curr = end
        while curr is not None:
            path.append(curr)
            curr = parents[curr]
        path.reverse()
        
    duration_ms = (time.perf_counter() - t_start) * 1000.0
    return path, explored_order, duration_ms


def run_grid_monte_carlo(
    rows: int,
    cols: int,
    start: Tuple[int, int],
    end: Tuple[int, int],
    static_obstacles: Set[Tuple[int, int]],
    trials_count: int,
    random_obstacle_prob: float  # probability that an empty cell becomes blocked (percolation)
) -> Dict:
    trials_log = []
    
    for trial_idx in range(trials_count):
        # Generate trial grid obstacles: static obstacles + random ones
        obstacles = set(static_obstacles)
        
        for r in range(rows):
            for c in range(cols):
                if (r, c) == start or (r, c) == end or (r, c) in obstacles:
                    continue
                if random.random() < random_obstacle_prob:
                    obstacles.add((r, c))
                    
        # Dijkstra search
        d_path, d_explored, d_time = solve_grid_dijkstra(rows, cols, start, end, obstacles)
        
        # A* search (Manhattan)
        a_path, a_explored, a_time = solve_grid_astar(rows, cols, start, end, obstacles, 'manhattan')
        
        trial_record = {
            'trial': trial_idx + 1,
            'dijkstra': {
                'success': d_path is not None,
                'path_length': len(d_path) if d_path else None,
                'nodes_explored': len(d_explored),
                'computation_ms': d_time,
                'path': d_path if (trial_idx < 10 and d_path) else None
            },
            'astar': {
                'success': a_path is not None,
                'path_length': len(a_path) if a_path else None,
                'nodes_explored': len(a_explored),
                'computation_ms': a_time,
                'path': a_path if (trial_idx < 10 and a_path) else None
            },
            # We also return obstacles list for first 10 trials to display percolation in browser
            'obstacles': [list(obs) for obs in obstacles] if trial_idx < 10 else None
        }
        
        trials_log.append(trial_record)
        
    # Stats aggregation
    stats = {}
    for model in ['dijkstra', 'astar']:
        successes = [r[model]['path_length'] for r in trials_log if r[model]['success']]
        nodes = [r[model]['nodes_explored'] for r in trials_log if r[model]['success']]
        comps = [r[model]['computation_ms'] for r in trials_log if r[model]['success']]
        
        success_count = len(successes)
        success_rate = (success_count / trials_count) * 100.0
        
        if success_count > 0:
            mean_len = sum(successes) / success_count
            std_len = math.sqrt(sum((x - mean_len)**2 for x in successes) / max(1, success_count - 1))
            mean_nodes = sum(nodes) / success_count
            mean_comp = sum(comps) / success_count
        else:
            mean_len = std_len = mean_nodes = mean_comp = 0.0
            
        stats[model] = {
            'success_rate_pct': round(success_rate, 2),
            'mean_path_length': round(mean_len, 2),
            'std_path_length': round(std_len, 2),
            'mean_nodes_explored': round(mean_nodes, 1),
            'mean_computation_ms': round(mean_comp, 3)
        }
        
    return {
        'stats': stats,
        'trials': trials_log
    }
