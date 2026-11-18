/**
 * Discrete diffusion on the primal graph for spectral-dimension estimates.
 * D_s(σ) = -2 d ln P(σ) / d ln σ
 * Browser-side demonstration only.
 */
(function (global) {
  "use strict";

  function mulberry32(seed) {
    let t = seed >>> 0;
    return function () {
      t += 0x6d2b79f5;
      let r = Math.imul(t ^ (t >>> 15), 1 | t);
      r ^= r + Math.imul(r ^ (r >>> 7), 61 | r);
      return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
    };
  }

  function randomWalkReturnProbabilities(adj, sigmaMax, nStarts, seed) {
    const nodes = [...adj.keys()];
    const n = nodes.length;
    if (n === 0) return { sigma: [], P: [], source: "browser" };
    const rng = mulberry32(seed >>> 0);
    const starts = [];
    for (let i = 0; i < Math.min(nStarts, n); i++) starts.push(nodes[Math.floor(rng() * n)]);

    let dists = starts.map((s) => {
      const d = new Map();
      for (const v of nodes) d.set(v, 0);
      d.set(s, 1);
      return d;
    });

    const sigma = [], P = [];
    for (let step = 1; step <= sigmaMax; step++) {
      const nextDists = dists.map((d) => {
        const nd = new Map();
        for (const v of nodes) nd.set(v, 0);
        for (const v of nodes) {
          const p = d.get(v);
          if (p === 0) continue;
          const nbrs = [...adj.get(v)];
          if (nbrs.length === 0) { nd.set(v, nd.get(v) + p); continue; }
          const share = p / nbrs.length;
          for (const u of nbrs) nd.set(u, nd.get(u) + share);
        }
        return nd;
      });
      dists = nextDists;
      let ret = 0;
      for (let i = 0; i < starts.length; i++) ret += dists[i].get(starts[i]);
      ret /= starts.length;
      sigma.push(step);
      P.push(ret);
    }
    return { sigma, P, graph: "primal", source: "browser", n_vertices: n, n_starts: starts.length, seed };
  }

  function spectralDimension(sigma, P) {
    const Ds = [], sigOut = [];
    for (let i = 1; i < sigma.length; i++) {
      const s0 = sigma[i - 1], s1 = sigma[i], p0 = P[i - 1], p1 = P[i];
      if (p0 <= 0 || p1 <= 0 || s0 <= 0 || s1 <= 0) { Ds.push(NaN); sigOut.push(s1); continue; }
      const dlnP = Math.log(p1) - Math.log(p0);
      const dlnS = Math.log(s1) - Math.log(s0);
      Ds.push(dlnS !== 0 ? (-2 * dlnP) / dlnS : NaN);
      sigOut.push(s1);
    }
    return { sigma: sigOut, Ds };
  }

  function drawSpectral(canvas, data) {
    const ctx = canvas.getContext("2d");
    const w = canvas.width, h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    if (!data || !data.sigma || data.sigma.length === 0) return;

    const pad = { l: 48, r: 16, t: 20, b: 36 };
    const plotW = w - pad.l - pad.r, plotH = h - pad.t - pad.b;
    ctx.fillStyle = "#8aa0bd";
    ctx.font = "11px ui-monospace, monospace";
    ctx.fillText("σ", w / 2, h - 8);

    const { Ds } = spectralDimension(data.sigma, data.P);
    const maxS = Math.max(...data.sigma);
    const maxP = Math.max(...data.P, 1e-12);
    const dsValid = Ds.filter((x) => Number.isFinite(x));
    const maxDs = dsValid.length ? Math.max(...dsValid, 2) : 4;
    const minDs = dsValid.length ? Math.min(...dsValid, 0) : 0;

    function xMap(s) { return pad.l + (plotW * Math.log(s)) / Math.log(maxS); }
    function yMapP(p) {
      const lp = Math.log(Math.max(p, 1e-15));
      const lpMax = Math.log(maxP);
      const positives = data.P.filter((x) => x > 0);
      const lpMin = Math.log(Math.max(Math.min(...positives), 1e-15));
      const t = (lp - lpMin) / (lpMax - lpMin || 1);
      return pad.t + plotH * (1 - t);
    }
    function yMapDs(d) {
      const t = (d - minDs) / (maxDs - minDs || 1);
      return pad.t + plotH * (1 - t);
    }

    ctx.strokeStyle = "#1e2d45";
    ctx.beginPath();
    ctx.moveTo(pad.l, pad.t);
    ctx.lineTo(pad.l, pad.t + plotH);
    ctx.lineTo(pad.l + plotW, pad.t + plotH);
    ctx.stroke();

    ctx.strokeStyle = "#56d1ff"; ctx.lineWidth = 1.5; ctx.beginPath();
    for (let i = 0; i < data.sigma.length; i++) {
      if (data.P[i] <= 0) continue;
      const x = xMap(data.sigma[i]), y = yMapP(data.P[i]);
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.stroke();

    ctx.strokeStyle = "#a78bfa"; ctx.lineWidth = 1.5; ctx.beginPath();
    let started = false;
    for (let i = 0; i < Ds.length; i++) {
      if (!Number.isFinite(Ds[i])) continue;
      const x = xMap(data.sigma[i + 1] || data.sigma[i]);
      const y = yMapDs(Ds[i]);
      if (!started) { ctx.moveTo(x, y); started = true; } else ctx.lineTo(x, y);
    }
    ctx.stroke();

    ctx.fillStyle = "#56d1ff"; ctx.fillRect(pad.l + 8, pad.t + 6, 12, 3);
    ctx.fillStyle = "#8aa0bd"; ctx.fillText("P(σ)", pad.l + 24, pad.t + 12);
    ctx.fillStyle = "#a78bfa"; ctx.fillRect(pad.l + 80, pad.t + 6, 12, 3);
    ctx.fillStyle = "#8aa0bd"; ctx.fillText("Ds(σ)", pad.l + 96, pad.t + 12);
  }

  global.SpacetimeDiffusion = { randomWalkReturnProbabilities, spectralDimension, drawSpectral };
})(typeof window !== "undefined" ? window : globalThis);
