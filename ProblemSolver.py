import math
class Queue:
    def __init__(self, passed_list=[]):
        self._passed_list = passed_list

    def __len__(self):
        return len(self._passed_list)

    def enqueue(self, passed_element):
        self._passed_list.append(passed_element)

    def dequeue(self):
        return self._passed_list.pop(0)

    def is_empty(self):
        return len(self) == 0

class FCDGNode:
    def __init__(self, farmer, cat, duck, grain):
        self.farmer = farmer
        self.cat = cat
        self.duck = duck
        self.grain = grain

    def _node_key(self):
        return self.farmer, self.cat, self.duck, self.grain

    def __hash__(self):
        return hash(self._node_key())

    def __repr__(self):
        return str(self._node_key())

    def __str__(self):
        return str(self._node_key())

    def __eq__(self, other):
        if isinstance(other, FCDGNode):
            return self._node_key() == other._node_key()
        else:
            return NotImplemented

class WaterNode:
    def __init__(self, bucket1, bucket2, tub):
        self.bucket1 = bucket1
        self.bucket2 = bucket2
        self.tub = tub
        self.total = bucket1 + bucket2 + tub

    def _item_key(self):
        return self.bucket1, self.bucket2, self.tub

    def __repr__(self):
        return str(self._item_key())

    def __str__(self):
        return str(self._item_key())

    def __hash__(self):
        return hash(self._item_key())

    def __eq__(self, other):
        if isinstance(other, WaterNode):
            return self._item_key() == other._item_key()
        else:
            return NotImplemented

class MLPNode:
    def __init__(self, location, x_coordinate, y_coordinate):
        self.location = location
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate

    def _item_key(self):
        return self.location, self.x_coordinate, self.y_coordinate

    def __repr__(self):
        return self.location

    def __str__(self):
        return self.location

    def __hash__(self):
        return hash(self._item_key())

    def __eq__(self, other):
        if isinstance(other, MLPNode):
            return (self.x_coordinate, self.y_coordinate) == (other.x_coordinate, other.y_coordinate)
        else:
            return NotImplemented

class FCDGSolver:
    def __init__(self):
        self.start_state = FCDGNode(0, 0, 0, 0)
        self.goal_state = FCDGNode(1, 1, 1, 1)

    @staticmethod
    def _check_validity(curr_node):
        # If the cat could eat the duck, return False.
        if curr_node.cat == curr_node.duck and curr_node.farmer != curr_node.cat:
            return False
        # If the duck could eat the grain, return False.
        elif curr_node.duck == curr_node.grain and curr_node.farmer != curr_node.duck:
            return False
        else:
            return True

    def _expand_node(self, curr_node):
        node_list = []
        farmer = curr_node.farmer
        cat = curr_node.cat
        duck = curr_node.duck
        grain = curr_node.grain

        # If valid, move farmer.
        if self._check_validity(FCDGNode(1-farmer, cat, duck, grain)):
            node_list.append(FCDGNode(1-farmer, cat, duck, grain))

        # If valid, transport cat.
        if cat == farmer and self._check_validity(FCDGNode(1-farmer, 1-cat, duck, grain)):
            node_list.append(FCDGNode(1-farmer, 1-cat, duck, grain))

        # If valid, transport duck.
        if duck == farmer and self._check_validity(FCDGNode(1-farmer, cat, 1-duck, grain)):
            node_list.append(FCDGNode(1-farmer, cat, 1-duck, grain))

        # If valid, transport grain.
        if grain == farmer and self._check_validity(FCDGNode(1-farmer, cat, duck, 1-grain)):
            node_list.append(FCDGNode(1-farmer, cat, duck, 1-grain))

        # Return the list of valid tuples.
        return node_list

    @staticmethod
    def _fcdg_heuristic(other_side):
        max_utility = None
        ideal_match = None

        for duo in other_side:
            total = duo[1].farmer + duo[1].cat + duo[1].duck + duo[1].grain
            if max_utility is None or total > max_utility:
                max_utility = total
                ideal_match = duo

        return ideal_match

    def dfs_solver(self):
        marked = {}
        remaining_nodes = [(None, self.start_state)]

        while remaining_nodes:
            prev_node, curr_node = remaining_nodes.pop()
            if curr_node not in marked:
                marked[curr_node] = prev_node
                if self.goal_state == curr_node:
                    return marked
                for node in self._expand_node(curr_node):
                    remaining_nodes.append((curr_node, node))

        return marked

    def bfs_solver(self):
        marked = {}
        remaining_nodes = Queue([(None, self.start_state)])

        while remaining_nodes:
            prev_node, curr_node = remaining_nodes.dequeue()
            if curr_node not in marked:
                marked[curr_node] = prev_node
                if self.goal_state == curr_node:
                    return marked
                for node in self._expand_node(curr_node):
                    remaining_nodes.enqueue((curr_node, node))

        return marked

    def a_star_solver(self):
        marked = {}
        remaining_nodes = [(None, self.start_state)]

        while remaining_nodes:
            prev_node, curr_node = self._fcdg_heuristic(remaining_nodes)
            remaining_nodes.remove(self._fcdg_heuristic(remaining_nodes))
            if curr_node not in marked:
                marked[curr_node] = prev_node
                if self.goal_state == curr_node:
                    return marked
                for node in self._expand_node(curr_node):
                    remaining_nodes.append((curr_node, node))

        return marked

    def find_answer(self, marked):
        curr_node = self.goal_state
        answer = []

        if self.goal_state not in marked:
            return "Answer not found."
        else:
            while curr_node is not None:
                answer.append(curr_node)
                curr_node = marked[curr_node]

        answer.reverse()
        return answer

