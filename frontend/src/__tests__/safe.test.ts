import { describe, it, expect } from "vitest";
import { buildPopupContent, mapsSearchUrl, safeHttpsUrl } from "../utils/safe";

describe("safeHttpsUrl", () => {
  it("accepts plain https URLs", () => {
    expect(safeHttpsUrl("https://maps.google.com/?q=Kinkaku-ji")).toBe("https://maps.google.com/?q=Kinkaku-ji");
  });

  it.each([
    "javascript:alert(document.cookie)",
    " JavaScript:alert(1)",
    "data:text/html,<script>alert(1)</script>",
    "http://insecure.example/img.jpg",
    "/relative/path",
    "",
    null,
    undefined,
  ])("rejects %s", (value) => {
    expect(safeHttpsUrl(value as string | null | undefined)).toBeNull();
  });
});

describe("mapsSearchUrl", () => {
  it("encodes the query", () => {
    expect(mapsSearchUrl("Kinkaku-ji", "Kita Ward")).toBe(
      "https://www.google.com/maps/search/?api=1&query=Kinkaku-ji%2C%20Kita%20Ward"
    );
  });
});

describe("buildPopupContent", () => {
  it("renders model output as text, never as HTML", () => {
    const payload = '<img src=x onerror="window.__xss=1">';
    const node = buildPopupContent([{ text: payload, bold: true }, { text: "Gion" }]);
    expect(node.querySelector("img")).toBeNull();
    expect(node.textContent).toContain(payload);
    expect((window as any).__xss).toBeUndefined();
  });
});
