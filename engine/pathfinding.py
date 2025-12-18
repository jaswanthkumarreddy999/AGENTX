import heapq
import math

class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position # (x, y)
        self.g = 0 # Cost from start
        self.h = 0 # Heuristic (estimated cost to end)
        self.f = 0 # Total cost

    def __eq__(self, other):
        return self.position == other.position
    
    def __lt__(self, other):
        return self.f < other.f

def a_star_search(tilemap, start, end):
    """
    Returns a list of tuples [(x, y), (x, y)] representing the path.
    """
    # Create start and end node
    start_node = Node(None, tuple(start))
    end_node = Node(None, tuple(end))

    open_list = []
    closed_list = set() # Use set for O(1) lookups

    heapq.heappush(open_list, start_node)

    # Safety break to prevent infinite loops in unreachable areas
    iterations = 0
    max_iterations = 5000 

    while open_list:
        iterations += 1
        if iterations > max_iterations:
            return None # Path too complex or unreachable

        # Get the current node
        current_node = heapq.heappop(open_list)
        closed_list.add(current_node.position)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1] # Return reversed path (start -> end)

        # Generate children (neighbors)
        # (0, -1) = Up, (0, 1) = Down, (-1, 0) = Left, (1, 0) = Right
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: 
            node_position = (current_node.position[0] + new_position[0], 
                             current_node.position[1] + new_position[1])

            # Check bounds
            if (node_position[0] > (tilemap.width - 1) or 
                node_position[0] < 0 or 
                node_position[1] > (tilemap.height - 1) or 
                node_position[1] < 0):
                continue

            # Check walkable (Make sure it's not a wall '#')
            if tilemap.is_wall(node_position[0], node_position[1]):
                continue

            new_node = Node(current_node, node_position)
            children.append(new_node)

        # Loop through children
        for child in children:
            if child.position in closed_list:
                continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            # Heuristic: Manhattan distance
            child.h = abs(child.position[0] - end_node.position[0]) + \
                      abs(child.position[1] - end_node.position[1])
            child.f = child.g + child.h

            # Add to open list
            # Note: In a full A* optimization we check if child is already in open_list 
            # with a lower G, but for this grid size, simply pushing is acceptable.
            heapq.heappush(open_list, child)

    return None