class WPSolver:
    def __init__(self, b1_cap, b2_cap, tub_cap, h2o_goal):
        self.b1_cap = b1_cap
        self.b2_cap = b2_cap
        self.tub_cap = tub_cap
        self.h2o_goal = h2o_goal
        self.h2o_goal_node = WaterNode(0, 0, h2o_goal)

    def _expand_node(self, passed_node):
        node_list = []

        # If bucket1 is less than its total capacity, fill it up.
        if passed_node.bucket1 < self.b1_cap:
            node_list.append(WaterNode(self.b1_cap, passed_node.bucket2, passed_node.tub))
            # If bucket2 still has water, pour it into bucket1.
            if passed_node.bucket2 is not 0:
                node_list.append(WaterNode(min(passed_node.bucket1 + passed_node.bucket2, self.b1_cap), 0,
                                           passed_node.tub))
        # If bucket2 is less than its total capacity, fill it up.
        if passed_node.bucket2 < self.b2_cap:
            node_list.append(WaterNode(self.b2_cap, passed_node.bucket2, passed_node.tub))
            # If bucket1 still has water, pour it into bucket2.
            if passed_node.bucket1 is not 0:
                node_list.append(WaterNode(0, min(passed_node.bucket2 + passed_node.bucket1, self.b2_cap),
                                           passed_node.tub))
        # If bucket1 can be used to fill up the tub, do so.
        if passed_node.tub + passed_node.bucket1 <= self.h2o_goal and passed_node.bucket1 is not 0:
            node_list.append(WaterNode(0, passed_node.bucket2, passed_node.tub + passed_node.bucket1))
        # If bucket2 can be used to fill up the tub, do so.
        if passed_node.tub + passed_node.bucket2 <= self.h2o_goal and passed_node.bucket2 is not 0:
            node_list.append(WaterNode(passed_node.bucket1, 0, passed_node.tub + passed_node.bucket2))
        # If there's still water in bucket1, dump it out.
        if passed_node.bucket1 is not 0:
            node_list.append(WaterNode(0, passed_node.bucket2, passed_node.tub))
        # If there's still water in bucket2, dump it out.
        if passed_node.bucket2 is not 0:
            node_list.append(WaterNode(passed_node.bucket1, 0, passed_node.tub))

        return node_list

    def _wp_heuristic(self, node_list):
        max_utility = 0
        ideal_node = node_list[0]

        # Observe tub's current level and decided accordingly.
        for curr_node in node_list:
            if curr_node[1].tub > max_utility:
                ideal_node = curr_node
                max_utility = curr_node[1].tub

        # Determine proximity to goal state and decide accordingly.
        for curr_node in node_list:
            if curr_node[1].tub + curr_node[1].bucket1 == self.h2o_goal:
                ideal_node = curr_node
            if curr_node[1].tub + curr_node[1].bucket2 == self.h2o_goal:
                ideal_node = curr_node

        return ideal_node

    def dfs_solver(self):
        marked = {}
        remaining_nodes = [(None, WaterNode(0, 0, 0))]

        while remaining_nodes:
            prev_node, curr_node = remaining_nodes.pop()
            if curr_node not in marked:
                marked[curr_node] = prev_node
                for node in self._expand_node(curr_node):
                    remaining_nodes.append((curr_node, node))

        return marked

    def bfs_solver(self):
        marked = {}
        remaining_nodes = Queue([(None, WaterNode(0, 0, 0))])

        while remaining_nodes:
            prev_node, curr_node = remaining_nodes.dequeue()
            if curr_node not in marked:
                marked[curr_node] = prev_node
                for node in self._expand_node(curr_node):
                    remaining_nodes.enqueue((curr_node, node))

        return marked

    def a_star_solver(self):
        marked = {}
        remaining_nodes = [(None, WaterNode(0, 0, 0))]

        while remaining_nodes:
            prev_node, curr_node = self._wp_heuristic(remaining_nodes)
            remaining_nodes.remove(self._wp_heuristic(remaining_nodes))
            if curr_node not in marked:
                marked[curr_node] = prev_node
                for node in self._expand_node(curr_node):
                    remaining_nodes.append((curr_node, node))

        return marked

    def find_answer(self, marked):
        curr_node = self.h2o_goal_node
        answer = []

        if self.h2o_goal_node not in marked:
            return "Answer not found."
        else:
            while curr_node is not None:
                answer.append(curr_node)
                curr_node = marked[curr_node]

        answer.reverse()
        return answer

