import { describe, it, expect, vi } from "vitest";
import { render } from "@testing-library/react";
import { InteractiveMap } from "../components/InteractiveMap";

// Mock Leaflet globally to prevent JSDOM layout dimension errors
vi.mock("leaflet", () => {
  const mockMap = {
    setView: vi.fn().mockReturnThis(),
    addTo: vi.fn().mockReturnThis(),
    remove: vi.fn(),
    eachLayer: vi.fn(),
  };

  return {
    default: {
      map: vi.fn(() => mockMap),
      tileLayer: vi.fn(() => ({
        addTo: vi.fn(),
      })),
      marker: vi.fn(() => ({
        addTo: vi.fn().mockReturnThis(),
        bindPopup: vi.fn().mockReturnThis(),
        openPopup: vi.fn().mockReturnThis(),
      })),
      Icon: Object.assign(
        vi.fn(() => ({})),
        {
          Default: {
            prototype: {},
            mergeOptions: vi.fn()
          }
        }
      )
    },
  };
});

describe("InteractiveMap Component", () => {
  it("renders the map container correctly", () => {
    const { container } = render(
      <InteractiveMap
        lat={35.0}
        lon={135.0}
        destinationName="Kyoto"
        attractions={[]}
      />
    );
    const mapContainer = container.querySelector("#leaflet-map-element");
    expect(mapContainer).toBeInTheDocument();
  });
});
