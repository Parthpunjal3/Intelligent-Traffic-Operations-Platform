export interface Camera {
  id: string;
  name: string;
  lat: number;
  lng: number;
}

export interface Incident {
  id: string;
  type: string;
  lat: number | null;
  lng: number | null;
  detected_at: string;
  confidence: number;
}

export interface CongestionReading {
  camera_id: string;
  level: "free_flow" | "moderate" | "heavy" | "gridlock";
  density: number;
  timestamp: string;
}

export interface MapState {
  cameras: Camera[];
  incidents: Incident[];
  congestion: CongestionReading[];
}

export interface PredictionPoint {
  target_timestamp: string;
  predicted_count: number;
  predicted_level: string;
  confidence: number;
}