class MLPSolver:
    def __init__(self, num_nodes, num_edges, start_node, goal_node):
        self.num_nodes = num_nodes
        self.num_edges = num_edges
        self.start_node = start_node
        self.goal_node = goal_node

    @staticmethod
    def _node_distance(node_1, node_2):
        x_1, y_1 = node_1.x_coordinate, node_1.y_coordinate
        x_2, y_2 = node_2.x_coordinate, node_2.y_coordinate
        return math.sqrt((x_2 - x_1)**2 + (y_2 - y_1)**2)

    def _expand_node(self, node_path):
        path_list = []

        for edge in self.num_edges:
            # If these nodes connect from the one side, add them to path_list.
            if edge[0] == node_path[-1] and edge[1] not in node_path:
                path_list.append(node_path + [edge[1]])
            # Else if these nodes connect from the other side, add them to path_list.
            elif edge[1] == node_path[-1] and edge[0] not in node_path:
                path_list.append(node_path + [edge[0]])

        return path_list

    def _calc_path(self, potential_path):
        path_cost = 0
        if len(potential_path) <= 1:
            return 0

        for item1, item2 in zip(potential_path[:-1], potential_path[1:]):
            path_cost += self._node_distance(item1, item2)

        return path_cost

    def _mlp_heuristic(self, path_list):
        min_cost = None
        ideal_path = None

        for potential_path in path_list:
            if min_cost is None or self._calc_path(potential_path) < min_cost:
                min_cost = self._calc_path(potential_path)
                ideal_path = potential_path

        return ideal_path

    def dfs_solver(self):
        path_list = []
        remaining_nodes = [[self.start_node]]

        while remaining_nodes:
            curr_node = remaining_nodes.pop()
            if curr_node[-1] == self.goal_node:
                path_list.append(curr_node)
            else:
                for next_node in self._expand_node(curr_node):
                    remaining_nodes.append(next_node)

        return path_list

    def bfs_solver(self):
        path_list = []
        remaining_nodes = Queue([[self.start_node]])

        while remaining_nodes:
            curr_node = remaining_nodes.dequeue()
            if curr_node[-1] == self.goal_node:
                path_list.append(curr_node)
            else:
                for next_node in self._expand_node(curr_node):
                    remaining_nodes.enqueue(next_node)

        return path_list

    def a_star_solver(self):
        remaining_nodes = [[self.start_node]]

        while remaining_nodes:
            curr_node = self._mlp_heuristic(remaining_nodes)
            remaining_nodes.remove(curr_node)
            if curr_node[-1] == self.goal_node:
                return [curr_node, self._calc_path(curr_node)]
            else:
                for next_node in self._expand_node(curr_node):
                    remaining_nodes.append(next_node)

        return "No solution could be found this time around."

    def shot_in_the_dark(self, path_list):
        min_cost = None
        ideal_path = None

        for curr_path in path_list:
            curr_cost = self._calc_path(curr_path)
            if min_cost is None or curr_cost < min_cost:
                min_cost = curr_cost
                ideal_path = curr_path

        return [ideal_path, min_cost]

