# ==============================
# File: inventory_app/services/reports.py
# ==============================
from __future__ import annotations
from typing import Iterable, Dict, Any

from ..domain.interfaces import Reporte


class ReporteTablaTexto(Reporte):
    def render(self, filas: Iterable[Dict[str, Any]]) -> str:
        out = [f"{'SKU':<12} {'Producto':<30} {'Und':<5} {'Cant.':>8} {'Min.':>6} {'Estado':<12}"]
        out.append("-" * 80)
        for r in filas:
            out.append(
                f"{r['sku']:<12} {r['nombre']:<30} {r['unidad']:<5} {r['cantidad']:>8.2f} {r['minimo']:>6.2f} {r['estado']:<12}"
            )
        return "\n".join(out)