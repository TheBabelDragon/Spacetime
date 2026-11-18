"""Deterministic Mulberry32 RNG and geometry stream derivation."""

from __future__ import annotations


def geometry_seed(master_seed: int, geometry_index: int) -> int:
    if geometry_index < 0:
        raise ValueError("geometry_index must be ≥ 0")
    return (int(master_seed) + 10007 * (int(geometry_index) + 1)) & 0xFFFFFFFF


class Mulberry32:
    __slots__ = ("_state",)

    def __init__(self, seed: int) -> None:
        self._state = int(seed) & 0xFFFFFFFF

    def next_u32(self) -> int:
        self._state = (self._state + 0x6D2B79F5) & 0xFFFFFFFF
        t = self._state
        t = ((t ^ (t >> 15)) * (t | 1)) & 0xFFFFFFFF
        t ^= (t + ((t ^ (t >> 7)) * (t | 61))) & 0xFFFFFFFF
        return (t ^ (t >> 14)) & 0xFFFFFFFF

    def next_float(self) -> float:
        return self.next_u32() / 4294967296.0

    def randrange(self, n: int) -> int:
        if n <= 0:
            raise ValueError("n must be positive")
        return int(self.next_float() * n) % n
