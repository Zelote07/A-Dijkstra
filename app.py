import os
import time
import heapq
import math
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
    run_grid_monte_carlo,
    haversine_distance,
    get_path_travel_time
)

# Import grid pathfinder functions for real-time visualization
from grid_pathfinder import solve_dijkstra, solve_astar, solve_dfs

app = Flask(__name__)

# ========================================================
# 1. Global Setup: Download and Cache OSM Road Network
# ========================================================
print("--- Initialisation : Chargement du réseau OpenStreetMap (Aix-en-Provence, France) ---")
ox.settings.use_cache = True
ox.settings.log_console = False

try:
    G_raw = ox.graph_from_place("Aix-en-Provence, France", network_type="drive")
    print(f"Graphe OSM chargé. Nœuds : {len(G_raw.nodes)}, Arêtes : {len(G_raw.edges)}")
except Exception as e:
    print(f"Erreur de chargement OSM : {e}. Utilisation du point de repli.")
    G_raw = ox.graph_from_point((43.5297, 5.4474), dist=2500, network_type="drive")
    print(f"Graphe de repli chargé. Nœuds : {len(G_raw.nodes)}, Arêtes : {len(G_raw.edges)}")

# Convert node IDs to strings for cleaner JSON handling
G = nx.relabel_nodes(G_raw, {n: str(n) for n in G_raw.nodes})

# Load gas stations in Aix-en-Provence
GAS_STATIONS = []
try:
    print("--- Chargement des stations-service à Aix-en-Provence ---")
    try:
        fuel_gdf = ox.features_from_place("Aix-en-Provence, France", tags={"amenity": "fuel"})
    except AttributeError:
        fuel_gdf = ox.geometries_from_place("Aix-en-Provence, France", tags={"amenity": "fuel"})
        
    if fuel_gdf is not None and not fuel_gdf.empty:
        for _, row in fuel_gdf.iterrows():
            geom = row.get('geometry')
            if geom:
                # Extract station name or brand
                name = row.get('name')
                if not name or (isinstance(name, float) and math.isnan(name)):
                    name = row.get('brand')
                if not name or (isinstance(name, float) and math.isnan(name)):
                    name = row.get('operator')
                if not name or (isinstance(name, float) and math.isnan(name)):
                    name = "Station Essence"
                
                if geom.geom_type == 'Point':
                    lat, lon = geom.y, geom.x
                elif geom.geom_type in ['Polygon', 'MultiPolygon']:
                    centroid = geom.centroid
                    lat, lon = centroid.y, centroid.x
                else:
                    continue
                
                # Pre-calculate nearest node in graph
                node_id = str(ox.nearest_nodes(G_raw, lon, lat))
                GAS_STATIONS.append({
                    'coords': [lat, lon],
                    'name': str(name),
                    'node': node_id
                })
    print(f"{len(GAS_STATIONS)} stations-service chargées.")
except Exception as e:
    print(f"Erreur de chargement des stations-service : {e}")

if len(GAS_STATIONS) < 5:
    fallback_data = [
        {"coords": [43.5255, 5.4385], "name": "TotalEnergies - Jas de Bouffan"},
        {"coords": [43.5180, 5.4620], "name": "Esso Express - Aix-en-Provence"},
        {"coords": [43.5350, 5.4290], "name": "Carrefour Fuel - Berre"},
        {"coords": [43.5410, 5.4590], "name": "Shell - Route des Alpes"},
        {"coords": [43.5290, 5.4510], "name": "Avia - Route de Nice"},
        {"coords": [43.5090, 5.4210], "name": "TotalEnergies - Les Milles"},
        {"coords": [43.5520, 5.4410], "name": "BP - Puyricard"},
        {"coords": [43.5220, 5.4190], "name": "Access Total - Galice"},
        {"coords": [43.5305, 5.4640], "name": "Elan - Val de l'Arc"}
    ]
    GAS_STATIONS = []
    for fb in fallback_data:
        lat, lon = fb["coords"]
        node_id = str(ox.nearest_nodes(G_raw, lon, lat))
        GAS_STATIONS.append({
            'coords': [lat, lon],
            'name': fb["name"],
            'node': node_id
        })
    print(f"Utilisation de {len(GAS_STATIONS)} stations de secours.")



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


