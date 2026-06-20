

"""
Execution Engine
----------------
Provides execution-path reasoning over the repository's function call graph.

Responsibilities:
- Trace execution starting from a function
- Return direct callers and callees
- Find reachable functions transitively
- Produce execution summaries for QueryEngine
"""

import networkx as nx


class ExecutionEngine:
    def __init__(self, function_graph):
        self.graph = function_graph

    def callers_of(self, function_name):
        if function_name not in self.graph:
            return []
        return sorted(list(self.graph.predecessors(function_name)))

    def callees_of(self, function_name):
        if function_name not in self.graph:
            return []
        return sorted(list(self.graph.successors(function_name)))

    def execution_trace(self, function_name):
        if function_name not in self.graph:
            return {
                "error": f"Function '{function_name}' not found"
            }

        descendants = sorted(nx.descendants(self.graph, function_name))

        return {
            "entry_function": function_name,
            "direct_callees": self.callees_of(function_name),
            "reachable_functions": descendants,
            "reachable_count": len(descendants)
        }

    def execution_path(self, source, target):
        if source not in self.graph:
            return {"error": f"Function '{source}' not found"}

        if target not in self.graph:
            return {"error": f"Function '{target}' not found"}

        try:
            path = nx.shortest_path(self.graph, source, target)
            return {
                "source": source,
                "target": target,
                "path": path,
                "length": len(path) - 1
            }
        except nx.NetworkXNoPath:
            return {
                "source": source,
                "target": target,
                "path": [],
                "length": -1,
                "message": "No execution path found"
            }

    def entry_points(self):
        return sorted([
            node
            for node in self.graph.nodes
            if self.graph.in_degree(node) == 0
        ])