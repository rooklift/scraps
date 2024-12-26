import heapq, random


def main():
	graph = parser("dijkstra_costs.txt")

	for i in range(100):
		from_int = random.randint(0, 19)
		to_int = random.randint(0, 19)

		path1, dist1 = dijkstra(graph, str(from_int), str(to_int))
		path2, dist2 = dijkstra_c(graph, str(from_int), str(to_int))

		print(f"{'-'.join(path1)}: {dist1}")
		print(f"{'-'.join(path2)}: {dist2}")

		if path1 != path2:
			print("Paths differed.")				# Maybe possible if multiple valid routes?
		if dist1 != dist2:
			print("-- DISTANCES DIFFERED! ---")		# Should be impossible.


# File format is  FROM_NODE   TO_NODE   COST
#                 (string)    (string)  (int)


def parser(filename):
	with open(filename) as infile:
		lines = [line.strip() for line in infile.readlines() if line.strip() != ""]
	graph = []
	for line in lines:
		tokens = line.split()
		graph.append((tokens[0], tokens[1], int(tokens[2])))
	return graph


"""----------------------------------------------------------------------------------------------------------------------------------------
 According to Claude:
	1. Start with your starting city. Mark its "distance from start" as 0, and all other cities as "infinity" distance.
	2. Keep a list of "cities to consider" and "cities we're done with". Initially, only your starting city is "to consider".
	3. Among all cities you're currently considering, look at the one with shortest "distance from start". Call this the "current city":
		3.1. If this "current city" is in the "done" list, skip it (go back to step 3).
	4. Look at all roads leading out from the current city. For each one:
		4.1. Calculate total distance if you went through current city to reach that neighbor
		4.2. If this total is less than that neighbor's currently recorded distance:
			4.3. Update the neighbor's recorded distance
			4.4. Add the neighbor to "cities to consider" (even if it's been considered before)
	5. Mark current city as "done" - we've found the shortest possible path to it
	6. Repeat steps 3-5 until you reach your destination city
Additional:
	To return the actual path [not done below], we would need to keep track of how we reached each node during the algorithm.
	The common approach is to maintain a "came_from" dictionary that records the predecessor of each node on its shortest path.
----------------------------------------------------------------------------------------------------------------------------------------"""

def dijkstra(graph, start, end):		# THIS VERSION ACTUALLY WRITTEN BY ME BASED ON CLAUDE'S PSEUDOCODE.

	# graph is our list of tuples in format (from, to, cost) where from and to are just node name strings.
	# start and end are strings naming the start and end nodes.

	# Preprocessing:

	connections = dict()				# name --> target --> cost

	for (from_name, to_name, cost) in graph:
		if from_name not in connections:
			connections[from_name] = dict()
		connections[from_name][to_name] = cost

	# Step 1:

	distances = dict()					# name --> dist from start

	for item in graph:
		distances[item[0]] = 999999999
		distances[item[1]] = 999999999

	distances[start] = 0

	# Additional:

	previous = dict()					# Name --> previous node name
	previous[start] = None

	# Step 2:

	consider_pq = [(0, start)]			# Note: to maintain the heap, the implied sort ordering of the items
										# needs to be correct, hence why we include the distance.
	done = set()

	while True:

		# Step 3:

		try:
			dist_to_current, current = heapq.heappop(consider_pq)
		except IndexError:
			return ((), -1)				# No path found.

		if current in done:														# Step 3.1
			continue

		# Step 4:

		for neighbour in connections[current]:

			if neighbour in done:		# In discussion with Claude, a bit unclear
				continue				# whether this is necessary or even correct.

			distance = connections[current][neighbour]

			dist_to_neighbour = dist_to_current + distance						# Step 4.1

			if dist_to_neighbour < distances[neighbour]:						# Step 4.2
				distances[neighbour] = dist_to_neighbour						# Step 4.3
				previous[neighbour] = current									# Additional
				heapq.heappush(consider_pq, (dist_to_neighbour, neighbour))		# Step 4.4

		# Step 5:

		done.add(current)

		if end in done:
			path = [end]
			while previous[path[-1]]:
				path.append(previous[path[-1]])
			return tuple(reversed(path)), distances[end]

# -----------------------------------------------------------------------------------------------------------------------------------------

def dijkstra_c(graph, start_name, end_name):		# THIS VERSION WRITTEN BY CLAUDE
	"""
	Find shortest path between start_name and end_name in graph using Dijkstra's algorithm.

	Args:
		graph: List of (from_node, to_node, distance) tuples
		start_name: Starting node name
		end_name: Target node name

	Returns:
		Tuple of (path, distance) where path is a tuple of node names and distance is total path length.
		If no path exists, returns ((), -1)
	"""
	# Build adjacency list
	edges = {}
	for src, dst, dist in graph:
		if src not in edges:
			edges[src] = []
		edges[src].append((dst, dist))

	# If start or end not in graph, return no path
	if start_name not in edges and not any(start_name == dst for _, dst, _ in graph):
		return ((), -1)
	if end_name not in edges and not any(end_name == dst for _, dst, _ in graph):
		return ((), -1)

	# Priority queue for Dijkstra's algorithm
	# Format: (total_distance, current_node, path_so_far)
	queue = [(0, start_name, (start_name,))]

	# Track visited nodes
	visited = set()

	while queue:
		total_dist, current, path = heapq.heappop(queue)

		if current == end_name:
			return path, total_dist

		if current in visited:
			continue

		visited.add(current)

		# Add all neighbors to queue
		if current in edges:  # Check if current node has any outgoing edges
			for next_node, edge_dist in edges[current]:
				if next_node not in visited:
					heapq.heappush(queue, (
						total_dist + edge_dist,
						next_node,
						path + (next_node,)
					))

	# No path found
	return ((), -1)

# -----------------------------------------------------------------------------------------------------------------------------------------

main()