# ========================================================
# 7. Real-World Scenario Pages and APIs
# ========================================================

import math

def get_node_elevation(lat: float, lon: float) -> float:
    """
    Simulates a realistic topographic height profile for Aix-en-Provence.
    Base altitude is 170m. Altitude increases as one moves north-east towards
    the plateau de Bibémus and Sainte-Victoire.
    """
    dy = lat - 43.5297
    dx = lon - 5.4474
    # Altitude model: base 170m rising up to 500m+ towards North-East
    elevation = 170.0 + (dy * 8000.0 + dx * 6000.0)
    # Add local hills and valleys
    elevation += 80.0 * math.sin(lat * 350.0) * math.sin(lon * 350.0)
    return max(150.0, elevation)


@app.route('/scenarios')
def scenarios():
    """
    Renders the dedicated scenarios page with tabs for Accessibility, Multi-POI and Eco-routing.
    """
    return render_template('scenarios.html')


@app.route('/api/scenarios/isochrone', methods=['POST'])
def api_scenarios_isochrone():
    """
    Calculates the accessibility isochrone using Dijkstra.
    Computes all nodes reachable within a specified travel time in minutes.
    """
    data = request.get_json() or {}
    start_ll = data.get('start')  # [lat, lon]
    max_time_mins = float(data.get('max_time_mins', 15.0))
    
    if not start_ll:
        return jsonify({"error": "Départ requis."}), 400
        
    start_node = str(ox.nearest_nodes(G_raw, start_ll[1], start_ll[0]))
    
    # Build graph with travel times (seconds)
    graph_time = {}
    coords = {}
    for n, n_data in G.nodes(data=True):
        coords[n] = (n_data['y'], n_data['x'])
        graph_time[n] = {}
        
    for u, v, e_data in G.edges(data=True):
        length = e_data.get('length', 1.0)
        speed_kph = 50.0
        if 'maxspeed' in e_data:
            try:
                ms = e_data['maxspeed']
                if isinstance(ms, list):
                    ms = ms[0]
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
        
        if v in graph_time[u]:
            graph_time[u][v] = min(graph_time[u][v], t_base)
        else:
            graph_time[u][v] = t_base
            
    # Dijkstra search bounded by max travel time
    max_time_sec = max_time_mins * 60.0
    pq = [(0.0, start_node)]  # (cumulative_time, node)
    distances = {start_node: 0.0}
    visited = set()
    explored_order = []
    
    t_start = time.perf_counter()
    while pq:
        curr_time, current = heapq.heappop(pq)
        
        if curr_time > max_time_sec:
            continue
            
        if current in visited:
            continue
        visited.add(current)
        explored_order.append(current)
        
        for neighbor, edge_time in graph_time.get(current, {}).items():
            if neighbor in visited:
                continue
            new_time = curr_time + edge_time
            if new_time <= max_time_sec and new_time < distances.get(neighbor, float('inf')):
                distances[neighbor] = new_time
                heapq.heappush(pq, (new_time, neighbor))
                
    duration_ms = (time.perf_counter() - t_start) * 1000.0
    
    # Identify gas stations reachable in this isochrone
    reachable_stations = []
    debug_stations_info = []
    for gs in GAS_STATIONS:
        node_id = gs['node']
        in_distances = node_id in distances
        dist_val = distances.get(node_id) if in_distances else None
        in_graph = node_id in G.nodes
        debug_stations_info.append({
            'name': gs['name'],
            'coords': gs['coords'],
            'node': node_id,
            'in_graph': in_graph,
            'in_distances': in_distances,
            'travel_time_sec': dist_val
        })
        if in_distances:
            reachable_stations.append({
                'name': gs['name'],
                'coords': gs['coords'],
                'time_mins': round(distances[node_id] / 60.0, 1)
            })
    # Sort gas stations by travel time (closest first)
    reachable_stations = sorted(reachable_stations, key=lambda s: s['time_mins'])
    
    # Pack response
    explored_nodes = [
        [coords[n][0], coords[n][1], round(distances[n] / 60.0, 2)] 
        for n in explored_order if n in coords
    ]
    
    return jsonify({
        'explored': explored_nodes,
        'nodes_explored_count': len(explored_order),
        'duration_ms': duration_ms,
        'stations': reachable_stations,
        'debug_stations': debug_stations_info,
        'meta': {
            'start_coords': [G.nodes[start_node]['y'], G.nodes[start_node]['x']]
        }
    })


