/**
 * Helpers for rendering LLM-generated content safely.
 *
 * Gemini output can be steered by user input and by retrieved Wikipedia text,
 * so every string it returns is treated as untrusted: never injected as HTML,
 * and URLs are only used when they are plain https links.
 */

export const FALLBACK_HERO_IMAGE =
  "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800";

/** Returns the URL if it is an absolute https URL, otherwise null. */
export function safeHttpsUrl(value: string | null | undefined): string | null {
  if (!value) return null;
  try {
    const url = new URL(value.trim());
    return url.protocol === "https:" ? url.toString() : null;
  } catch {
    return null;
  }
}

/** A Google Maps search link built from trusted parts, used when map_link is unsafe. */
export function mapsSearchUrl(...parts: Array<string | null | undefined>): string {
  const query = parts.filter(Boolean).join(", ");
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`;
}

export interface PopupLine {
  text: string;
  bold?: boolean;
  small?: boolean;
}

/**
 * Builds a Leaflet popup as a DOM node. Leaflet treats string popups as HTML,
 * so passing a node built with textContent is what keeps model output inert.
 */
export function buildPopupContent(lines: PopupLine[]): HTMLElement {
  const root = document.createElement("div");
  lines.forEach((line, i) => {
    if (i > 0) root.appendChild(document.createElement("br"));
    const el = document.createElement(line.bold ? "b" : "span");
    el.textContent = line.text;
    if (line.small) {
      el.style.fontSize = "10px";
      el.style.color = "#666";
    }
    root.appendChild(el);
  });
  return root;
}
