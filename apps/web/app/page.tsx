import Link from "next/link";

export default function HomePage() {
  return (
    <section className="hero">
      <h1>Investment Research Dashboard</h1>
      <p>
        Generate source-attributed, structured company analysis using AI-powered tool orchestration.
      </p>
      <div className="hero-actions">
        <a className="button" href="/auth/login">
          Sign in with Auth0
        </a>
        <Link className="button button-secondary" href="/reports">
          View reports
        </Link>
      </div>
    </section>
  );
}
