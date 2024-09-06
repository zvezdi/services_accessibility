// Utility functions for color interpolation and gradient calculation

function colorToHex(colorName) {
  const colorMap = {
    maroon: "#800000",
    chocolate: "#d2691e",
    orange: "#ffa500",
    gold: "#ffd700",
    yellowgreen: "#9acd32",
    forestgreen: "#228b22",
    darkgreen: "#006400",
  };
  return colorMap[colorName.toLowerCase()] || colorName;
}

function interpolateColor(startColor, endColor, t) {
  const startRgb = hexToRgb(startColor);
  const endRgb = hexToRgb(endColor);

  const r = Math.round(startRgb.r + (endRgb.r - startRgb.r) * t);
  const g = Math.round(startRgb.g + (endRgb.g - startRgb.g) * t);
  const b = Math.round(startRgb.b + (endRgb.b - startRgb.b) * t);

  return `rgb(${r}, ${g}, ${b})`;
}

function hexToRgb(hex) {
  const bigint = Number.parseInt(hex.replace("#", ""), 16);
  return {
    r: (bigint >> 16) & 255,
    g: (bigint >> 8) & 255,
    b: bigint & 255,
  };
}

function colorFor(value, colors) {
  const scaledValue = (value * (colors.length - 1)) / 100.0;
  const index = Math.floor(scaledValue);
  const t = scaledValue - index;

  const startColor = colorToHex(colors[index]);
  const endColor = colorToHex(colors[index + 1] || colors[index]);

  return interpolateColor(startColor, endColor, t);
}
