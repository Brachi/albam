"""Compatibility import for the chain UI, now in ``mtfw.chain.ui``."""

from .chain import ui as _ui


def __getattr__(name):
    return getattr(_ui, name)
