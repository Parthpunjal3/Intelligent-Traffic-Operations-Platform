import axios from "axios";

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
export const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/live";

const api = axios.create({ baseURL: API_URL, timeout: 10000 });

export const getMapState = () => api.get("/map/state").then((r) => r.data);
export const getIncidents = () => api.get("/incidents").then((r) => r.data);
export const generatePrediction = (cameraId: string) =>
  api.post(`/predictions/${cameraId}/generate`).then((r) => r.data);
export const recommendSignal = (intersectionId: string) =>
  api.post(`/signals/${intersectionId}/recommend`).then((r) => r.data);
export const getCongestionHistory = (cameraId: string, hours = 1) =>
  api.get(`/congestion/${cameraId}`, { params: { hours } }).then((r) => r.data);

export default api;
