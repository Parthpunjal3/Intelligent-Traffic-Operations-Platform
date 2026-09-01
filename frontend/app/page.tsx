"use client";

import dynamic from "next/dynamic";
import Dashboard from "@/components/Dashboard";
import { useLiveMapState } from "@/hooks/useLiveMapState";

// react-leaflet needs the DOM, so load it client-side only.
const TrafficMap = dynamic(() => import("@/components/TrafficMap"), { ssr: false });

export default function HomePage() {
  const { state, connected } = useLiveMapState();

  return (
    <main className="grid grid-cols-[380px_1fr] h-screen">
      <aside className="border-r">
        <Dashboard state={state} connected={connected} />
      </aside>
      <section className="relative">
        <TrafficMap state={state} />
      </section>
    </main>
  );
}
