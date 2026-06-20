"""
Coupling Engine
----------------
Computes structural coupling metrics over the repository dependency graph.

Metrics:
- Afferent Coupling (Ca): Number of modules depending on a node.
- Efferent Coupling (Ce): Number of modules a node depends on.
- Instability (I): Ce / (Ca + Ce)
- Central Modules: Ranked by total coupling.
"""

from typing import Dict, List, Any
import networkx as nx


class CouplingEngine:
    def __init__(self, dependency_graph: nx.DiGraph):
        self.graph = dependency_graph

    def afferent_coupling(self, node: str) -> int:
        """Modules that depend on this node."""
        if node not in self.graph:
            return 0
        return self.graph.in_degree(node)

    def efferent_coupling(self, node: str) -> int:
        """Modules this node depends on."""
        if node not in self.graph:
            return 0
        return self.graph.out_degree(node)

    def instability(self, node: str) -> float:
        """Robert Martin's instability metric."""
        ca = self.afferent_coupling(node)
        ce = self.efferent_coupling(node)

        total = ca + ce
        if total == 0:
            return 0.0

        return round(ce / total, 3)

    def coupling_report(self, node: str) -> Dict[str, Any]:
        """Full coupling report for a module."""
        return {
            "node": node,
            "afferent_coupling": self.afferent_coupling(node),
            "efferent_coupling": self.efferent_coupling(node),
            "instability": self.instability(node),
        }

    def central_modules(self, top_k: int = 10) -> List[Dict[str, Any]]:
        """Most structurally important modules."""
        rankings = []

        for node in self.graph.nodes():
            ca = self.afferent_coupling(node)
            ce = self.efferent_coupling(node)
            total = ca + ce

            rankings.append(
                {
                    "node": node,
                    "afferent_coupling": ca,
                    "efferent_coupling": ce,
                    "total_coupling": total,
                    "instability": self.instability(node),
                }
            )

        rankings.sort(
            key=lambda x: (x["total_coupling"], x["afferent_coupling"]),
            reverse=True,
        )

        return rankings[:top_k]

    def repository_summary(self) -> Dict[str, Any]:
        """Repository-level coupling summary."""
        modules = list(self.graph.nodes())

        if not modules:
            return {
                "total_modules": 0,
                "average_afferent": 0,
                "average_efferent": 0,
                "most_coupled_modules": [],
            }

        avg_ca = round(
            sum(self.afferent_coupling(n) for n in modules) / len(modules),
            3,
        )
        avg_ce = round(
            sum(self.efferent_coupling(n) for n in modules) / len(modules),
            3,
        )

        return {
            "total_modules": len(modules),
            "average_afferent": avg_ca,
            "average_efferent": avg_ce,
            "most_coupled_modules": self.central_modules(5),
        }
