from __future__ import annotations

from collections.abc import Callable
from typing import Any

from . import drill_down_stair, heat_matrix, layered_architecture, phase_roadmap


Renderer = Callable[[Any, dict[str, Any], dict[str, Any], dict[str, Any]], dict[str, Any]]

RENDERERS: dict[str, Renderer] = {
    "heat_matrix": heat_matrix.render,
    "layered_architecture": layered_architecture.render,
    "drill_down_stair": drill_down_stair.render,
    "phase_roadmap": phase_roadmap.render,
}


def get_renderer(component_type: str) -> Renderer | None:
    return RENDERERS.get(component_type)