@app.route('/api/scenarios/nearest_poi', methods=['POST'])
def api_scenarios_nearest_poi():
    """
    Finds the nearest Point of Interest (POI) among a set of candidates using multi-target Dijkstra.
    Stops immediately when the first POI is extracted.
    Candidates are dynamically selected as the 5 closest gas stations from the global GAS_STATIONS list.
    """
    data = request.get_json() or {}
    start_ll = data.get('start')  # [lat, lon]
    
    if not start_ll:
        return jsonify({"error": "Départ requis."}), 400
        
    start_node = str(ox.nearest_nodes(G_raw, start_ll[1], start_ll[0]))
    
    # Dynamically find 5 closest gas stations based on starting coordinates
    from monte_carlo_engine import haversine_distance
    start_coord = (start_ll[0], start_ll[1])
    sorted_gas_stations = sorted(GAS_STATIONS, key=lambda gs: haversine_distance(start_coord, gs['coords']))
    pois_ll = [gs['coords'] for gs in sorted_gas_stations[:5]]
    
    # Map POIs to nearest nodes
    poi_nodes_set = set()
    poi_node_to_index = {}
    for idx, gs in enumerate(sorted_gas_stations[:5]):
        p_node = gs['node']
        poi_nodes_set.add(p_node)
        poi_node_to_index[p_node] = idx
        
    # Build graph with travel times
    graph_time = {}
    coords = {}
    for n, n_data in G.nodes(data=True):
        coords[n] = (n_data['y'], n_data['x'])
        graph_time[n] = {}
        
    for u, v, e_data in G.edges(data=True):
        length = e_data.get('length', 1.0)
        speed_kph = 50.0
        if 'maxspeed' in e_data:
            try:
                ms = e_data['maxspeed']
                if isinstance(ms, list):
                    ms = ms[0]
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
        
        if v in graph_time[u]:
            graph_time[u][v] = min(graph_time[u][v], t_base)
        else:
            graph_time[u][v] = t_base
            
    # Dijkstra search (Multi-target stop condition)
    pq = [(0.0, start_node)]  # (cumulative_time, node)
    distances = {start_node: 0.0}
    parents = {start_node: None}
    visited = set()
    explored_order = []
    
    closest_poi_node = None
    t_start = time.perf_counter()
    
    while pq:
        curr_time, current = heapq.heappop(pq)
        
        # Stop condition: we found the nearest POI
        if current in poi_nodes_set:
            closest_poi_node = current
            explored_order.append(current)
            break
            
        if current in visited:
            continue
        visited.add(current)
        explored_order.append(current)
        
        for neighbor, edge_time in graph_time.get(current, {}).items():
            if neighbor in visited:
                continue
            new_time = curr_time + edge_time
            if new_time < distances.get(neighbor, float('inf')):
                distances[neighbor] = new_time
                parents[neighbor] = current
                heapq.heappush(pq, (new_time, neighbor))
                
    duration_ms = (time.perf_counter() - t_start) * 1000.0
    
    # Path reconstruction
    path = []
    if closest_poi_node:
        curr = closest_poi_node
        while curr is not None:
            path.append(curr)
            curr = parents[curr]
        path.reverse()
        
    # Simulate A* comparison (must run A* N times to find nearest POI)
    total_astar_explored = 0
    for p_node in poi_nodes_set:
        _, a_explored, _ = run_astar(graph_time, coords, start_node, p_node, 'great_circle')
        total_astar_explored += len(a_explored)
        
    path_geom = get_path_geometry_coords(path, G) if path else None
    
    return jsonify({
        'path': path_geom,
        'explored': [[coords[n][0], coords[n][1]] for n in explored_order if n in coords],
        'closest_poi_index': poi_node_to_index.get(closest_poi_node) if closest_poi_node else None,
        'travel_time_mins': round(distances[closest_poi_node] / 60.0, 2) if closest_poi_node else 0.0,
        'path_length_meters': get_path_length_meters(path, G) if path else 0.0,
        'pois': pois_ll,
        'stats': {
            'dijkstra_explored': len(explored_order),
            'astar_explored_total': total_astar_explored,
            'dijkstra_runs': 1,
            'astar_runs': len(poi_nodes_set),
            'duration_ms': duration_ms
        },
        'meta': {
            'start_coords': [G.nodes[start_node]['y'], G.nodes[start_node]['x']],
            'closest_poi_coords': [coords[closest_poi_node][0], coords[closest_poi_node][1]] if closest_poi_node else None
        }
    })


