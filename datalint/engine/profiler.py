"""
Data profiling module.

This module re-exports the profiling functionality from learner.py
for convenience and backward compatibility.

Usage:
    from datalint.engine.profiler import DataProfile, RuleLearner
"""

from .learner import DataProfile, RuleLearner

__all__ = ["DataProfile", "RuleLearner"]
