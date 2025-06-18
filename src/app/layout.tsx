import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "SPS-ARSYS | Self Photo Studio Appointment System",
  description:
    "An exclusive appointment reservation system for any self photo studio business",
  authors: [{ name: "Lunaxcode" }],
  keywords: [
    "appointment",
    "reservation",
    "photo studio",
    "booking",
    "self photo",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
