import type { Metadata } from "next";
import { Analytics } from "@vercel/analytics/next";
import { SpeedInsights } from "@vercel/speed-insights/next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Daily Tech Digest",
  description: "An automated daily summary of top tech stories.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <main>
          {children}
          <footer className="site-footer">
            <a href="/">Home</a>
            <span aria-hidden="true">·</span>
            <a href="/about">How it works</a>
          </footer>
        </main>
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}
