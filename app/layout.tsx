import type { Metadata } from "next";
import type { ReactNode } from "react";
export const metadata: Metadata = { title: "EventRadar", description: "Read-only crypto event risk scanner" };
export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) { return <html lang="ko"><body>{children}</body></html>; }
