import React, { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { AttractionItem } from "../types/travel";

// Solve default Leaflet icon loading bug in Vite/Webpack builds
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

interface InteractiveMapProps {
  lat: number;
  lon: number;
  destinationName: string;
  attractions: AttractionItem[];
}

export const InteractiveMap: React.FC<InteractiveMapProps> = ({
  lat,
  lon,
  destinationName,
  attractions,
}) => {
  const mapRef = useRef<L.Map | null>(null);
  const containerId = "leaflet-map-element";

  // 1. Initialize map once on mount
  useEffect(() => {
    mapRef.current = L.map(containerId).setView([lat, lon], 12);
    
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(mapRef.current);

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []); // Run ONLY once on mount

  // 2. Update map view and markers when props change
  useEffect(() => {
    if (!mapRef.current) return;
    const mapInstance = mapRef.current;

    // Pan/zoom view to new coordinates
    mapInstance.setView([lat, lon], 12);

    // Remove existing markers before rendering new ones
    mapInstance.eachLayer((layer) => {
      if (layer instanceof L.Marker) {
        mapInstance.removeLayer(layer);
      }
    });

    // Create a special green icon for the center point
    const centerIcon = new L.Icon({
      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41]
    });

    // Add center marker
    L.marker([lat, lon], { icon: centerIcon }).addTo(mapInstance)
      .bindPopup(`<b>📍 Center: ${destinationName}</b><br/>Latitude: ${lat}<br/>Longitude: ${lon}`)
      .openPopup();

    // Add markers for each attraction
    attractions.forEach((attr) => {
      if (attr.latitude && attr.longitude) {
        L.marker([attr.latitude, attr.longitude]).addTo(mapInstance)
          .bindPopup(`<b>🏛️ ${attr.name}</b><br/>${attr.location}<br/><span style="font-size:10px; color:#666;">Cost: ${attr.estimated_cost}</span>`);
      }
    });
  }, [lat, lon, attractions, destinationName]);


  return (
    <div className="backdrop-blur-xl bg-slate-900/60 border border-slate-800/80 rounded-3xl p-5 shadow-xl text-slate-100 flex flex-col gap-4">
      <div className="flex flex-col gap-1 border-b border-slate-800/60 pb-3">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">🗺️ Interactive Culture Map</h3>
        <p className="text-xs text-slate-400">Factual OpenStreetMap geolocations of attractions.</p>
      </div>
      <div 
        id={containerId} 
        role="region"
        aria-label={`Interactive map of ${destinationName} showing local attractions`}
        className="h-[350px] w-full rounded-2xl border border-slate-800 bg-slate-950 z-10"
      />
    </div>
  );
};
export default InteractiveMap;
