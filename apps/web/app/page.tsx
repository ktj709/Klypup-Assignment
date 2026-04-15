import Link from "next/link";

import { ResearchConsole } from "@/components/ResearchConsole";
import { auth0 } from "@/lib/auth0";

export default async function HomePage() {
  const session = await auth0.getSession();

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
          <Link className="button button-secondary" href="/reports">
            View reports
          </Link>
        </div>
      </section>
      {session ? <ResearchConsole accessToken={session.tokenSet.accessToken} /> : null}
    </>
  );
}
