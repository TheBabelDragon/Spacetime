/**
 * Browser-side 2D CDT geometry (shared conventions with Python Spacetime engine).
 * Source label: browser-demo — not a Python research result.
 */
(function (global) {
  "use strict";

  function vertexId(t, x, N) { return t * N + x; }
  function timeOf(v, N) { return Math.floor(v / N); }
  function spaceOf(v, N) { return v % N; }
  function canonEdge(a, b) { return a < b ? [a, b] : [b, a]; }
  function edgeKey(a, b) { const e = canonEdge(a, b); return e[0] + ":" + e[1]; }

  function buildFlatCDT(nSpatial, nTime, periodicTime) {
    const N = nSpatial | 0;
    const T = nTime | 0;
    if (N < 3) throw new Error("n_spatial must be ≥ 3");
    if (T < 2) throw new Error("n_time must be ≥ 2");

    const vertices = [];
    for (let t = 0; t < T; t++) for (let x = 0; x < N; x++) vertices.push(vertexId(t, x, N));

    const triangles = [];
    const edges = new Map();

    function addEdge(a, b) {
      const key = edgeKey(a, b);
      if (edges.has(key)) return;
      const ta = timeOf(a, N), tb = timeOf(b, N);
      let kind = "invalid";
      if (ta === tb) {
        const xa = spaceOf(a, N), xb = spaceOf(b, N);
        const d = Math.min((xa - xb + N) % N, (xb - xa + N) % N);
        kind = d === 1 ? "spacelike" : "invalid";
      } else if (
        Math.abs(ta - tb) === 1 ||
        (periodicTime && ((ta === 0 && tb === T - 1) || (tb === 0 && ta === T - 1)))
      ) {
        kind = "timelike";
      }
      edges.set(key, { a: Math.min(a, b), b: Math.max(a, b), kind });
    }

    function addTriangle(v0, v1, v2) {
      const times = new Set([timeOf(v0, N), timeOf(v1, N), timeOf(v2, N)]);
      if (times.size !== 2) throw new Error("triangle must span two time slices");
      const sortedT = [...times].sort((a, b) => a - b);
      const tLo = sortedT[0], tHi = sortedT[1];
      const adjacent = tHi === tLo + 1 || (periodicTime && tLo === 0 && tHi === T - 1);
      if (!adjacent) throw new Error("non-adjacent slices");
      const nLo = [v0, v1, v2].filter((v) => timeOf(v, N) === tLo).length;
      if (nLo !== 1 && nLo !== 2) throw new Error("not (1,2) or (2,1)");
      triangles.push({ verts: [v0, v1, v2], type: nLo === 2 ? 1 : -1 });
      addEdge(v0, v1); addEdge(v0, v2); addEdge(v1, v2);
    }

    const timePairs = [];
    for (let t = 0; t < T - 1; t++) timePairs.push([t, t + 1]);
    if (periodicTime) timePairs.push([T - 1, 0]);

    for (const [tLo, tHi] of timePairs) {
      for (let x = 0; x < N; x++) {
        const xNext = (x + 1) % N;
        const a = vertexId(tLo, x, N);
        const b = vertexId(tLo, xNext, N);
        const c = vertexId(tHi, x, N);
        const d = vertexId(tHi, xNext, N);
        addTriangle(a, b, c);
        addTriangle(b, c, d);
      }
    }

    const expectedN2 = periodicTime ? 2 * N * T : 2 * N * (T - 1);
    if (triangles.length !== expectedN2) {
      throw new Error("triangle count " + triangles.length + " ≠ expected " + expectedN2);
    }

    return {
      source: "browser",
      model: "cdt2d",
      config: { n_spatial: N, n_time: T, periodic_time: !!periodicTime },
      vertices,
      triangles,
      edges: [...edges.values()],
      n2: triangles.length,
      n0: vertices.length,
      topology: periodicTime ? "torus_S1xS1" : "cylinder_S1xI",
    };
  }

  function primalGraph(geom) {
    const adj = new Map();
    for (const v of geom.vertices) adj.set(v, new Set());
    for (const e of geom.edges) {
      if (e.kind === "invalid") continue;
      adj.get(e.a).add(e.b);
      adj.get(e.b).add(e.a);
    }
    return adj;
  }

  function layoutPositions(geom, width, height) {
    const N = geom.config.n_spatial;
    const T = geom.config.n_time;
    const padX = 40, padY = 36;
    const pos = new Map();
    for (let t = 0; t < T; t++) {
      for (let x = 0; x < N; x++) {
        const v = vertexId(t, x, N);
        const px = padX + ((width - 2 * padX) * (x + 0.5)) / N;
        const py = padY + ((height - 2 * padY) * t) / Math.max(1, T - 1);
        pos.set(v, { x: px, y: py });
      }
    }
    return pos;
  }

  function drawGeometry(canvas, geom, opts) {
    const ctx = canvas.getContext("2d");
    const w = canvas.width, h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    if (!geom) return;
    opts = opts || {};
    const showSpacelike = opts.showSpacelike !== false;
    const showTimelike = opts.showTimelike !== false;
    const showTriangles = opts.showTriangles !== false;
    const showLabels = !!opts.showLabels;
    const pos = layoutPositions(geom, w, h);

    if (showTriangles) {
      for (const tri of geom.triangles) {
        const p0 = pos.get(tri.verts[0]), p1 = pos.get(tri.verts[1]), p2 = pos.get(tri.verts[2]);
        ctx.beginPath();
        ctx.moveTo(p0.x, p0.y); ctx.lineTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y); ctx.closePath();
        ctx.fillStyle = tri.type === 1 ? "rgba(86,209,255,0.08)" : "rgba(167,139,250,0.12)";
        ctx.fill();
      }
    }
    for (const e of geom.edges) {
      if (e.kind === "spacelike" && !showSpacelike) continue;
      if (e.kind === "timelike" && !showTimelike) continue;
      if (e.kind === "invalid") continue;
      const p0 = pos.get(e.a), p1 = pos.get(e.b);
      ctx.beginPath(); ctx.moveTo(p0.x, p0.y); ctx.lineTo(p1.x, p1.y);
      if (e.kind === "spacelike") { ctx.strokeStyle = "#56d1ff"; ctx.lineWidth = 1.5; }
      else { ctx.strokeStyle = "#f0a56e"; ctx.lineWidth = 1.2; ctx.setLineDash([4, 3]); }
      ctx.stroke(); ctx.setLineDash([]);
    }
    for (const v of geom.vertices) {
      const p = pos.get(v);
      ctx.beginPath(); ctx.arc(p.x, p.y, 3.5, 0, Math.PI * 2);
      ctx.fillStyle = "#d7e3f4"; ctx.fill();
      if (showLabels) {
        ctx.fillStyle = "#8aa0bd";
        ctx.font = "10px ui-monospace, monospace";
        ctx.fillText(String(v), p.x + 5, p.y - 5);
      }
    }
  }

  function toManifest(geom, extra) {
    return Object.assign({
      format: "spacetime-observatory-manifest/v1",
      source: geom.source || "browser",
      model: geom.model,
      config: geom.config,
      topology: geom.topology,
      combinatorics: { n0: geom.n0, n2: geom.n2, n_edges: geom.edges.length },
      software: { ui: "spacetime-observatory", engine: "browser-js" },
      created_at: new Date().toISOString(),
    }, extra || {});
  }

  global.SpacetimeCDT = { buildFlatCDT, primalGraph, drawGeometry, toManifest, vertexId, timeOf, spaceOf };
})(typeof window !== "undefined" ? window : globalThis);
