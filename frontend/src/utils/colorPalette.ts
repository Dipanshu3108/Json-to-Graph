export type Theme = "default" | "dark" | "pastel" | "vivid";

const THEME_HUES: Record<Theme, number[]> = {
  default: [211, 168, 35, 14, 280, 140],
  dark: [188, 271, 327, 60, 150, 30],
  pastel: [200, 340, 80, 160, 30, 260],
  vivid: [220, 0, 48, 120, 280, 180],
};

const THEME_SATURATION: Record<Theme, [number, number]> = {
  default: [65, 60],
  dark: [80, 75],
  pastel: [45, 55],
  vivid: [95, 90],
};

const THEME_LIGHTNESS: Record<Theme, [number, number]> = {
  default: [50, 45],
  dark: [65, 60],
  pastel: [70, 65],
  vivid: [52, 48],
};

export function generateColors(theme: Theme, count: number): string[] {
  const hues = THEME_HUES[theme];
  const [s1, s2] = THEME_SATURATION[theme];
  const [l1, l2] = THEME_LIGHTNESS[theme];

  return Array.from({ length: count }, (_, i) => {
    const hue = hues[i % hues.length];
    const s = i % 2 === 0 ? s1 : s2;
    const l = i % 2 === 0 ? l1 : l2;
    return `hsl(${hue}, ${s}%, ${l}%)`;
  });
}

export function generateFillColors(theme: Theme, count: number, opacity = 0.2): string[] {
  return generateColors(theme, count).map((hsl) => {
    const match = hsl.match(/hsl\((\d+), (\d+)%, (\d+)%\)/);
    if (!match) return hsl;
    const [, h, s, l] = match;
    return `hsla(${h}, ${s}%, ${l}%, ${opacity})`;
  });
}
