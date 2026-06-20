"""
Impact Engine
-------------
Performs change-impact analysis on the repository dependency graph.

Graph convention:
A ---> B means A depends on/imports B.

Therefore, if B changes, A is impacted.
"""

from collections import deque
from typing import Dict, List, Set


class ImpactEngine:
    def __init__(self, dependency_graph):
        """
        Parameters
        ----------
        dependency_graph : networkx.DiGraph
            Directed graph where:
            file_a -> file_b means file_a depends on file_b.
        """
        self.graph = dependency_graph

    def get_impacted_files(self, node: str) -> List[str]:
        """
        Return every file that may be affected if `node` changes.
        Traverses incoming edges recursively.
        """
        if node not in self.graph:
            return []

        impacted: Set[str] = set()
        queue = deque(self.graph.predecessors(node))

        while queue:
            current = queue.popleft()

            if current in impacted:
                continue

            impacted.add(current)

            for parent in self.graph.predecessors(current):
                if parent not in impacted:
                    queue.append(parent)

        return sorted(impacted)

    def get_impact_radius(self, node: str) -> int:
        """Number of files affected by a change."""
        return len(self.get_impacted_files(node))

    def get_change_blast_radius(self, node: str) -> Dict:
        """Return a compact impact summary."""
        impacted = self.get_impacted_files(node)

        return {
            "changed_file": node,
            "impacted_files": impacted,
            "blast_radius": len(impacted),
        }

    def get_criticality(self, node: str) -> float:
        """
        Normalized criticality score in [0, 1].
        Higher score means changing this file affects more of the repository.
        """
        total_nodes = max(len(self.graph.nodes()) - 1, 1)
        radius = self.get_impact_radius(node)
        return round(radius / total_nodes, 3)

    def impact_report(self, node: str) -> Dict:
        """Full report used later by the Risk Engine and LLM context builder."""
        impacted = self.get_impacted_files(node)

        return {
            "changed_file": node,
            "impacted_files": impacted,
            "blast_radius": len(impacted),
            "criticality": self.get_criticality(node),
        }

    # ---------------------------------------------------------
    # Backward-compatible aliases used by QueryEngine/RiskEngine
    # ---------------------------------------------------------

    def impacted_by(self, node: str) -> List[str]:
        """Alias for get_impacted_files()."""
        return self.get_impacted_files(node)

    def impact_of(self, node: str) -> Dict:
        """Alias returning an impact summary."""
        return self.impact_report(node)

    def blast_radius(self, node: str) -> int:
        """Alias for get_impact_radius()."""
        return self.get_impact_radius(node)

    def criticality(self, node: str) -> float:
        """Alias for get_criticality()."""
        return self.get_criticality(node)

    def blast_radius_report(self, node: str) -> Dict:
        """Alias for get_change_blast_radius()."""
        return self.get_change_blast_radius(node)
