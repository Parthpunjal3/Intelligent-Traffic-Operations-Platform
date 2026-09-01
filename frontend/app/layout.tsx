import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Smart City Traffic AI",
  description: "Live traffic monitoring, prediction, and signal optimization",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
