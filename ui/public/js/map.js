document.addEventListener("DOMContentLoaded", () => {
  const map = L.map("map", {
    zoomControl: false,
  }).setView([42.6977, 23.3219], 13);

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
          return L.circleMarker(latlng, {
            radius: layerInfo.pointSize || 6,
            fillColor: layerInfo.color,
            color: layerInfo.color,
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
        style: {
          color: layerInfo.color,
          fillColor: layerInfo.fillColor || layerInfo.color,
          fillOpacity: layerInfo.fillOpacity || 0.4,
          weight: 2,
        },
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
    toggleDiv.className = "mb-2 flex items-center";
    toggleDiv.innerHTML = `
      <div class="w-4 h-4 mr-2" style="background-color: ${layerColor};"></div>
      <label class="inline-flex items-center">
        <input type="checkbox" id="toggle${layerName.replace(/\s+/g, "")}" class="form-checkbox" ${layersData.find((l) => l.name === layerName).visible !== false ? "checked" : ""}>
        <span class="ml-2">${layerName}</span>
      </label>
    `;
    return toggleDiv;
  }

  const layerTogglesContainer = document.getElementById("layer-toggles");

  layersData.forEach((layerInfo) => {
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
    });
  });

  const allLayers = L.featureGroup(Object.values(layers));
  map.fitBounds(allLayers.getBounds());

  window.addEventListener("resize", () => {
    map.invalidateSize();
  });

  setTimeout(() => {
    map.invalidateSize();
  }, 100);
});
