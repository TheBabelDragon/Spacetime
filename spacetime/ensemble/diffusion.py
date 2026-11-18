"""Primal-graph random-walk diffusion and spectral dimension estimator."""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Set, Tuple

from spacetime.ensemble.rng import Mulberry32

Adj = Dict[int, List[int]]


def primal_adjacency_from_edges(edges: Sequence[Tuple[int, int]]) -> Adj:
    adj: Dict[int, Set[int]] = {}
    for a, b in edges:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    return {v: sorted(nbrs) for v, nbrs in adj.items()}


def return_probabilities(
    adj: Adj,
    sigma_max: int,
    n_starts: int,
    rng: Mulberry32,
) -> Tuple[List[int], List[float], int]:
    nodes = sorted(adj.keys())
    n = len(nodes)
    if n == 0:
        return [], [], 0
    n_starts_used = min(n_starts, n)
    starts = [nodes[rng.randrange(n)] for _ in range(n_starts_used)]
    index = {v: i for i, v in enumerate(nodes)}
    nbr_idx = [[index[u] for u in adj[v]] for v in nodes]
    dists = []
    for s in starts:
        d = [0.0] * n
        d[index[s]] = 1.0
        dists.append(d)
    sigma_list: List[int] = []
    p_list: List[float] = []
    start_idx = [index[s] for s in starts]
    for step in range(1, sigma_max + 1):
        next_dists = []
        for d in dists:
            nd = [0.0] * n
            for i, p in enumerate(d):
                if p == 0.0:
                    continue
                nbrs = nbr_idx[i]
                if not nbrs:
                    nd[i] += p
                    continue
                share = p / len(nbrs)
                for j in nbrs:
                    nd[j] += share
            next_dists.append(nd)
        dists = next_dists
        ret = sum(dists[k][start_idx[k]] for k in range(n_starts_used)) / n_starts_used
        sigma_list.append(step)
        p_list.append(ret)
    return sigma_list, p_list, n_starts_used


def spectral_dimension(
    sigma: Sequence[int], p: Sequence[float]
) -> Tuple[List[int], List[Optional[float]]]:
    out_s: List[int] = []
    out_d: List[Optional[float]] = []
    for i in range(1, len(sigma)):
        s0, s1 = sigma[i - 1], sigma[i]
        p0, p1 = p[i - 1], p[i]
        out_s.append(s1)
        if p0 <= 0.0 or p1 <= 0.0 or s0 <= 0 or s1 <= 0:
            out_d.append(None)
            continue
        dln_p = math.log(p1) - math.log(p0)
        dln_s = math.log(s1) - math.log(s0)
        out_d.append(None if dln_s == 0.0 else -2.0 * dln_p / dln_s)
    return out_s, out_d