@app.route('/api/scenarios/eco_routing', methods=['POST'])
def api_scenarios_eco_routing():
    """
    Computes energy-optimal routing (Wh) comparing Dijkstra (correct) with A* (inadmissible heuristic).
    Friction cost: 0.15 Wh/m.
    Gravity cost: Uphill +4.09 Wh/m-elevation, Downhill -2.45 Wh/m-elevation (regeneration).
    Weights clamped to minimum 1.0 Wh.
    """
    data = request.get_json() or {}
    start_ll = data.get('start')
    end_ll = data.get('end')
    
    if not start_ll or not end_ll:
        return jsonify({"error": "Départ et arrivée requis."}), 400
        
    start_node = str(ox.nearest_nodes(G_raw, start_ll[1], start_ll[0]))
    end_node = str(ox.nearest_nodes(G_raw, end_ll[1], end_ll[0]))
    
    # Build energy-weighted graph and store node elevations
    graph_energy = {}
    coords = {}
    elevations = {}
    
    for n, n_data in G.nodes(data=True):
        lat, lon = n_data['y'], n_data['x']
        coords[n] = (lat, lon)
        elevations[n] = get_node_elevation(lat, lon)
        graph_energy[n] = {}
        
    for u, v, e_data in G.edges(data=True):
        length = e_data.get('length', 1.0)
        lat_u, lon_u = coords[u]
        lat_v, lon_v = coords[v]
        
        h_u = elevations[u]
        h_v = elevations[v]
        dh = h_v - h_u
        
        # Friction energy (Wh)
        E_friction = 0.15 * length
        
        # Gravity energy (Wh)
        if dh > 0:
            E_gravity = 4.09 * dh
        else:
            E_gravity = 2.45 * dh  # negative (regeneration)
            
        # Clamp weight to a positive minimum to avoid negative weights/cycles
        weight = max(1.0, E_friction + E_gravity)
        
        if v in graph_energy[u]:
            graph_energy[u][v] = min(graph_energy[u][v], weight)
        else:
            graph_energy[u][v] = weight
            
    # Helper path profiling function
    def get_path_profile(path_nodes):
        profile = []
        if not path_nodes:
            return profile
        
        curr_dist = 0.0
        profile.append({
            'elevation': round(elevations[path_nodes[0]], 1),
            'distance': 0.0
        })
        
        for i in range(len(path_nodes) - 1):
            u, v = path_nodes[i], path_nodes[i+1]
            edge_data = G.get_edge_data(u, v)
            length = 0.0
            if edge_data:
                key = list(edge_data.keys())[0]
                length = edge_data[key].get('length', 0.0)
            curr_dist += length
            profile.append({
                'elevation': round(elevations[v], 1),
                'distance': round(curr_dist, 1)
            })
        return profile

    # A* Energy search using standard Haversine distance heuristic (0.15 Wh/m)
    def run_astar_energy(start, target):
        t_start = time.perf_counter()
        target_coord = coords[target]
        
        def heuristic(node):
            # Estimate flat energy cost (friction only, 0.15 Wh/m)
            dist = haversine_distance(coords[node], target_coord)
            return dist * 0.15
                
        start_h = heuristic(start)
        pq = [(start_h, 0.0, start)]
        g_scores = {start: 0.0}
        parents = {start: None}
        visited = set()
        explored_order = []
        
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
            
            for neighbor, weight in graph_energy.get(current, {}).items():
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

    # Run searches
    d_path, d_explored, d_time = run_dijkstra(graph_energy, start_node, end_node)
    a_path, a_explored, a_time = run_astar_energy(start_node, end_node)
    
    d_geom = get_path_geometry_coords(d_path, G) if d_path else None
    a_geom = get_path_geometry_coords(a_path, G) if a_path else None
    
    return jsonify({
        'dijkstra': {
            'path': d_geom,
            'explored': [[coords[n][0], coords[n][1]] for n in d_explored if n in coords],
            'energy_wh': round(get_path_travel_time(d_path, graph_energy), 1) if d_path else 0.0,
            'length_m': round(get_path_length_meters(d_path, G), 1) if d_path else 0.0,
            'explored_count': len(d_explored),
            'duration_ms': d_time,
            'profile': get_path_profile(d_path)
        },
        'astar': {
            'path': a_geom,
            'explored': [[coords[n][0], coords[n][1]] for n in a_explored if n in coords],
            'energy_wh': round(get_path_travel_time(a_path, graph_energy), 1) if a_path else 0.0,
            'length_m': round(get_path_length_meters(a_path, G), 1) if a_path else 0.0,
            'explored_count': len(a_explored),
            'duration_ms': a_time,
            'profile': get_path_profile(a_path)
        },
        'meta': {
            'start_coords': [G.nodes[start_node]['y'], G.nodes[start_node]['x']],
            'end_coords': [G.nodes[end_node]['y'], G.nodes[end_node]['x']]
        }
    })
 
 
