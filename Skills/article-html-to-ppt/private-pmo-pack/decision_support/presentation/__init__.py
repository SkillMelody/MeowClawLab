"""Native editable presentation views for audited decision packages."""

from .adapter import build_decision_presentation_ir
from .renderer import BuildResult, render_decision_deck

__all__ = ["BuildResult", "build_decision_presentation_ir", "render_decision_deck"]
