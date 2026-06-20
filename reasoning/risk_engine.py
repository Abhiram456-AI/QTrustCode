from typing import Dict, List


class RiskEngine:
    """
    Computes architectural change risk using repository metrics,
    dependency impact, and coupling information.
    """

    def __init__(self, metrics: Dict, impact_engine=None, coupling_engine=None):
        self.metrics = metrics or {}
        self.impact_engine = impact_engine
        self.coupling_engine = coupling_engine

    def risk_report(self, node: str) -> Dict:
        """
        Backward-compatible alias used by QueryEngine.
        """
        return self.risk_of(node)

    def _get_blast_radius(self, node: str) -> int:
        if not self.impact_engine:
            return 0

        try:
            if hasattr(self.impact_engine, "blast_radius"):
                blast = self.impact_engine.blast_radius(node)
                if isinstance(blast, dict):
                    return int(blast.get("blast_radius", 0))
                return int(blast or 0)

            for method_name in ("impact_of", "show_impacted_by"):
                if hasattr(self.impact_engine, method_name):
                    impact = getattr(self.impact_engine, method_name)(node)
                    if isinstance(impact, dict):
                        impacted = (
                            impact.get("upstream_dependencies")
                            or impact.get("impacted_files")
                            or []
                        )
                        return len(impacted)
        except Exception:
            return 0

        return 0

    def risk_of(self, node: str) -> Dict:
        data = self.metrics.get(node, {})

        fan_in = data.get("fan_in", 0)
        fan_out = data.get("fan_out", 0)
        centrality = data.get("centrality", 0.0)
        pagerank = data.get("pagerank", 0.0)

        blast_radius = self._get_blast_radius(node)

        instability = 0.0
        if self.coupling_engine:
            if hasattr(self.coupling_engine, "coupling_of"):
                coupling = self.coupling_engine.coupling_of(node)
            elif hasattr(self.coupling_engine, "coupling_report"):
                coupling = self.coupling_engine.coupling_report(node)
            else:
                coupling = {}

            if isinstance(coupling, dict):
                instability = coupling.get("instability", 0.0)

        score = (
            (fan_in * 0.15)
            + (fan_out * 0.10)
            + (centrality * 0.30)
            + (pagerank * 0.20)
            + (blast_radius * 0.10)
            + (instability * 0.15)
        )

        score = round(min(score, 1.0), 3)

        reasons: List[str] = []
        if fan_in >= 3:
            reasons.append(f"high fan-in ({fan_in})")
        if fan_out >= 3:
            reasons.append(f"high fan-out ({fan_out})")
        if blast_radius >= 3:
            reasons.append(f"large blast radius ({blast_radius})")
        if centrality >= 0.5:
            reasons.append(f"high centrality ({centrality})")
        if instability >= 0.6:
            reasons.append(f"high instability ({instability})")

        if score >= 0.75:
            level = "HIGH"
        elif score >= 0.40:
            level = "MEDIUM"
        else:
            level = "LOW"

        return {
            "node": node,
            "risk_score": score,
            "risk_level": level,
            "reasons": reasons,
            "metrics": {
                "fan_in": fan_in,
                "fan_out": fan_out,
                "centrality": centrality,
                "pagerank": pagerank,
                "blast_radius": blast_radius,
                "instability": instability,
            },
        }

    def highest_risk_modules(self, limit: int = 5) -> List[Dict]:
        risks = [self.risk_of(node) for node in self.metrics.keys()]
        risks.sort(key=lambda x: x["risk_score"], reverse=True)
        return risks[:limit]

    def risk_summary(self) -> Dict:
        modules = self.highest_risk_modules(limit=len(self.metrics))

        if modules:
            average = round(
                sum(m["risk_score"] for m in modules) / len(modules),
                3,
            )
        else:
            average = 0.0

        return {
            "total_modules": len(self.metrics),
            "average_risk_score": average,
            "highest_risk_modules": modules[:5],
        }

    def repository_summary(self) -> Dict:
        """
        Backward-compatible alias expected by QueryEngine.
        """
        return self.risk_summary()

    def risky_modules(self, limit: int = 5) -> List[Dict]:
        """
        Backward-compatible alias expected by QueryEngine.
        """
        return self.highest_risk_modules(limit)

    def high_risk_modules(self, limit: int = 5) -> List[Dict]:
        """
        Additional backward-compatible alias for older QueryEngine versions.
        """
        return self.highest_risk_modules(limit)