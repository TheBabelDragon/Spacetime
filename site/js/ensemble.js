/**
 * Browser-side CDT ensemble preview (NOT the authoritative Python engine).
 */
(function (global) {
  "use strict";

  var SCHEMA_VERSION = "ensemble/v1";
  var ALGORITHM_VERSION = "cdt2d-flat+rw-primal/0.3.0";
  var ENGINE_VERSION = "0.3.0-browser";

  function geometrySeed(master, index) {
    return (master + 10007 * (index + 1)) >>> 0;
  }

  function Mulberry32(seed) {
    this.state = seed >>> 0;
  }
  Mulberry32.prototype.nextU32 = function () {
    this.state = (this.state + 0x6d2b79f5) >>> 0;
    var t = this.state;
    t = Math.imul(t ^ (t >>> 15), 1 | t);
    t ^= t + Math.imul(t ^ (t >>> 7), 61 | t);
    return (t ^ (t >>> 14)) >>> 0;
  };
  Mulberry32.prototype.nextFloat = function () {
    return this.nextU32() / 4294967296;
  };
  Mulberry32.prototype.randrange = function (n) {
    return (this.nextFloat() * n) | 0;
  };

  function validateConfig(cfg) {
    if (cfg.nSpatial < 3) throw new Error("n_spatial must be ≥ 3");
    if (cfg.nTime < 2) throw new Error("n_time must be ≥ 2");
    if (cfg.nGeometries < 1) throw new Error("n_geometries must be ≥ 1");
    if (cfg.sigmaMax < 2) throw new Error("sigma_max must be ≥ 2");
    if (cfg.nStarts < 1) throw new Error("n_starts must be ≥ 1");
    return cfg;
  }

  function mean(xs) {
    if (!xs.length) return null;
    var s = 0;
    for (var i = 0; i < xs.length; i++) s += xs[i];
    return s / xs.length;
  }

  function sampleVar(xs) {
    if (xs.length < 2) return 0;
    var m = mean(xs);
    var s = 0;
    for (var i = 0; i < xs.length; i++) s += (xs[i] - m) * (xs[i] - m);
    return s / (xs.length - 1);
  }

  function aggregate(seriesList) {
    var nSteps = seriesList[0] ? seriesList[0].length : 0;
    var out = { mean: [], std: [], stderr: [], ci95_low: [], ci95_high: [], n_valid: [] };
    for (var t = 0; t < nSteps; t++) {
      var vals = [];
      for (var g = 0; g < seriesList.length; g++) {
        var v = seriesList[g][t];
        if (v !== null && v !== undefined && isFinite(v)) vals.push(v);
      }
      out.n_valid.push(vals.length);
      if (!vals.length) {
        out.mean.push(null); out.std.push(null); out.stderr.push(null);
        out.ci95_low.push(null); out.ci95_high.push(null);
        continue;
      }
      var m = mean(vals);
      var sd = Math.sqrt(sampleVar(vals));
      var se = sd / Math.sqrt(vals.length);
      out.mean.push(m);
      out.std.push(sd);
      out.stderr.push(se);
      out.ci95_low.push(m - 1.96 * se);
      out.ci95_high.push(m + 1.96 * se);
    }
    out.ci95_method = "normal_approx_1.96_stderr";
    return out;
  }

  function runEnsemble(cfg, onProgress, shouldCancel) {
    cfg = validateConfig(cfg);
    var geos = [];
    var pSeries = [];
    var dsSeries = [];
    var sigma = null;
    for (var i = 0; i < cfg.nGeometries; i++) {
      if (shouldCancel && shouldCancel()) throw new Error("cancelled");
      var seed = geometrySeed(cfg.masterSeed, i);
      var geom = SpacetimeCDT.buildFlatCDT(cfg.nSpatial, cfg.nTime, cfg.periodicTime);
      var adj = SpacetimeCDT.primalGraph(geom);
      var diff = SpacetimeDiffusion.randomWalkReturnProbabilities(adj, cfg.sigmaMax, cfg.nStarts, seed);
      var ds = SpacetimeDiffusion.spectralDimension(diff.sigma, diff.P);
      var dsVals = ds.Ds.map(function (x) { return isFinite(x) ? x : null; });
      geos.push({
        geometry_index: i, seed: seed, n0: geom.n0, n2: geom.n2,
        sigma: diff.sigma, P: diff.P, Ds_sigma: ds.sigma, Ds: dsVals,
        n_starts_used: diff.n_starts,
      });
      pSeries.push(diff.P);
      dsSeries.push(dsVals);
      if (!sigma) sigma = diff.sigma;
      if (onProgress) onProgress(i + 1, cfg.nGeometries);
    }
    return {
      format: "spacetime-ensemble-manifest/v1",
      source: "browser",
      config: {
        n_spatial: cfg.nSpatial, n_time: cfg.nTime, periodic_time: !!cfg.periodicTime,
        n_geometries: cfg.nGeometries, master_seed: cfg.masterSeed,
        sigma_max: cfg.sigmaMax, n_starts: cfg.nStarts, start_policy: "uniform_seeded",
        schema_version: SCHEMA_VERSION, algorithm_version: ALGORITHM_VERSION,
        engine_version: ENGINE_VERSION,
      },
      notes: [
        "source=browser preview — Python is authoritative for published claims",
        "graph=primal", "geometry_v0.3=flat_cylinder_or_torus",
        "ci95=normal_approx 1.96*stderr",
      ],
      sigma: sigma,
      P_ensemble: aggregate(pSeries),
      Ds_ensemble: aggregate(dsSeries),
      geometries: geos,
      n_geometries: geos.length,
    };
  }

  function csvP(result) {
    var lines = ["sigma,P_mean,P_std,P_stderr,P_ci95_low,P_ci95_high,n_valid"];
    var a = result.P_ensemble;
    for (var i = 0; i < result.sigma.length; i++) {
      lines.push([result.sigma[i], a.mean[i], a.std[i], a.stderr[i], a.ci95_low[i], a.ci95_high[i], a.n_valid[i]].join(","));
    }
    return lines.join("\n");
  }

  function csvDs(result) {
    var lines = ["sigma,Ds_mean,Ds_std,Ds_stderr,Ds_ci95_low,Ds_ci95_high,n_valid"];
    var a = result.Ds_ensemble;
    var dsSigma = result.geometries[0] ? result.geometries[0].Ds_sigma : [];
    for (var i = 0; i < dsSigma.length; i++) {
      lines.push([dsSigma[i], a.mean[i], a.std[i], a.stderr[i], a.ci95_low[i], a.ci95_high[i], a.n_valid[i]].join(","));
    }
    return lines.join("\n");
  }

  global.SpacetimeEnsemble = {
    SCHEMA_VERSION: SCHEMA_VERSION,
    ALGORITHM_VERSION: ALGORITHM_VERSION,
    ENGINE_VERSION: ENGINE_VERSION,
    geometrySeed: geometrySeed,
    runEnsemble: runEnsemble,
    csvP: csvP,
    csvDs: csvDs,
    validateConfig: validateConfig,
  };
})(typeof window !== "undefined" ? window : globalThis);
