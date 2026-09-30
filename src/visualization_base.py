"""
Base Visualization Module.

Provides BaseVisualizer with centralized headless Matplotlib/Seaborn configuration,
CJK font cascades, directory resolution, and figure export lifecycle management.
"""

from __future__ import annotations

import logging
import os
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import matplotlib

# Headless backend guarantee for headless server, CI, and CLI environments
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# Suppress common glyph and deprecation warnings across visualization backends
warnings.filterwarnings("ignore", message=".*Glyph.*missing from font.*")
warnings.filterwarnings("ignore", message=".*The set_bad function will be deprecated.*")
warnings.filterwarnings("ignore", message=".*vert: bool was deprecated.*")

logger = logging.getLogger("visualization_base")


class BaseVisualizer:
    """Base class for clustering and comparative market visualizers."""

    COHORT_COLORS: Dict[str, str] = {
        "jp": "#3b82f6",      # Japanese Domestic (Blue)
        "non-jp": "#ef4444",  # International / Overseas (Red)
        "all": "#8b5cf6",     # Combined Universe (Purple)
    }

    SUB_ORIGIN_COLORS: Dict[str, str] = {
        "JP": "#3b82f6",       # Japan
        "CN": "#ef4444",       # China (Donghua)
        "KR": "#10b981",       # Korea (Aeni)
        "WESTERN": "#f59e0b",  # Western (US/Europe)
        "OTHER": "#6b7280",    # Other International
    }

    def __init__(self, style: str = "whitegrid", dpi: int = 150) -> None:
        """
        Initialize common styling, DPI, and CJK font hierarchy.

        :param style: Seaborn theme style ('whitegrid', 'darkgrid', 'white', 'ticks').
        :param dpi: Resolution for rasterized figure export.
        """
        self.dpi = dpi
        self.style = style
        self._setup_style(style)

    def _setup_style(self, style: str) -> None:
        """Configure Seaborn theme and font fallbacks."""
        sns.set_theme(style=style)
        logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
        plt.rcParams["font.sans-serif"] = [
            "DejaVu Sans",
            "Noto Sans CJK JP",
            "Noto Sans CJK SC",
            "Noto Sans CJK KR",
            "WenQuanYi Zen Hei",
            "TakaoPGothic",
            "IPAGothic",
            "AppleGothic",
            "Arial Unicode MS",
            "sans-serif",
        ]
        plt.rcParams["axes.unicode_minus"] = False

    @staticmethod
    def _ensure_dir(output_path: Union[str, Path]) -> Path:
        """Ensure parent directory exists for target output path."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def _save_figure(
        self,
        fig: plt.Figure,
        output_path: Union[str, Path],
        dpi: Optional[int] = None,
        bbox_inches: str = "tight",
        close: bool = True,
    ) -> str:
        """
        Save figure to disk with directory safety and clean memory cleanup.

        :param fig: Matplotlib Figure instance.
        :param output_path: Destination file path.
        :param dpi: Optional DPI override (defaults to self.dpi).
        :param bbox_inches: Bounding box mode.
        :param close: Whether to close figure after saving to free memory.
        :return: String path of saved figure.
        """
        dest = self._ensure_dir(output_path)
        save_dpi = dpi or self.dpi
        fig.savefig(dest, dpi=save_dpi, bbox_inches=bbox_inches)
        if close:
            plt.close(fig)
        logger.debug("Saved figure to %s (dpi=%d)", dest, save_dpi)
        return str(dest)