while True:
    choice = input("Choose the problem number to solve:\n1.FCDG\n2.WP\n3.MLP\n4.Quit\n->")
    if choice == "1":
        print("Problem: Farmer-Cat-Duck-Grain")
        prob = FCDGSolver()
        while True:
            pick = input("Pick the number of the algorithm to use:\n1.DFS\n2.BFS\n3.A*\n4.Return\n-->")
            if pick == "1":
                print(prob.find_answer(prob.dfs_solver()))
            elif pick == "2":
                print(prob.find_answer(prob.bfs_solver()))
            elif pick == "3":
                print(prob.find_answer(prob.a_star_solver()))
            elif pick == "4":
                break
            else:
                print("Invalid choice. Please put the number of the algorithm you would like to use.")

    elif choice == "2":
        print("Problem: Water Buckets")
        b1 = int(input("Enter the capacity for bucket 1: "))
        b2 = int(input("Enter the capacity for bucket 2: "))
        tub = int(input("Enter the capacity for the tub: "))
        goal = int(input("Enter the water goal: "))
        prob = WPSolver(b1, b2, tub, goal)
        while True:
            pick = input("Pick the number of the algorithm to use:\n1.DFS\n2.BFS\n3.A*\n4.Return\n-->")
            if pick == "1":
                print(prob.find_answer(prob.dfs_solver()))
            elif pick == "2":
                print(prob.find_answer(prob.bfs_solver()))
            elif pick == "3":
                print(prob.find_answer(prob.a_star_solver()))
            elif pick == "4":
                break
            else:
                print("Invalid choice. Please put the number of the algorithm you would like to use.")

    elif choice == "3":
        print("Problem: Minimum-Length Path")
        N = MLPNode('N', 0.2, 1)
        P = MLPNode('P', 1.35, 4.25)
        U = MLPNode('U', 2.15, 0.875)
        E = MLPNode('E', 3.42, 2.125)
        J = MLPNode('J', 3.8, 4.575)
        M = MLPNode('M', 6.7, 3.875)
        S = MLPNode('S', 6.7, 1.875)
        V = MLPNode('V', 5.6, 0.1)
        nodes = [N, P, U, E, J, M, S, V]
        edges = [(N, P), (P, U), (N, U), (P, E), (U, E), (P, J), (E, J), (J, M), (E, V), (M, V), (M, S)]
        f = str(input("Pick the first location ([N, P, U, E, J, M, S, V]):")).capitalize()
        s = str(input("Pick the second location ([N, P, U, E, J, M, S, V]):")).capitalize()
        prob = MLPSolver(nodes, edges, f, s)
        while True:
            pick = input("Pick the number of the algorithm to use:\n1.DFS\n2.BFS\n3.A*\n4.Return\n-->")
            if pick == "1":
                print(prob.shot_in_the_dark(prob.dfs_solver()))
            elif pick == "2":
                print(prob.shot_in_the_dark(prob.bfs_solver()))
            elif pick == "3":
                print(prob.a_star_solver())
            elif pick == "4":
                break
            else:
                print("Invalid choice. Please put the number of the algorithm you would like to use.")

    elif choice == "4":
        print("Thanks for playing.")
        break
    else:
        print("Invalid choice. Please put the number of the problem you would like solved.")
