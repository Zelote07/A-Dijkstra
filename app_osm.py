from flask import Flask, render_template, jsonify, request
import osmnx as ox
import networkx as nx
from shapely.geometry import Polygon, Point
import heapq
import time
import math
from typing import List, Tuple, Set, Dict, Optional

app = Flask(__name__)

# ========================================================
# 1. Global Setup: Download and Cache OSM Road Network
# ========================================================
print("--- Loading OpenStreetMap network (Chamonix, France) ---")
ox.settings.use_cache = True
ox.settings.log_console = False

# We use Chamonix-Mont-Blanc because it's a beautiful, bounded alpine valley
# network that loads quickly and makes pathfinding/barriers very visual.
try:
    G_raw = ox.graph_from_place("Chamonix-Mont-Blanc, France", network_type="drive")
    print(f"Network loaded. Nodes: {len(G_raw.nodes)}, Edges: {len(G_raw.edges)}")
except Exception as e:
    print(f"Error loading place: {e}. Falling back to point center.")
    G_raw = ox.graph_from_point((45.9227, 6.8685), dist=1500, network_type="drive")
    print(f"Fallback network loaded. Nodes: {len(G_raw.nodes)}, Edges: {len(G_raw.edges)}")

# Convert node IDs to strings for cleaner JSON handling
G = nx.relabel_nodes(G_raw, {n: str(n) for n in G_raw.nodes})


# ========================================================
# 2. Custom Haversine Distance
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
# 3. Pathfinding Algorithms on Generic Graph Dictionary
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
            # Convert degrees lat/lon roughly to meters (1 deg lat ~ 111,000m)
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
        
        for neighbor in graph.get(current, {}):
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
# 4. Helper: Extract Path Geometry along streets
# ========================================================
def get_path_geometry(path: List[str]) -> List[Tuple[float, float]]:
    if not path:
        return []
    coords = []
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i+1]
        edge_data = G.get_edge_data(u, v)
        if edge_data:
            # Use geometry if available, otherwise straight line
            key = list(edge_data.keys())[0]
            data = edge_data[key]
            if 'geometry' in data:
                pts = [(lat, lon) for lon, lat in data['geometry'].coords]
                coords.extend(pts[:-1])
                continue
        # Fallback
        coords.append((G.nodes[u]['y'], G.nodes[u]['x']))
    coords.append((G.nodes[path[-1]]['y'], G.nodes[path[-1]]['x']))
    return coords


def get_path_length(path: List[str]) -> float:
    if not path:
        return 0.0
    total_len = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        edge_data = G.get_edge_data(u, v)
        if edge_data:
            key = list(edge_data.keys())[0]
            total_len += edge_data[key].get('length', 0.0)
    return total_len


# ========================================================
# 5. Flask Endpoints
# ========================================================

@app.route('/')
def index():
    return render_template('index_osm.html')


@app.route('/api/solve_osm', methods=['POST'])
def solve_osm():
    data = request.get_json() or {}
    
    start_ll = data.get('start')  # [lat, lon]
    end_ll = data.get('end')      # [lat, lon]
    obstacle_polygons = data.get('obstacles', [])  # [[[lat, lon], ...], ...]
    heuristic_type = data.get('heuristic', 'great_circle')
    
    if not start_ll or not end_ll:
        return jsonify({"error": "Start and End coordinates required."}), 400
        
    # Match lat/lon to nearest OSM nodes
    start_node = str(ox.nearest_nodes(G_raw, start_ll[1], start_ll[0]))
    end_node = str(ox.nearest_nodes(G_raw, end_ll[1], end_ll[0]))
    
    # 1. Identify which nodes are blocked by user-drawn polygons
    blocked_nodes: Set[str] = set()
    for poly_coords in obstacle_polygons:
        if len(poly_coords) < 3:
            continue
        # Shapely expects coordinates in (longitude, latitude)
        polygon = Polygon([(lon, lat) for lat, lon in poly_coords])
        for node, n_data in G.nodes(data=True):
            point = Point(n_data['x'], n_data['y'])
            if polygon.contains(point):
                blocked_nodes.add(node)
                
    # Check if start/end themselves are blocked. If so, don't search
    if start_node in blocked_nodes or end_node in blocked_nodes:
        return jsonify({"error": "Départ ou arrivée bloqué par une zone d'obstacle !"}), 400
        
    # 2. Build filtered graph dictionary
    graph = {}
    coords = {}
    
    # Fill coordinates for active nodes
    for n, n_data in G.nodes(data=True):
        if n not in blocked_nodes:
            coords[n] = (n_data['y'], n_data['x'])
            graph[n] = {}
            
    # Add active edges
    for u, v, e_data in G.edges(data=True):
        if u not in blocked_nodes and v not in blocked_nodes:
            weight = e_data.get('length', 0.0)
            if v in graph[u]:
                graph[u][v] = min(graph[u][v], weight)
            else:
                graph[u][v] = weight
                
    results = {}
    
    # Run Dijkstra
    d_path, d_explored, d_time = run_dijkstra(graph, start_node, end_node)
    d_geom = get_path_geometry(d_path) if d_path else None
    results['dijkstra'] = {
        'path': d_geom,
        'explored': [[coords[n][0], coords[n][1]] for n in d_explored if n in coords],
        'duration_ms': d_time,
        'nodes_explored_count': len(d_explored),
        'path_length_meters': get_path_length(d_path) if d_path else 0.0
    }
    
    # Run A*
    a_path, a_explored, a_time = run_astar(graph, coords, start_node, end_node, heuristic_type)
    a_geom = get_path_geometry(a_path) if a_path else None
    results['astar'] = {
        'path': a_geom,
        'explored': [[coords[n][0], coords[n][1]] for n in a_explored if n in coords],
        'duration_ms': a_time,
        'nodes_explored_count': len(a_explored),
        'path_length_meters': get_path_length(a_path) if a_path else 0.0
    }
    
    # Run DFS
    dfs_path, dfs_explored, dfs_time = run_dfs(graph, start_node, end_node)
    dfs_geom = get_path_geometry(dfs_path) if dfs_path else None
    results['dfs'] = {
        'path': dfs_geom,
        'explored': [[coords[n][0], coords[n][1]] for n in dfs_explored if n in coords],
        'duration_ms': dfs_time,
        'nodes_explored_count': len(dfs_explored),
        'path_length_meters': get_path_length(dfs_path) if dfs_path else 0.0
    }
    
    # Provide matched start/end actual locations
    results['meta'] = {
        'start_node_coords': [G.nodes[start_node]['y'], G.nodes[start_node]['x']],
        'end_node_coords': [G.nodes[end_node]['y'], G.nodes[end_node]['x']]
    }
    
    return jsonify(results)


if __name__ == '__main__':
    # Serve on port 5001 to avoid port collision with the grid app (port 5000)
    app.run(debug=True, port=5001)
