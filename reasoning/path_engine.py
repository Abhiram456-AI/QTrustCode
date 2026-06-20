"""Path reasoning utilities for repository graphs.
This module provides reusable path-finding operations on the repository's
NetworkX graphs. These utilities will later support impact analysis,
reliability scoring, multi-agent reasoning, and quantum optimization.
"""

from typing import Dict, List, Optional, Set

import networkx as nx


class PathEngine:
    """Provides path queries over a directed repository graph."""

    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def find_shortest_path(self, source: str, target: str) -> Optional[List[str]]:
        """Return the shortest directed path between two nodes.

        Returns None if either node does not exist or if no path is found.
        """
        if source not in self.graph or target not in self.graph:
            return None

        try:
            return nx.shortest_path(self.graph, source=source, target=target)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def find_all_paths(
        self,
        source: str,
        target: str,
        cutoff: Optional[int] = None,
    ) -> List[List[str]]:
        """Return all simple paths between source and target.

        An empty list is returned when nodes do not exist or no path is found.
        The optional cutoff limits maximum path length.
        """
        if source not in self.graph or target not in self.graph:
            return []

        try:
            return list(
                nx.all_simple_paths(
                    self.graph,
                    source=source,
                    target=target,
                    cutoff=cutoff,
                )
            )
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

    def path_exists(self, source: str, target: str) -> bool:
        """Return True if a directed path exists."""
        return self.find_shortest_path(source, target) is not None

    def get_descendants(self, node: str) -> List[str]:
        """Return all nodes reachable from the given node."""
        if node not in self.graph:
            return []

        return sorted(nx.descendants(self.graph, node))

    def get_ancestors(self, node: str) -> List[str]:
        """Return all nodes that can reach the given node."""
        if node not in self.graph:
            return []

        return sorted(nx.ancestors(self.graph, node))

    def impact_analysis(self, node: str) -> Dict[str, object]:
        """Summarize the impact of changing a node."""
        descendants = self.get_descendants(node)
        ancestors = self.get_ancestors(node)

        return {
            "node": node,
            "upstream_dependencies": ancestors,
            "downstream_dependents": descendants,
            "fan_in": len(ancestors),
            "fan_out": len(descendants),
        }

    def get_subgraph_between(self, source: str, target: str) -> Set[str]:
        """Return all nodes participating in any path between source and target."""
        paths = self.find_all_paths(source, target)

        nodes: Set[str] = set()
        for path in paths:
            nodes.update(path)

        return nodes

    def explain_path(self, source: str, target: str) -> dict:
        """Return a structured path explanation for query responses."""
        path = self.find_shortest_path(source, target)
        all_paths = self.find_all_paths(source, target, cutoff=10)

        return {
            "source": source,
            "target": target,
            "path_exists": path is not None,
            "shortest_path": path or [],
            "shortest_length": max(len(path or []) - 1, 0),
            "path_count": len(all_paths),
            "all_paths": all_paths,
            "subgraph_nodes": sorted(self.get_subgraph_between(source, target)),
        }
