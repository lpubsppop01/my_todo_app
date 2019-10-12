#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

"""Implement tree structure traversal."""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import *


class TreeTraversal(metaclass=ABCMeta):
    """Tree structure traversal."""

    def __init__(self):
        pass

    @abstractmethod
    def parent(self, self_: Any) -> Optional[Any]:
        pass

    @abstractmethod
    def children(self, self_: Any) -> List[Any]:
        pass

    def descendants(self, self_: Any) -> List[Any]:
        result = []
        for child in self.children(self_):
            result.append(child)
            for child_result in self.descendants(child):
                result.append(child_result)
        return result

    def descendants_and_self(self, self_: Any) -> List[Any]:
        result = [self_]
        for descendant in self.descendants(self_):
            result.append(descendant)
        return result

    def ancestors(self, self_: Any) -> List[Any]:
        result = []
        parent = self.parent(self_)
        if parent is not None:
            result.append(parent)
            for parent_result in self.ancestors(parent):
                result.append(parent_result)
        return result