@app.route('/api/scenarios/dfs_connectivity', methods=['POST'])
def api_scenarios_dfs_connectivity():
    """
    Compares Dijkstra, A* and DFS for simple reachability (connectivity) checking.
    Demonstrates that DFS is extremely lightweight and fast to find ANY path from A to B.
    """
    data = request.get_json() or {}
    start_ll = data.get('start')
    end_ll = data.get('end')
    
    if not start_ll or not end_ll:
        return jsonify({"error": "Départ et arrivée requis."}), 400
        
    start_node = str(ox.nearest_nodes(G_raw, start_ll[1], start_ll[0]))
    end_node = str(ox.nearest_nodes(G_raw, end_ll[1], end_ll[0]))
    
    # Build standard travel time graph
    graph_time = {}
    coords = {}
    for n, n_data in G.nodes(data=True):
        coords[n] = (n_data['y'], n_data['x'])
        graph_time[n] = {}
        
    for u, v, e_data in G.edges(data=True):
        length = e_data.get('length', 1.0)
        speed_kph = 50.0
        if 'maxspeed' in e_data:
            try:
                ms = e_data['maxspeed']
                if isinstance(ms, list):
                    ms = ms[0]
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
        
        if v in graph_time[u]:
            graph_time[u][v] = min(graph_time[u][v], t_base)
        else:
            graph_time[u][v] = t_base

    # Run searches
    d_path, d_explored, d_time = run_dijkstra(graph_time, start_node, end_node)
    a_path, a_explored, a_time = run_astar(graph_time, coords, start_node, end_node, 'great_circle')
    dfs_path, dfs_explored, dfs_time = run_dfs(graph_time, start_node, end_node)
    
    d_geom = get_path_geometry_coords(d_path, G) if d_path else None
    a_geom = get_path_geometry_coords(a_path, G) if a_path else None
    dfs_geom = get_path_geometry_coords(dfs_path, G) if dfs_path else None
    
    return jsonify({
        'dijkstra': {
            'path': d_geom,
            'explored': [[coords[n][0], coords[n][1]] for n in d_explored if n in coords],
            'length_m': round(get_path_length_meters(d_path, G), 1) if d_path else 0.0,
            'explored_count': len(d_explored),
            'duration_ms': d_time
        },
        'astar': {
            'path': a_geom,
            'explored': [[coords[n][0], coords[n][1]] for n in a_explored if n in coords],
            'length_m': round(get_path_length_meters(a_path, G), 1) if a_path else 0.0,
            'explored_count': len(a_explored),
            'duration_ms': a_time
        },
        'dfs': {
            'path': dfs_geom,
            'explored': [[coords[n][0], coords[n][1]] for n in dfs_explored if n in coords],
            'length_m': round(get_path_length_meters(dfs_path, G), 1) if dfs_path else 0.0,
            'explored_count': len(dfs_explored),
            'duration_ms': dfs_time
        },
        'meta': {
            'start_coords': [G.nodes[start_node]['y'], G.nodes[start_node]['x']],
            'end_coords': [G.nodes[end_node]['y'], G.nodes[end_node]['x']]
        }
    })



if __name__ == '__main__':
    # Start the server on port 5000
    app.run(debug=True, port=5000)
