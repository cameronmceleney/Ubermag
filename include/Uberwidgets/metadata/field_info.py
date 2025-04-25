#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project: Ubermag
Path:    include/Uberwidgets/metadata/field_info.py

Description:
    Dataclasses which group values required to define Ubermag df.Field instances in order to improve readability
    when generating python widgets.
    
Author:      Cameron Aidan McEleney < c.mceleney.1@research.gla.ac.uk >
Created:     25 Apr 2025
IDE:         PyCharm
Version:     0.1.0
"""

# Standard library imports
from dataclasses import dataclass, field
from typing import Any, Iterator, Mapping

# Third-party imports

# Local application imports

@dataclass(frozen=True)
class FieldInfo(Mapping[str, Any]):
    label: str
    symbol: str = ''
    options: list[str] = field(default_factory=list)
    units: dict[str,str] = field(default_factory=dict)
    group: str = ''

    def __getitem__(self, key: str) -> Any:
        # redirect key lookups to the corresponding attribute
        if key in self.__dict__:
            return getattr(self, key)
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        # iterate over our five metadata keys
        yield from ("label", "symbol", "options", "units", "group")

    def __len__(self) -> int:
        return len(self.__dict__)

    def __repr__(self) -> str:
        # dict-like printout
        return repr({k: self[k] for k in self})
