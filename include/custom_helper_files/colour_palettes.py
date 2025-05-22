# -*- coding: utf-8 -*-

# -------------------------- Preprocessing Directives -------------------------

# Standard Libraries
import logging as lg
# import os as os
from sys import exit

# 3rd Party packages
from datetime import datetime

# import matplotlib.pyplot as plt
# import numpy as np

# My packages/Header files
# Here

# ----------------------------- Program Information ----------------------------

"""
Class with helper methods for generating color palettes saved by the user
"""
PROGRAM_NAME = "color_palettes.py"
"""
Created on 25 Nov 24 by cameronmceleney
"""

__all__ = [
    "ColorPalette",
    "PaletteAccessor"
]

# ---------------------------- Function Declarations ---------------------------
class ColorPalette:
    """
    Class with helper methods for generating color palettes saved by the user.

    Attributes
    ----------
    palettes : dict
        Dictionary containing the saved palettes.
    active_palette : dict
        The currently loaded palette.

    Usage
    -----
    # Initialize the class
    CP = ColorPalette()

    # Add palettes
    CP.add_palette("dutch_field", ["#e60049", "#0bb4ff", "#50e991"])  # Auto-indexed
    CP.add_palette("custom", [["blue", "#e60049"], ["orange", "#0bb4ff"], ["red", "#50e991"]])  # Keyed

    # Accessing colors by palette
    print(CP["dutch_field"][0])  # "#e60049" (indexed)
    print(CP["dutch_field"]["1"])  # "#e60049" (keyed auto-generated)
    print(CP["custom"]["blue"])  # "#e60049" (keyed manually)

    # Load a palette and use it
    CP.load_palette("custom")
    print(CP.use("blue"))  # "#e60049"
    print(CP.use(1))  # "#0bb4ff" (indexed access)
    """

    def __init__(self):
        # Initialize the palette storage with some default palettes
        self.palettes = {
            # https://www.heavy.ai/blog/12-color-palettes-for-telling-better-stories-with-your-data
            "dutch_field": {
                "red": "#e60049",
                "blue": "#0bb4ff",
                "green": "#50e991",
                "yellow": "#e6d800",
                "purple": "#9b19f5",
                "orange": "#ffa300",
                "magenta": "#dc0ab4",
                "lightblue": "#b3d4ff",
                "turquoise": "#00bfa0",
            },

            # https://www.heavy.ai/blog/12-color-palettes-for-telling-better-stories-with-your-data
            "spring_pastels": {
                "red": "#fd7f6f",
                "blue": "#7eb0d5",
                "green": "#b2e061",
                "purple": "#bd7ebe",
                "orange": "#ffb55a",
                "yellow": "#ffee65",
                "lightpurple": "#beb9db",
                "pink": "#fdcce5",
                "turquoise": "#8bd3c7",
            },
            # https://www.heavy.ai/blog/12-color-palettes-for-telling-better-stories-with-your-data
            "river_nights": {
                "red": "#b30000",
                "darkpurple": "#7c1158",
                "purple": "#4421af",
                "darkblue": "#1a53ff",
                "blue": "#0d88e6",
                "cyan": "#00b7c7",
                "green": "#5ad45a",
                "lightgreen": "#8be04e",
                "yellow": "#ebdc78",
            },
        }
        self.active_palette = None  # Tracks the currently loaded palette

    def add_palette(self, name, colors):
        """Add a new palette. Supports both list and key-value formats."""
        if isinstance(colors, list):
            palette = {}
            for i, color in enumerate(colors, start=1):
                # If a sub-item is a list (key-value), use it; otherwise, auto-generate keys
                if isinstance(color, (list, tuple)):
                    palette[str(color[0])] = color[1]
                else:
                    palette[str(i)] = color
            self.palettes[name] = palette
        elif isinstance(colors, dict):
            # If a dictionary is directly passed
            self.palettes[name] = {str(k): v for k, v in colors.items()}
        else:
            raise ValueError("Colors must be a list or dictionary.")

    def get_palette(self, name):
        """Retrieve a palette by its name."""
        return self.palettes.get(name, None)

    def load_palette(self, name):
        """Set a palette as active for direct color access."""
        palette = self.get_palette(name)
        if palette:
            self.active_palette = palette
        else:
            raise ValueError(f"Palette '{name}' does not exist.")

    def use(self, key_or_index):
        """Access a color from the active palette using key or index."""
        if not self.active_palette:
            raise ValueError("No palette is currently loaded. Use `load_palette()` first.")
        # Try accessing by key; fallback to indexed access
        if isinstance(key_or_index, str):
            return self.active_palette.get(key_or_index)
        elif isinstance(key_or_index, int):
            keys = list(self.active_palette.keys())
            if 0 <= key_or_index < len(keys):
                return self.active_palette[keys[key_or_index]]
        raise KeyError(f"Key or index '{key_or_index}' is invalid.")

    def __getitem__(self, name):
        """Dictionary-style access to palettes."""
        palette = self.palettes.get(name, None)
        if palette:
            # Allow indexed or key access
            return PaletteAccessor(palette)
        raise KeyError(f"Palette '{name}' does not exist.")

    def __getattr__(self, name):
        """Attribute-style access to palettes."""
        if name in self.palettes:
            return PaletteAccessor(self.palettes[name])
        raise AttributeError(f"'ColorPalette' object has no attribute '{name}'")


class PaletteAccessor:
    def __init__(self, palette):
        self.palette = palette

    def __getitem__(self, key_or_index):
        """Access colors by key or index."""
        if isinstance(key_or_index, str):
            return self.palette.get(key_or_index)
        elif isinstance(key_or_index, int):
            keys = list(self.palette.keys())
            if 0 <= key_or_index < len(keys):
                return self.palette[keys[key_or_index]]
        raise KeyError(f"Key or index '{key_or_index}' is invalid.")

    def __repr__(self):
        return repr(self.palette)