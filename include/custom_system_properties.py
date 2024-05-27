# -*- coding: utf-8 -*-

# -------------------------- Preprocessing Directives -------------------------

# Standard Libraries
import logging as lg
from sys import exit

# 3rd Party packages
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List

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
    cell: tuple = field(default_factory=lambda: (0e-9, 0e-9, 0e-9))
    p1: tuple = field(default_factory=lambda: (0, 0, 0))
    units: tuple = field(default=('m', 'm', 'm'))
    p2: tuple = field(init=False)
    numcells: tuple = field(init=False)

    def __post_init__(self):
        if len(self.cell) == 3 and all(c > 0 for c in self.cell):
            self.update_lengths()
        self.p2 = (self.lx, self.ly, self.lz)

    def update_lengths(self):
        if len(self.cell) == 3 and all(c > 0 for c in self.cell):
            self.lx *= self.cell[0]
            self.ly *= self.cell[1]
            self.lz *= self.cell[2]

            self.p2 = (self.lx, self.ly, self.lz)
        else:
            raise ValueError("Cell must be a tuple of three non-zero values")

    def update_numcells(self):
        if len(self.cell) == 3 and all(c > 0 for c in self.cell):
            self.numcells = (int(self.lx / self.cell[0]),
                             int(self.ly / self.cell[1]),
                             int(self.lz / self.cell[2]))
        else:
            raise ValueError("Cell must be a tuple of three non-zero values")


@dataclass
class SubRegion:
    p1: tuple = field(default_factory=tuple)
    p2: tuple = field(default_factory=tuple)
    region: df.Region = field(init=False, default=None)
    dims: tuple = field(init=False, default_factory=lambda: ('x', 'y', 'z'))
    cellsize: tuple = field(init=False, default_factory=lambda: (0e-9, 0e-9, 0e-9))
    units: tuple = field(init=False, default_factory=lambda: ('m', 'm', 'm'))
    mesh: df.Mesh = field(init=False, default=None)

    def __call__(self, **kwargs):
        if kwargs:
            self.set_values(**kwargs)
            if kwargs.get('auto_create', True):
                self.create()

        # Default options for if no kwargs are passed (ideally want to return the region)
        if self.region is not None:
            return self.region
        else:
            return self.p2

    def set_values(self, **kwargs):
        # Assign positions (p) that are required to draw a cuboid
        if 'p1' in kwargs:
            self.p1 = kwargs['p1']
        if 'p2' in kwargs:
            self.p2 = kwargs['p2']

        if 'cellsize' in kwargs and kwargs['cellsize'] is not None:
            self.cellsize = kwargs['cellsize']
            self.p1 = tuple(self.p1[j] * self.cellsize[j] for j in range(len(self.p1)))
            self.p2 = tuple(self.p2[j] * self.cellsize[j] for j in range(len(self.p2)))

        if 'units' in kwargs and kwargs['units'] is not None:
            if isinstance(kwargs['units'], tuple) and isinstance(kwargs['units'][0], float):
                self.p1 = tuple(coord * unit for coord, unit in zip(self.p1, kwargs['units']))
                self.p2 = tuple(coord * unit for coord, unit in zip(self.p2, kwargs['units']))
            else:
                self.units = kwargs['units']

        if 'dims' in kwargs and kwargs['dims'] is not None:
            self.dims = kwargs['dims']

    def create(self):
        if len(self.p1) == 0 or len(self.p2) == 0:
            print('Invalid args in call')
        else:
            self.region = df.Region(p1=self.p1, p2=self.p2, units=self.units, dims=self.dims)


class MyRegions:
    def __init__(self, name: str):
        self.name = name
        self._details: Dict[str, SubRegion] = {}
        self._mesh: None | df.Mesh = field(init=False, default=None)

    def __getattr__(self, region_name: str):
        if region_name == self.name:
            return self.name

        if region_name == '_details':
            print('are you sure?')
            return self._details

        if region_name not in self._details:
            self._details[region_name] = SubRegion()
            self.regions[region_name] = self._details[region_name].region
            print(f'Created subregion: {region_name}')
        return self._details[region_name]

    def __repr__(self):
        regions_repr = {name: repr(region) for name, region in self._details.items()}
        return f"MyRegions(name={self.name}, regions={regions_repr})"

    @property
    def regions(self):
        # Dynamically create a dict of initialized regions
        return {name: subregion.region for name, subregion in self._details.items() if subregion.region is not None}

    @property
    def mag_vals(self):
        # Dynamically create a dict of initialized regions
        return {name: (0, 0, 1) for name, subregion in self._details.items() if subregion.region is not None}

    def delete_subregion(self, region_name: str):
        if region_name in self.regions:
            del self.regions[region_name]
        else:
            raise KeyError(f"(Sub)region '{region_name}' does not exist")
        if region_name in self._details:
            del self._details[region_name]
        else:
            raise KeyError(f"(Sub)region '{region_name}' does not exist in details!")


def add_tuples(tuple_a: tuple, tuple_b=None, mult=None, dims=None, base=None):
    if tuple_b is None:
        # Create a tuple of zeros with the same length as tuple1 (to handle 1D/2D/3D cases)
        tuple_b = (0,) * len(tuple_a)

    if mult is not None and isinstance(mult, (float, int)):
        tuple_b = tuple(val * mult for val in tuple_b)

    # Get indexes of dims to be summed, else default to all dims
    dim_to_index = {'x': 0, 'X': 0, 'y': 1, 'Y': 1, 'z': 2, 'Z': 2}
    dims_idxs = [dim_to_index[dim] for dim in dims] if dims is not None else range(len(tuple_a))

    result = list(base if base is not None else tuple_a)

    for i in dims_idxs:
        if i < len(tuple_a):
            result[i] = tuple_a[i] + tuple_b[i]

    return tuple(result)
