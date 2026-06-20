import type { Metadata } from "next";
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
        <main>{children}</main>
      </body>
    </html>
  );
}
