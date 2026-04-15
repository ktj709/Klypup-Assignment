import Link from "next/link";

import { ResearchConsole } from "@/components/ResearchConsole";
import { auth0 } from "@/lib/auth0";
import { getReports, getWatchlist } from "@/lib/api";

export default async function HomePage() {
  const session = await auth0.getSession();
  const accessToken = session?.tokenSet.accessToken;

  let recentReports = [];
  let watchlist = [];
  if (accessToken) {
    try {
      recentReports = await getReports(accessToken);
      watchlist = await getWatchlist(accessToken);
    } catch {
      // Keep dashboard resilient even if backend or provider is temporarily unavailable.
      recentReports = [];
      watchlist = [];
    }
  }

  return (
    <>
      <section className="hero">
        <h1>Investment Research Dashboard</h1>
        <p>
          Generate source-attributed, structured company analysis using AI-powered tool orchestration.
        </p>
        <div className="hero-actions">
          {!session ? (
            <a className="button" href="/auth/login">
              Sign in with Auth0
            </a>
          ) : null}
          <Link className="button button-secondary" href="/watchlist">
            Open watchlist
          </Link>
          <Link className="button button-secondary" href="/reports">
            View reports
          </Link>
        </div>
      </section>
      {session ? (
        <section className="dashboard-grid">
          <article className="dashboard-card">
            <h3>Recent Research</h3>
            {recentReports.length === 0 ? (
              <p className="empty-state">No saved reports yet.</p>
            ) : (
              <ul>
                {recentReports.slice(0, 5).map((report) => (
                  <li key={report.id}>
                    <Link href={`/reports?reportId=${report.id}`}>{report.title}</Link>
                  </li>
                ))}
              </ul>
            )}
          </article>

          <article className="dashboard-card">
            <h3>Bookmarked Companies</h3>
            {watchlist.length === 0 ? (
              <p className="empty-state">No companies in watchlist.</p>
            ) : (
              <ul>
                {watchlist.slice(0, 8).map((item) => (
                  <li key={item.id}>
                    <strong>{item.ticker}</strong> {item.company_name ? `- ${item.company_name}` : ""}
                  </li>
                ))}
              </ul>
            )}
          </article>

          <article className="dashboard-card">
            <h3>Quick Actions</h3>
            <div className="quick-actions">
              <Link className="button" href="/reports">
                New Research
              </Link>
              <Link className="button button-secondary" href="/reports?q=compare">
                Compare Companies
              </Link>
              <Link className="button button-secondary" href="/watchlist">
                Manage Watchlist
              </Link>
            </div>
          </article>
        </section>
      ) : null}
      {session ? <ResearchConsole accessToken={session.tokenSet.accessToken} /> : null}
    </>
  );
}
