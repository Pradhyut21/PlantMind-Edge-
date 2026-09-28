import type { Metadata, Viewport } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'PlantMind Edge — Offline Industrial Knowledge Continuity',
  description:
    'Offline-first industrial knowledge-continuity platform where factory-floor technicians search and update maintenance knowledge locally via Qdrant Edge, with intelligent, conflict-aware sync to central Qdrant Server.',
  manifest: '/manifest.json',
};

export const viewport: Viewport = {
  themeColor: '#FF7B00',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="manifest" href="/manifest.json" />
      </head>
      <body>{children}</body>
    </html>
  );
}
