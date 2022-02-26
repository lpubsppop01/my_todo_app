#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Implement generic class that is being lazily initialized."""

from typing import Optional, TypeVar, Generic, Callable

T = TypeVar('T')


class Lazy(Generic[T]):
    """Generic class that is being lazily initialized."""

    def __init__(self, get_value: Callable[[], T]) -> None:
        self._get_value = get_value
        self._value: Optional[T] = None

    @property
    def value(self) -> T:
        if self._value is None:
            self._value = self._get_value()
        return self._value
