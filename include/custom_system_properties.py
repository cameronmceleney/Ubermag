# -*- coding: utf-8 -*-

# -------------------------- Preprocessing Directives -------------------------

# Standard Libraries
import logging as lg
from sys import exit

# 3rd Party packages
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict

# Ubermag modules
import discretisedfield as df

# ----------------------------- Program Information ----------------------------

"""
Description of what custom_system_properties.py does
"""
PROGRAM_NAME = "custom_system_properties.py"
"""
Created on 23 May 24 by Cameron Aidan McEleney
"""


# ---------------------------- Function Declarations ---------------------------

def loggingSetup():
    """
    Minimum Working Example (MWE) for logging. Pre-defined levels are:
        
        Highest               ---->            Lowest
        CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
    """
    today_date = datetime.now().strftime("%y%m%d")
    current_time = datetime.now().strftime("%H%M")

    lg.basicConfig(filename=f'./{today_date}-{current_time}.log',
                   filemode='w',
                   level=lg.INFO,
                   format='%(asctime)s | %(module)s::%(funcName)s | %(levelname)s | %(message)s',
                   datefmt='%Y-%m-%d %H:%M:%S',
                   force=True)

# ------------------------------ Implementations ------------------------------


@dataclass
class SystemProperties:
    lx: float
    ly: float
    lz: float
    cell: tuple = field(default_factory=lambda: (1e-9, 1e-9, 1e-9))
    p1: tuple = field(default_factory=lambda: (0, 0, 0))
    units: tuple = field(default_factory=lambda: ('m', 'm', 'm'))
    p2: tuple = field(init=False)
    numcells: tuple = field(init=False)

    def __post_init__(self):
        if len(self.cell) == 3 and all(c != 0 for c in self.cell):
            self.numcells = (self.lx, self.ly, self.lz)
            self.lx *= self.cell[0]
            self.ly *= self.cell[1]
            self.lz *= self.cell[2]
            self.p2 = (self.lx, self.ly, self.lz)
        else:
            raise ValueError("Cell must be a tuple of three non-zero values")


@dataclass
class SubRegion:
    p1: tuple = field(default_factory=tuple)
    p2: tuple = field(default_factory=tuple)
    region: df.Region = field(init=False, default=None)
    dims: tuple = field(init=False, default_factory=tuple)
    cellsize: tuple = field(init=False, default_factory=tuple)
    units: tuple = field(init=False, default_factory=tuple)

    def __call__(self, p1=None, p2=None, cellsize=None, units=None, dims=None, auto_create=True):

        if p1 is None or p2 is None:
            if self.p1 is not None and self.p2 is not None:
                if cellsize is not None:
                    self.cellsize = cellsize

                if units is not None:
                    if type(units) is tuple:
                        self.units = units
                    elif len(units) == 1:
                        self.p1 = tuple(coord * units for coord in self.p1)
                        self.p2 = tuple(coord * units for coord in self.p2)

                if dims is not None:
                    self.dims = dims
            else:
                print('Invalid args in call')
        else:
            self.p1 = p1
            self.p2 = p2

            if cellsize is not None:
                self.p1 = tuple(self.p1[j] * cellsize[j] for j in range(3))
                self.p2 = tuple(self.p2[j] * cellsize[j] for j in range(3))
            elif units is not None and type(units) is not tuple:
                self.p1 = tuple(coord * units for coord in self.p1)
                self.p2 = tuple(coord * units for coord in self.p2)

            if auto_create:
                self.create()

    def create(self):
        if len(self.p1) == 0 or len(self.p2) == 0:
            print('Invalid args in call')
        else:
            self.region = df.Region(p1=self.p1, p2=self.p2)


class MyRegions:
    def __init__(self, name: str):
        self.name = name
        self._subregions: Dict[str, SubRegion] = {}

    def __getattr__(self, subregion_name: str):
        if subregion_name == "subregion":
            return self
        if subregion_name == self.name:
            return self.name
        if subregion_name not in self._subregions:
            self._subregions[subregion_name] = SubRegion()
        return self._subregions[subregion_name]

    def delete_subregion(self, subregion_name: str):
        if subregion_name in self._subregions:
            del self._subregions[subregion_name]
        else:
            raise KeyError(f"Subregion '{subregion_name}' does not exist")