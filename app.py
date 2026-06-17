import os
from flask import Flask, render_template, jsonify, request
import osmnx as ox
import networkx as nx
from shapely.geometry import Polygon, Point
from typing import Set

# Import our custom Monte Carlo engine
from monte_carlo_engine import (
    run_dijkstra,
    run_astar,
    run_dfs,
    get_path_geometry_coords,
    get_path_length_meters,
    run_osm_monte_carlo,
    run_grid_monte_carlo
)

# Import grid pathfinder functions for real-time visualization
from grid_pathfinder import solve_dijkstra, solve_astar, solve_dfs

app = Flask(__name__)

# ========================================================
# 1. Global Setup: Download and Cache OSM Road Network
# ========================================================
print("--- Initialisation : Chargement du réseau OpenStreetMap (Chamonix, France) ---")
ox.settings.use_cache = True
ox.settings.log_console = False

try:
    G_raw = ox.graph_from_place("Chamonix-Mont-Blanc, France", network_type="drive")
    print(f"Graphe OSM chargé. Nœuds : {len(G_raw.nodes)}, Arêtes : {len(G_raw.edges)}")
except Exception as e:
    print(f"Erreur de chargement OSM : {e}. Utilisation du point de repli.")
    G_raw = ox.graph_from_point((45.9227, 6.8685), dist=1500, network_type="drive")
    print(f"Graphe de repli chargé. Nœuds : {len(G_raw.nodes)}, Arêtes : {len(G_raw.edges)}")

# Convert node IDs to strings for cleaner JSON handling
G = nx.relabel_nodes(G_raw, {n: str(n) for n in G_raw.nodes})


# ========================================================
# 2. Main Page Route
# ========================================================
@app.route('/')
def index():
    return render_template('index.html')


# ========================================================
# 3. Interactive Real-Time Grid API
# ========================================================
@app.route('/api/solve', methods=['POST'])
def api_solve_grid():
    data = request.get_json() or {}
    
    rows = data.get('rows', 20)
    cols = data.get('cols', 20)
    
    start_list = data.get('start')
    end_list = data.get('end')
    obstacles_list = data.get('obstacles', [])
    algorithm = data.get('algorithm', 'both')  # 'dijkstra', 'astar', or 'both'
    
    if not start_list or not end_list:
        return jsonify({"error": "Départ et arrivée requis."}), 400
        
    start = (start_list[0], start_list[1])
    end = (end_list[0], end_list[1])
    obstacles = {tuple(obs) for obs in obstacles_list}
    
    results = {}
    
    # Dijkstra
    if algorithm in ('dijkstra', 'both'):
        d_path, d_explored, d_time = solve_dijkstra(rows, cols, start, end, obstacles)
        results['dijkstra'] = {
            'path': d_path,
            'explored': d_explored,
            'duration_ms': d_time,
            'nodes_explored_count': len(d_explored)
        }
        
    # A*
    if algorithm in ('astar', 'both'):
        heuristic_type = data.get('heuristic', 'manhattan')
        a_path, a_explored, a_time = solve_astar(rows, cols, start, end, obstacles, heuristic_type)
        results['astar'] = {
            'path': a_path,
            'explored': a_explored,
            'duration_ms': a_time,
            'nodes_explored_count': len(a_explored)
        }
        
    # DFS
    dfs_path, dfs_explored, dfs_time = solve_dfs(rows, cols, start, end, obstacles)
    results['dfs'] = {
        'path': dfs_path,
        'explored': dfs_explored,
        'duration_ms': dfs_time,
        'nodes_explored_count': len(dfs_explored)
    }
        
    return jsonify(results)


