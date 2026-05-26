import heapq
import time
from typing import List, Tuple, Set, Dict, Optional

def get_neighbors(node: Tuple[int, int], rows: int, cols: int, obstacles: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    Get valid 4-directional neighbors of a grid node.
    """
    r, c = node
    neighbors = []
    # Up, Down, Left, Right
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            if (nr, nc) not in obstacles:
                neighbors.append((nr, nc))
    return neighbors

def solve_dijkstra(
    rows: int,
    cols: int,
    start: Tuple[int, int],
    end: Tuple[int, int],
    obstacles: Set[Tuple[int, int]]
) -> Tuple[Optional[List[Tuple[int, int]]], List[Tuple[int, int]], float]:
    """
    Finds the shortest path on a 2D grid using Dijkstra's algorithm.
    
    Returns:
        path: List of (r, c) coordinates forming the path from start to end (or None)
        explored: List of (r, c) coordinates in the order they were expanded (for animation)
        duration_ms: Precise execution time in milliseconds
    """
    t_start = time.perf_counter()
    
    pq: List[Tuple[float, Tuple[int, int]]] = [(0.0, start)]
    distances: Dict[Tuple[int, int], float] = {start: 0.0}
    parents: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
    visited: Set[Tuple[int, int]] = set()
    explored_order: List[Tuple[int, int]] = []
    
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
        
        neighbors = get_neighbors(current, rows, cols, obstacles)
        for neighbor in neighbors:
            if neighbor in visited:
                continue
                
            # Grid edge weight is always 1.0
            new_dist = dist + 1.0
            if new_dist < distances.get(neighbor, float('inf')):
                distances[neighbor] = new_dist
                parents[neighbor] = current
                heapq.heappush(pq, (new_dist, neighbor))
                
    # Reconstruct path
    if end in distances:
        path = []
        curr = end
        while curr is not None:
            path.append(curr)
            curr = parents[curr]
        path.reverse()
        
    duration_ms = (time.perf_counter() - t_start) * 1000.0
    return path, explored_order, duration_ms

def solve_astar(
    rows: int,
    cols: int,
    start: Tuple[int, int],
    end: Tuple[int, int],
    obstacles: Set[Tuple[int, int]],
    heuristic_type: str = 'manhattan'
) -> Tuple[Optional[List[Tuple[int, int]]], List[Tuple[int, int]], float]:
    """
    Finds the shortest path on a 2D grid using A* algorithm with configurable distance heuristics.
    
    Heuristics:
        'manhattan': standard L1 distance (admissible and consistent)
        'euclidean': standard L2 distance (admissible, less informed)
        'weighted_manhattan': inadmissible (Manhattan x 3), very fast search but potentially suboptimal path
    
    Returns:
        path: List of (r, c) coordinates forming the path from start to end (or None)
        explored: List of (r, c) coordinates in the order they were expanded (for animation)
        duration_ms: Precise execution time in milliseconds
    """
    t_start = time.perf_counter()
    import math
    
    # Configure heuristic function
    if heuristic_type == 'euclidean':
        def heuristic(node: Tuple[int, int]) -> float:
            return float(math.sqrt((node[0] - end[0])**2 + (node[1] - end[1])**2))
    elif heuristic_type == 'weighted_manhattan':
        def heuristic(node: Tuple[int, int]) -> float:
            return 3.0 * float(abs(node[0] - end[0]) + abs(node[1] - end[1]))
    else:  # Default is 'manhattan'
        def heuristic(node: Tuple[int, int]) -> float:
            return float(abs(node[0] - end[0]) + abs(node[1] - end[1]))
        
    start_h = heuristic(start)
    # PQ stores: (f_score, g_score, current_node)
    pq: List[Tuple[float, float, Tuple[int, int]]] = [(start_h, 0.0, start)]
    g_scores: Dict[Tuple[int, int], float] = {start: 0.0}
    parents: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
    visited: Set[Tuple[int, int]] = set()
    explored_order: List[Tuple[int, int]] = []
    
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
        
        neighbors = get_neighbors(current, rows, cols, obstacles)
        for neighbor in neighbors:
            if neighbor in visited:
                continue
                
            tentative_g = g + 1.0
            if tentative_g < g_scores.get(neighbor, float('inf')):
                g_scores[neighbor] = tentative_g
                parents[neighbor] = current
                f_score = tentative_g + heuristic(neighbor)
                heapq.heappush(pq, (f_score, tentative_g, neighbor))
                
    # Reconstruct path
    if end in g_scores:
        path = []
        curr = end
        while curr is not None:
            path.append(curr)
            curr = parents[curr]
        path.reverse()
        
    duration_ms = (time.perf_counter() - t_start) * 1000.0
    return path, explored_order, duration_ms

def solve_dfs(
    rows: int,
    cols: int,
    start: Tuple[int, int],
    end: Tuple[int, int],
    obstacles: Set[Tuple[int, int]]
) -> Tuple[Optional[List[Tuple[int, int]]], List[Tuple[int, int]], float]:
    """
    Finds a path on a 2D grid using Depth First Search (DFS).
    
    Returns:
        path: List of (r, c) coordinates forming a path from start to end (or None)
        explored: List of (r, c) coordinates in the order they were expanded (for animation)
        duration_ms: Precise execution time in milliseconds
    """
    t_start = time.perf_counter()
    
    # Stack stores current node
    stack: List[Tuple[int, int]] = [start]
    visited: Set[Tuple[int, int]] = set()
    parents: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
    explored_order: List[Tuple[int, int]] = []
    
    path = None
    
    while stack:
        current = stack.pop()
        
        if current == end:
            visited.add(current)
            explored_order.append(current)
            break
            
        if current in visited:
            continue
            
        visited.add(current)
        explored_order.append(current)
        
        neighbors = get_neighbors(current, rows, cols, obstacles)
        for neighbor in neighbors:
            if neighbor not in visited and neighbor not in parents:
                parents[neighbor] = current
                stack.append(neighbor)
                
    # Reconstruct path
    if end in visited:
        path = []
        curr = end
        while curr is not None:
            path.append(curr)
            curr = parents[curr]
        path.reverse()
        
    duration_ms = (time.perf_counter() - t_start) * 1000.0
    return path, explored_order, duration_ms
