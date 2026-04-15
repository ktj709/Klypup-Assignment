import "../styles/globals.css";

import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Klypup Research Dashboard",
  description: "Investment research dashboard with AI orchestration",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <header className="topbar">
          <div className="container topbar-content">
            <Link className="brand" href="/">
              Klypup Research
            </Link>
            <nav>
              <Link href="/reports">Reports</Link>
              <Link href="/watchlist">Watchlist</Link>
              <Link href="/admin">Admin</Link>
              <a href="/auth/login">Login</a>
              <a href="/auth/logout">Logout</a>
            </nav>
          </div>
        </header>
        <main className="container">{children}</main>
      </body>
    </html>
  );
}
