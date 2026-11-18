(function () {
  "use strict";
  const state = { geom: null, diffusion: null, manifest: null, ensemble: null, ensCancel: false };
  const $ = (id) => document.getElementById(id);

  (function setBuildId() {
    var el = $("buildId");
    if (!el) return;
    var eng = (window.SpacetimeEnsemble && SpacetimeEnsemble.ENGINE_VERSION) || "n/a";
    var schema = (window.SpacetimeEnsemble && SpacetimeEnsemble.SCHEMA_VERSION) || "n/a";
    el.textContent = "UI 0.3.0 · engine " + eng + " · " + schema;
  })();

  function readParams() {
    return {
      nSpatial: Math.max(3, parseInt($("nSpatial").value, 10) || 6),
      nTime: Math.max(2, parseInt($("nTime").value, 10) || 4),
      periodicTime: $("periodicTime").checked,
    };
  }

  function buildGeometry() {
    const p = readParams();
    try {
      state.geom = SpacetimeCDT.buildFlatCDT(p.nSpatial, p.nTime, p.periodicTime);
      state.manifest = SpacetimeCDT.toManifest(state.geom, { note: "Browser-side flat CDT construction" });
      renderGeometry(); renderManifest(); updateGeomMeta(); runValidationTable();
    } catch (err) {
      $("geomMeta").textContent = "Error: " + err.message;
    }
  }

  function vizOpts() {
    return {
      showSpacelike: $("showSpacelike").checked,
      showTimelike: $("showTimelike").checked,
      showTriangles: $("showTriangles").checked,
      showLabels: $("showLabels").checked,
    };
  }

  function renderGeometry() {
    SpacetimeCDT.drawGeometry($("cdtCanvas"), state.geom, vizOpts());
  }

  function updateGeomMeta() {
    if (!state.geom) { $("geomMeta").textContent = "No geometry."; return; }
    const g = state.geom;
    $("geomMeta").textContent = [
      "source: " + g.source + " (browser)",
      "topology: " + g.topology,
      "N=" + g.config.n_spatial + " T=" + g.config.n_time + " periodic=" + g.config.periodic_time,
      "N0=" + g.n0 + " N2=" + g.n2,
    ].join("\n");
  }

  function runDiffusion() {
    if (!state.geom) buildGeometry();
    if (!state.geom) return;
    const sigmaMax = Math.max(2, parseInt($("sigmaMax").value, 10) || 40);
    const nStarts = Math.max(1, parseInt($("nStarts").value, 10) || 32);
    const seed = parseInt($("diffSeed").value, 10) || 0;
    const adj = SpacetimeCDT.primalGraph(state.geom);
    state.diffusion = SpacetimeDiffusion.randomWalkReturnProbabilities(adj, sigmaMax, nStarts, seed);
    SpacetimeDiffusion.drawSpectral($("spectralCanvas"), state.diffusion);
    $("spectralMeta").textContent = "source: browser · primal · σ_max=" + sigmaMax;
  }

  function renderManifest() {
    if (!state.manifest) { $("manifestView").textContent = "No experiment loaded."; return; }
    $("manifestView").textContent = JSON.stringify(state.manifest, null, 2);
  }

  function downloadJSON(obj, filename) {
    const blob = new Blob([JSON.stringify(obj, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = filename; a.click();
    URL.revokeObjectURL(url);
  }

  function importJSON(file) {
    const reader = new FileReader();
    reader.onload = function () {
      try {
        const data = JSON.parse(reader.result);
        if (data.config && data.config.n_spatial) {
          $("nSpatial").value = data.config.n_spatial;
          $("nTime").value = data.config.n_time;
          $("periodicTime").checked = !!data.config.periodic_time;
          state.geom = SpacetimeCDT.buildFlatCDT(data.config.n_spatial, data.config.n_time, !!data.config.periodic_time);
          state.manifest = data;
          renderGeometry(); updateGeomMeta(); renderManifest(); runValidationTable();
        } else {
          state.manifest = data; renderManifest();
        }
      } catch (e) {
        $("manifestView").textContent = "Import error: " + e.message;
      }
    };
    reader.readAsText(file);
  }

  function runValidationTable() {
    const tbody = $("vectorTable").querySelector("tbody");
    tbody.innerHTML = "";
    const vectors = [
      { name: "Cylinder N=4,T=3", expected: 16, actual: function () { return SpacetimeCDT.buildFlatCDT(4, 3, false).n2; } },
      { name: "Torus N=4,T=3", expected: 24, actual: function () { return SpacetimeCDT.buildFlatCDT(4, 3, true).n2; } },
      { name: "Cylinder N=3,T=2", expected: 6, actual: function () { return SpacetimeCDT.buildFlatCDT(3, 2, false).n2; } },
    ];
    vectors.forEach(function (v) {
      var actual = v.actual();
      var match = actual === v.expected;
      var tr = document.createElement("tr");
      tr.innerHTML = "<td>" + v.name + "</td><td>" + v.expected + "</td><td>" + actual +
        "</td><td class=\"" + (match ? "match-ok" : "match-fail") + "\">" + (match ? "yes" : "no") + "</td>";
      tbody.appendChild(tr);
    });
    $("validationReport").textContent = "Shared N2 test vectors";
  }

  function drawEnsemble(result) {
    var canvas = $("ensembleCanvas");
    if (!canvas || !result) return;
    var ctx = canvas.getContext("2d");
    var w = canvas.width, h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    var dsSigma = result.geometries[0] ? result.geometries[0].Ds_sigma : [];
    var mean = result.Ds_ensemble.mean;
    var lo = result.Ds_ensemble.ci95_low;
    var hi = result.Ds_ensemble.ci95_high;
    if (!dsSigma.length) return;
    var pad = { l: 48, r: 16, t: 20, b: 36 };
    var maxS = Math.max.apply(null, dsSigma);
    var vals = mean.concat(lo).concat(hi).filter(function (x) { return x !== null && isFinite(x); });
    var ymin = Math.min.apply(null, vals.concat([0]));
    var ymax = Math.max.apply(null, vals.concat([2]));
    function xMap(s) { return pad.l + (w - pad.l - pad.r) * Math.log(s) / Math.log(maxS); }
    function yMap(v) { return pad.t + (h - pad.t - pad.b) * (1 - (v - ymin) / (ymax - ymin || 1)); }
    ctx.strokeStyle = "#1e2d45";
    ctx.beginPath(); ctx.moveTo(pad.l, pad.t); ctx.lineTo(pad.l, h - pad.b); ctx.lineTo(w - pad.r, h - pad.b); ctx.stroke();
    ctx.fillStyle = "rgba(167,139,250,0.15)";
    ctx.beginPath();
    var started = false;
    for (var i = 0; i < dsSigma.length; i++) {
      if (hi[i] == null || !isFinite(hi[i])) continue;
      var x = xMap(dsSigma[i]), y = yMap(hi[i]);
      if (!started) { ctx.moveTo(x, y); started = true; } else ctx.lineTo(x, y);
    }
    for (var j = dsSigma.length - 1; j >= 0; j--) {
      if (lo[j] == null || !isFinite(lo[j])) continue;
      ctx.lineTo(xMap(dsSigma[j]), yMap(lo[j]));
    }
    ctx.closePath(); ctx.fill();
    ctx.strokeStyle = "#a78bfa"; ctx.lineWidth = 1.5; ctx.beginPath();
    started = false;
    for (var k = 0; k < dsSigma.length; k++) {
      if (mean[k] == null || !isFinite(mean[k])) continue;
      var xx = xMap(dsSigma[k]), yy = yMap(mean[k]);
      if (!started) { ctx.moveTo(xx, yy); started = true; } else ctx.lineTo(xx, yy);
    }
    ctx.stroke();
  }

  function runEnsembleUI() {
    state.ensCancel = false;
    var cfg = {
      nSpatial: Math.max(3, parseInt($("nSpatial").value, 10) || 4),
      nTime: Math.max(2, parseInt($("nTime").value, 10) || 3),
      periodicTime: $("periodicTime").checked,
      nGeometries: Math.max(1, parseInt($("ensNGeom").value, 10) || 10),
      masterSeed: parseInt($("ensSeed").value, 10) || 0,
      sigmaMax: Math.max(2, parseInt($("ensSigma").value, 10) || 20),
      nStarts: Math.max(1, parseInt($("ensStarts").value, 10) || 8),
    };
    $("ensMeta").textContent = "Running…";
    try {
      var result = SpacetimeEnsemble.runEnsemble(cfg, function (i, n) {
        $("ensMeta").textContent = "Progress " + i + " / " + n;
      }, function () { return state.ensCancel; });
      state.ensemble = result;
      state.manifest = result;
      drawEnsemble(result);
      renderManifest();
      $("ensMeta").textContent = [
        "source: browser (preview — not Python)",
        "geometries=" + result.n_geometries + " seed=" + cfg.masterSeed,
        "algorithm=" + result.config.algorithm_version,
      ].join("\n");
    } catch (e) {
      $("ensMeta").textContent = "Error: " + e.message;
    }
  }

  $("btnBuild").addEventListener("click", buildGeometry);
  $("btnDiffuse").addEventListener("click", runDiffusion);
  $("btnExport").addEventListener("click", function () {
    if (!state.geom) buildGeometry();
    downloadJSON(state.manifest || SpacetimeCDT.toManifest(state.geom), "cdt-geometry.json");
  });
  $("btnManifestExport").addEventListener("click", function () {
    if (!state.manifest) buildGeometry();
    downloadJSON(state.manifest, "spacetime-manifest.json");
  });
  $("btnImport").addEventListener("click", function () { $("fileImport").click(); });
  $("fileImport").addEventListener("change", function (e) {
    if (e.target.files && e.target.files[0]) importJSON(e.target.files[0]);
  });
  $("btnLoadSample").addEventListener("click", function () {
    $("nSpatial").value = 5; $("nTime").value = 3; buildGeometry();
  });
  ["showSpacelike", "showTimelike", "showTriangles", "showLabels"].forEach(function (id) {
    if ($(id)) $(id).addEventListener("change", renderGeometry);
  });
  if ($("btnEnsemble")) $("btnEnsemble").addEventListener("click", runEnsembleUI);
  if ($("btnCancelEns")) $("btnCancelEns").addEventListener("click", function () { state.ensCancel = true; });
  if ($("btnExportEnsJson")) $("btnExportEnsJson").addEventListener("click", function () {
    if (!state.ensemble) runEnsembleUI();
    if (state.ensemble) downloadJSON(state.ensemble, "ensemble-manifest.json");
  });
  if ($("btnExportEnsCsv")) $("btnExportEnsCsv").addEventListener("click", function () {
    if (!state.ensemble) runEnsembleUI();
    if (!state.ensemble) return;
    var blob = new Blob([SpacetimeEnsemble.csvP(state.ensemble) + "\n\n" + SpacetimeEnsemble.csvDs(state.ensemble)], { type: "text/csv" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a"); a.href = url; a.download = "ensemble-curves.csv"; a.click();
    URL.revokeObjectURL(url);
  });

  buildGeometry();
  runValidationTable();
})();
