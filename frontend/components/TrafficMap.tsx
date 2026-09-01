"use client";

import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { MapState } from "@/types";

const LEVEL_COLORS: Record<string, string> = {
  free_flow: "#22c55e",
  moderate: "#eab308",
  heavy: "#f97316",
  gridlock: "#dc2626",
};

const INCIDENT_COLOR = "#7c3aed";

interface Props {
  state: MapState;
  center?: [number, number];
}

export default function TrafficMap({ state, center = [22.3039, 70.8022] }: Props) {
  const congestionByCam = Object.fromEntries(state.congestion.map((c) => [c.camera_id, c]));

  return (
    <MapContainer center={center} zoom={13} style={{ height: "100%", width: "100%" }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
      />

      {state.cameras.map((cam) => {
        const congestion = congestionByCam[cam.id];
        const color = congestion ? LEVEL_COLORS[congestion.level] || "#3b82f6" : "#3b82f6";
        return (
          <CircleMarker key={cam.id} center={[cam.lat, cam.lng]} radius={9} pathOptions={{ color, fillColor: color, fillOpacity: 0.8 }}>
            <Popup>
              <div className="text-sm">
                <div className="font-semibold">{cam.name}</div>
                {congestion ? (
                  <>
                    <div>Level: {congestion.level}</div>
                    <div>Density: {congestion.density.toFixed(0)} veh/min</div>
                  </>
                ) : (
                  <div>No data yet</div>
                )}
              </div>
            </Popup>
          </CircleMarker>
        );
      })}

      {state.incidents
        .filter((i) => i.lat != null && i.lng != null)
        .map((incident) => (
          <CircleMarker
            key={incident.id}
            center={[incident.lat as number, incident.lng as number]}
            radius={11}
            pathOptions={{ color: INCIDENT_COLOR, fillColor: INCIDENT_COLOR, fillOpacity: 0.9 }}
          >
            <Popup>
              <div className="text-sm">
                <div className="font-semibold capitalize">{incident.type.replace("_", " ")}</div>
                <div>Confidence: {(incident.confidence * 100).toFixed(0)}%</div>
                <div>{new Date(incident.detected_at).toLocaleTimeString()}</div>
              </div>
            </Popup>
          </CircleMarker>
        ))}
    </MapContainer>
  );
}
