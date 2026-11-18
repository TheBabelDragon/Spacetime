(function () {
  "use strict";
  const state = { geom: null, diffusion: null, manifest: null };
  const $ = (id) => document.getElementById(id);

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
      renderGeometry();
      renderManifest();
      updateGeomMeta();
      runValidationTable();
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
    const nSL = g.edges.filter((e) => e.kind === "spacelike").length;
    const nTL = g.edges.filter((e) => e.kind === "timelike").length;
    $("geomMeta").textContent = [
      "source: " + g.source + " (browser demonstration)",
      "topology: " + g.topology,
      "N=" + g.config.n_spatial + "  T=" + g.config.n_time + "  periodic_time=" + g.config.periodic_time,
      "N₀=" + g.n0 + "  N₂=" + g.n2 + "  edges=" + g.edges.length,
      "spacelike_edges=" + nSL + "  timelike_edges=" + nTL,
      "expected N₂: " + (g.config.periodic_time
        ? "2·N·T = " + (2 * g.config.n_spatial * g.config.n_time)
        : "2·N·(T-1) = " + (2 * g.config.n_spatial * (g.config.n_time - 1))),
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
    const { Ds } = SpacetimeDiffusion.spectralDimension(state.diffusion.sigma, state.diffusion.P);
    const finite = Ds.filter((x) => Number.isFinite(x));
    const meanDs = finite.length ? finite.reduce((a, b) => a + b, 0) / finite.length : NaN;
    SpacetimeDiffusion.drawSpectral($("spectralCanvas"), state.diffusion);
    $("spectralMeta").textContent = [
      "source: browser · graph: primal (not dual)",
      "σ_max=" + sigmaMax + "  starts=" + state.diffusion.n_starts + "  seed=" + seed,
      "⟨Ds⟩ diagnostic = " + (Number.isFinite(meanDs) ? meanDs.toFixed(3) : "n/a"),
      "Note: finite-size RW estimates; not continuum spectral dimension.",
    ].join("\n");
    if (state.manifest) {
      state.manifest.spectral_demo = {
        source: "browser", graph: "primal", sigma_max: sigmaMax,
        mean_Ds_diagnostic: meanDs, seed,
      };
      renderManifest();
    }
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
        const source = data.source || "unknown";
        if (data.config && data.config.n_spatial) {
          $("nSpatial").value = data.config.n_spatial;
          $("nTime").value = data.config.n_time;
          $("periodicTime").checked = !!data.config.periodic_time;
          state.geom = SpacetimeCDT.buildFlatCDT(
            data.config.n_spatial, data.config.n_time, !!data.config.periodic_time
          );
          state.geom.source = source === "python" ? "python-import-geometry-rebuild" : source;
          state.manifest = Object.assign({}, data, {
            imported_at: new Date().toISOString(),
            import_note: source === "python"
              ? "Geometry rebuilt in browser from config; not a bit-identical Python snapshot."
              : "Imported manifest",
          });
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
      { name: "Cylinder N=4,T=3 → N₂", expected: 16, actual: () => SpacetimeCDT.buildFlatCDT(4, 3, false).n2 },
      { name: "Torus N=4,T=3 → N₂", expected: 24, actual: () => SpacetimeCDT.buildFlatCDT(4, 3, true).n2 },
      { name: "Cylinder N=3,T=2 → N₂", expected: 6, actual: () => SpacetimeCDT.buildFlatCDT(3, 2, false).n2 },
      { name: "Torus−Cylinder ΔN₂ (N=5,T=4)", expected: 10, actual: () => {
          return SpacetimeCDT.buildFlatCDT(5, 4, true).n2 - SpacetimeCDT.buildFlatCDT(5, 4, false).n2;
        }},
    ];
    const lines = ["Shared test vectors (browser vs convention):"];
    for (const v of vectors) {
      let actual, match;
      try { actual = v.actual(); match = actual === v.expected; }
      catch (e) { actual = e.message; match = false; }
      const tr = document.createElement("tr");
      tr.innerHTML = "<td>" + v.name + "</td><td>" + v.expected + "</td><td>" + actual +
        "</td><td class=\"" + (match ? "match-ok" : "match-fail") + "\">" + (match ? "yes" : "no") + "</td>";
      tbody.appendChild(tr);
      lines.push(v.name + ": expected=" + v.expected + " actual=" + actual + " match=" + match);
    }
    $("validationReport").textContent = lines.join("\n");
  }

  function loadSample() {
    $("nSpatial").value = 5; $("nTime").value = 3; $("periodicTime").checked = false;
    buildGeometry();
    $("sigmaMax").value = 30; $("nStarts").value = 20; $("diffSeed").value = 7;
    runDiffusion();
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
  $("btnLoadSample").addEventListener("click", loadSample);
  ["showSpacelike", "showTimelike", "showTriangles", "showLabels"].forEach(function (id) {
    $(id).addEventListener("change", renderGeometry);
  });

  buildGeometry();
  runValidationTable();
})();
