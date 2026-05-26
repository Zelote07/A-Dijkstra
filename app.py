from flask import Flask, render_template, jsonify, request
from grid_pathfinder import solve_dijkstra, solve_astar, solve_dfs

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/solve', methods=['POST'])
def solve():
    data = request.get_json() or {}
    
    rows = data.get('rows', 20)
    cols = data.get('cols', 20)
    
    start_list = data.get('start')
    end_list = data.get('end')
    obstacles_list = data.get('obstacles', [])
    algorithm = data.get('algorithm', 'both')  # 'dijkstra', 'astar', or 'both'
    
    if not start_list or not end_list:
        return jsonify({"error": "Start and End positions are required."}), 400
        
    start = (start_list[0], start_list[1])
    end = (end_list[0], end_list[1])
    
    # Convert list of obstacles to set of tuples for O(1) lookups
    obstacles = {tuple(obs) for obs in obstacles_list}
    
    results = {}
    
    # Run Dijkstra if requested
    if algorithm in ('dijkstra', 'both'):
        d_path, d_explored, d_time = solve_dijkstra(rows, cols, start, end, obstacles)
        results['dijkstra'] = {
            'path': d_path,
            'explored': d_explored,
            'duration_ms': d_time,
            'nodes_explored_count': len(d_explored)
        }
        
    # Run A* if requested
    if algorithm in ('astar', 'both'):
        heuristic_type = data.get('heuristic', 'manhattan')
        a_path, a_explored, a_time = solve_astar(rows, cols, start, end, obstacles, heuristic_type)
        results['astar'] = {
            'path': a_path,
            'explored': a_explored,
            'duration_ms': a_time,
            'nodes_explored_count': len(a_explored)
        }
        
    # Always run DFS to keep payload complete
    dfs_path, dfs_explored, dfs_time = solve_dfs(rows, cols, start, end, obstacles)
    results['dfs'] = {
        'path': dfs_path,
        'explored': dfs_explored,
        'duration_ms': dfs_time,
        'nodes_explored_count': len(dfs_explored)
    }
        
    return jsonify(results)

if __name__ == '__main__':
    # Start on port 5000 by default
    app.run(debug=True, port=5000)