# ========================================================
# 4. Interactive Real-Time OSM API
# ========================================================
@app.route('/api/solve_osm', methods=['POST'])
def api_solve_osm():
    data = request.get_json() or {}
    
    start_ll = data.get('start')  # [lat, lon]
    end_ll = data.get('end')      # [lat, lon]
    obstacle_polygons = data.get('obstacles', [])  # [[[lat, lon], ...], ...]
    heuristic_type = data.get('heuristic', 'great_circle')
    
    if not start_ll or not end_ll:
        return jsonify({"error": "Coordonnées de départ et d'arrivée requises."}), 400
        
    # Match lat/lon to nearest OSM nodes using the raw graph (keys are numeric ints)
    start_node = str(ox.nearest_nodes(G_raw, start_ll[1], start_ll[0]))
    end_node = str(ox.nearest_nodes(G_raw, end_ll[1], end_ll[0]))
    
    # 1. Identify which nodes are blocked by user-drawn polygons
    blocked_nodes: Set[str] = set()
    for poly_coords in obstacle_polygons:
        if len(poly_coords) < 3:
            continue
        polygon = Polygon([(lon, lat) for lat, lon in poly_coords])
        for node, n_data in G.nodes(data=True):
            point = Point(n_data['x'], n_data['y'])
            if polygon.contains(point):
                blocked_nodes.add(node)
                
    # Check if start/end themselves are blocked
    if start_node in blocked_nodes or end_node in blocked_nodes:
        return jsonify({"error": "Départ ou arrivée bloqué par une zone d'obstacle !"}), 400
        
    # 2. Build filtered graph dictionary with lengths as weights
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
    d_geom = get_path_geometry_coords(d_path, G) if d_path else None
    results['dijkstra'] = {
        'path': d_geom,
        'explored': [[coords[n][0], coords[n][1]] for n in d_explored if n in coords],
        'duration_ms': d_time,
        'nodes_explored_count': len(d_explored),
        'path_length_meters': get_path_length_meters(d_path, G) if d_path else 0.0
    }
    
    # Run A*
    a_path, a_explored, a_time = run_astar(graph, coords, start_node, end_node, heuristic_type)
    a_geom = get_path_geometry_coords(a_path, G) if a_path else None
    results['astar'] = {
        'path': a_geom,
        'explored': [[coords[n][0], coords[n][1]] for n in a_explored if n in coords],
        'duration_ms': a_time,
        'nodes_explored_count': len(a_explored),
        'path_length_meters': get_path_length_meters(a_path, G) if a_path else 0.0
    }
    
    # Run DFS
    dfs_path, dfs_explored, dfs_time = run_dfs(graph, start_node, end_node)
    dfs_geom = get_path_geometry_coords(dfs_path, G) if dfs_path else None
    results['dfs'] = {
        'path': dfs_geom,
        'explored': [[coords[n][0], coords[n][1]] for n in dfs_explored if n in coords],
        'duration_ms': dfs_time,
        'nodes_explored_count': len(dfs_explored),
        'path_length_meters': get_path_length_meters(dfs_path, G) if dfs_path else 0.0
    }
    
    # Provide matched start/end actual locations
    results['meta'] = {
        'start_node_coords': [G.nodes[start_node]['y'], G.nodes[start_node]['x']],
        'end_node_coords': [G.nodes[end_node]['y'], G.nodes[end_node]['x']]
    }
    
    return jsonify(results)


# ========================================================
# 5. Monte Carlo OSM API
# ========================================================
@app.route('/api/monte_carlo_osm', methods=['POST'])
def api_monte_carlo_osm():
    data = request.get_json() or {}
    
    start_ll = data.get('start')  # [lat, lon]
    end_ll = data.get('end')      # [lat, lon]
    obstacle_polygons = data.get('obstacles', [])
    trials = int(data.get('trials', 50))
    traffic_level = data.get('traffic_level', 'medium')
    closure_prob = float(data.get('closure_prob', 0.02))
    
    if not start_ll or not end_ll:
        return jsonify({"error": "Coordonnées de départ et d'arrivée requises."}), 400
        
    start_node = str(ox.nearest_nodes(G_raw, start_ll[1], start_ll[0]))
    end_node = str(ox.nearest_nodes(G_raw, end_ll[1], end_ll[0]))
    
    # Identify statically blocked nodes
    blocked_nodes: Set[str] = set()
    for poly_coords in obstacle_polygons:
        if len(poly_coords) < 3:
            continue
        polygon = Polygon([(lon, lat) for lat, lon in poly_coords])
        for node, n_data in G.nodes(data=True):
            point = Point(n_data['x'], n_data['y'])
            if polygon.contains(point):
                blocked_nodes.add(node)
                
    if start_node in blocked_nodes or end_node in blocked_nodes:
        return jsonify({"error": "Le départ ou la destination se situe dans une zone d'obstacle permanent."}), 400
        
    # Run simulation
    sim_results = run_osm_monte_carlo(
        G_osm=G,
        start_node=start_node,
        end_node=end_node,
        blocked_nodes=blocked_nodes,
        trials_count=trials,
        traffic_level=traffic_level,
        closure_prob=closure_prob
    )
    
    if "error" in sim_results:
        return jsonify({"error": sim_results["error"]}), 400
        
    # Inject matched node metadata
    sim_results['meta'] = {
        'start_node_coords': [G.nodes[start_node]['y'], G.nodes[start_node]['x']],
        'end_node_coords': [G.nodes[end_node]['y'], G.nodes[end_node]['x']]
    }
    
    return jsonify(sim_results)


# ========================================================
# 6. Monte Carlo Grid API
# ========================================================
@app.route('/api/monte_carlo_grid', methods=['POST'])
def api_monte_carlo_grid():
    data = request.get_json() or {}
    
    rows = data.get('rows', 20)
    cols = data.get('cols', 20)
    
    start_list = data.get('start')
    end_list = data.get('end')
    obstacles_list = data.get('obstacles', [])
    trials = int(data.get('trials', 50))
    random_obstacle_prob = float(data.get('random_obstacle_prob', 0.15))
    
    if not start_list or not end_list:
        return jsonify({"error": "Départ et arrivée requis."}), 400
        
    start = (start_list[0], start_list[1])
    end = (end_list[0], end_list[1])
    static_obstacles = {tuple(obs) for obs in obstacles_list}
    
    sim_results = run_grid_monte_carlo(
        rows=rows,
        cols=cols,
        start=start,
        end=end,
        static_obstacles=static_obstacles,
        trials_count=trials,
        random_obstacle_prob=random_obstacle_prob
    )
    
    return jsonify(sim_results)


if __name__ == '__main__':
    # Start the server on port 5000
    app.run(debug=True, port=5000)
