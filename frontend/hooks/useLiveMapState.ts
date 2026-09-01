"use client";

import { useEffect, useRef, useState } from "react";
import { getMapState } from "@/lib/api";
import { MapState } from "@/types";
import { WS_URL } from "@/lib/api";

const EMPTY_STATE: MapState = { cameras: [], incidents: [], congestion: [] };

export function useLiveMapState(pollIntervalMs = 8000) {
  const [state, setState] = useState<MapState>(EMPTY_STATE);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const refresh = async () => {
    try {
      const data = await getMapState();
      setState(data);
    } catch (err) {
      console.error("Failed to fetch map state", err);
    }
  };

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, pollIntervalMs);

    try {
      const ws = new WebSocket(WS_URL);
      ws.onopen = () => setConnected(true);
      ws.onclose = () => setConnected(false);
      ws.onmessage = () => refresh(); // any push event triggers a refetch
      wsRef.current = ws;
    } catch (err) {
      console.error("WebSocket connection failed", err);
    }

    return () => {
      clearInterval(interval);
      wsRef.current?.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { state, connected, refresh };
}
