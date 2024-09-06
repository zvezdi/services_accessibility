document.addEventListener("DOMContentLoaded", () => {
  const map = L.map("map", {
    zoomControl: false,
  }).setView([42.6977, 23.3219], 15);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  L.control
    .zoom({
      position: "topleft",
    })
    .addTo(map);

  const layers = {};

  function getColor(layerInfo, feature) {
    if (
      layerInfo.getColorForFeature &&
      typeof layerInfo.getColorForFeature === "function"
    ) {
      return layerInfo.getColorForFeature(feature);
    }

    if (layerInfo.color) {
      return layerInfo.color;
    }

    return "black";
  }

  function createLayer(layerInfo) {
    let layer;
    if (layerInfo.type === "line") {
      layer = L.geoJSON(layerInfo.data, {
        style: {
          color: layerInfo.color,
          weight: 3,
        },
        onEachFeature: (feature, featureLayer) => {
          if (feature.properties) {
            featureLayer.bindPopup(createPopupContent(feature.properties));
          }
        },
      });
    } else if (layerInfo.type === "point") {
      layer = L.geoJSON(layerInfo.data, {
        pointToLayer: (feature, latlng) => {
          const computed_color = getColor(layerInfo, feature);
          return L.circleMarker(latlng, {
            radius: layerInfo.pointSize || 6,
            fillColor: computed_color,
            color: computed_color,
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8,
          });
        },
        onEachFeature: (feature, featureLayer) => {
          if (feature.properties) {
            featureLayer.bindPopup(createPopupContent(feature.properties));
          }
        },
      });
    } else if (layerInfo.type === "polygon") {
      layer = L.geoJSON(layerInfo.data, {
        style: (feature) => ({
          color: getColor(layerInfo, feature),
          fillColor: getColor(layerInfo, feature),
          fillOpacity: layerInfo.fillOpacity || 0.4,
          weight: 2,
        }),
        onEachFeature: (feature, featureLayer) => {
          if (feature.properties) {
            featureLayer.bindPopup(createPopupContent(feature.properties));
          }
        },
      });
    }

    if (layerInfo.visible === undefined || layerInfo.visible) {
      layer.addTo(map);
    }

    return layer;
  }

  function createPopupContent(properties) {
    return Object.entries(properties)
      .map(([key, value]) => `<strong>${key}:</strong> ${value}`)
      .join("<br>");
  }

  function createToggle(layerName, layerColor) {
    const toggleDiv = document.createElement("div");
    toggleDiv.className = "flex items-center mb-2";
    toggleDiv.innerHTML = `
    <label class="inline-flex items-center">
      <input type="checkbox" id="toggle${layerName.replace(/\s+/g, "")}" class="form-checkbox" ${layersData.find((l) => l.name === layerName).visible !== false ? "checked" : ""}>
      <span class="ml-2">${layerName}</span>
    </label>
    <div class="w-4 h-4 ml-2" style="background-color: ${layerColor};"></div>
    `;
    return toggleDiv;
  }

  function fitToVisibleLayers(map, layers) {
    const visibleLayers = [];

    for (const layerName of Object.keys(layers)) {
      const layer = layers[layerName];

      if (map.hasLayer(layer)) {
        visibleLayers.push(layer);
      }
    }

    if (visibleLayers.length > 0) {
      const visibleGroup = L.featureGroup(visibleLayers);
      map.fitBounds(visibleGroup.getBounds());
    }
  }

  const layerTogglesContainer = document.getElementById("layer-toggles");

  for (const layerInfo of layersData) {
    const layer = createLayer(layerInfo);
    layers[layerInfo.name] = layer;

    const toggle = createToggle(layerInfo.name, layerInfo.color);
    layerTogglesContainer.appendChild(toggle);

    const toggleCheckbox = toggle.querySelector('input[type="checkbox"]');
    toggleCheckbox.addEventListener("change", (e) => {
      if (e.target.checked) {
        layer.addTo(map);
      } else {
        map.removeLayer(layer);
      }

      fitToVisibleLayers(map, layers);
    });
  }

  const allLayers = L.featureGroup(Object.values(layers));
  map.fitBounds(allLayers.getBounds());

  window.addEventListener("resize", () => {
    map.invalidateSize();
  });

  setTimeout(() => {
    map.invalidateSize();
  }, 100);

  // Legend logic
  if (typeof showLegend !== "undefined" && showLegend) {
    const legendHtml = document.createElement("div");
    legendHtml.innerHTML = legendHtmlContent; // Legend HTML comes from erb config
    document.body.appendChild(legendHtml);
  }
});
