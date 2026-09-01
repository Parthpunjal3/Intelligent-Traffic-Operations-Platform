"use client";

import { useMemo } from "react";
import { MapState } from "@/types";

const LEVEL_LABELS: Record<string, string> = {
  free_flow: "Free flow",
  moderate: "Moderate",
  heavy: "Heavy",
  gridlock: "Gridlock",
};

interface Props {
  state: MapState;
  connected: boolean;
}

export default function Dashboard({ state, connected }: Props) {
  const counts = useMemo(() => {
    const tally: Record<string, number> = { free_flow: 0, moderate: 0, heavy: 0, gridlock: 0 };
    state.congestion.forEach((c) => {
      tally[c.level] = (tally[c.level] || 0) + 1;
    });
    return tally;
  }, [state.congestion]);

  return (
    <div className="flex flex-col gap-4 p-4 h-full overflow-y-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-bold">City Traffic Overview</h1>
        <span className={`text-xs px-2 py-1 rounded-full ${connected ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
          {connected ? "Live" : "Offline"}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {Object.entries(counts).map(([level, n]) => (
          <div key={level} className="rounded-lg border p-3">
            <div className="text-2xl font-semibold">{n}</div>
            <div className="text-xs text-gray-500">{LEVEL_LABELS[level]}</div>
          </div>
        ))}
      </div>

      <div>
        <h2 className="font-semibold mb-2">Active Incidents ({state.incidents.length})</h2>
        <ul className="space-y-2">
          {state.incidents.slice(0, 10).map((incident) => (
            <li key={incident.id} className="text-sm border rounded p-2">
              <div className="font-medium capitalize">{incident.type.replace("_", " ")}</div>
              <div className="text-gray-500">{new Date(incident.detected_at).toLocaleString()}</div>
            </li>
          ))}
          {state.incidents.length === 0 && <li className="text-sm text-gray-400">No active incidents</li>}
        </ul>
      </div>

      <div>
        <h2 className="font-semibold mb-2">Cameras ({state.cameras.length})</h2>
        <ul className="space-y-1 text-sm">
          {state.cameras.map((cam) => (
            <li key={cam.id} className="text-gray-600">{cam.name}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
