"use client";

export default function RootError({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <section className="panel">
      <h2>Something went wrong</h2>
      <p className="subtle">The page failed to load. Please try again.</p>
      <button className="button" onClick={() => reset()} type="button">
        Retry
      </button>
    </section>
  );
}
