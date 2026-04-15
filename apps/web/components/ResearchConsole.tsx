"use client";

import { useState } from "react";

import { createReport, ResearchResponse, runResearch } from "@/lib/api";

type ResearchConsoleProps = {
  accessToken: string;
};

export function ResearchConsole({ accessToken }: ResearchConsoleProps) {
  const [query, setQuery] = useState(
    "Analyze NVDA earnings and compare with AMD and INTC. Include recent news sentiment.",
  );
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ResearchResponse | null>(null);
  const [status, setStatus] = useState<string>("");

  async function onRunResearch() {
    setIsLoading(true);
    setStatus("");
    try {
      const response = await runResearch(accessToken, query);
      setResult(response);
      setStatus("Research completed.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Research failed.");
    } finally {
      setIsLoading(false);
    }
  }

  async function onSaveReport() {
    if (!result) {
      return;
    }

    setIsLoading(true);
    setStatus("");
    try {
      await createReport(accessToken, {
        title: result.title,
        query_text: query,
        summary: result.executive_summary,
      });
      setStatus("Report saved to your workspace.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to save report.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="panel">
      <h2>New Research Query</h2>
      <textarea
        className="textarea"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        rows={6}
      />
      <div className="hero-actions">
        <button className="button" disabled={isLoading} onClick={onRunResearch} type="button">
          {isLoading ? "Running..." : "Run Research"}
        </button>
        <button
          className="button button-secondary"
          disabled={isLoading || !result}
          onClick={onSaveReport}
          type="button"
        >
          Save Report
        </button>
      </div>
      {status ? <p className="subtle">{status}</p> : null}

      {result ? (
        <article className="result-card">
          <h3>{result.title}</h3>
          <p>{result.executive_summary}</p>
          <p className="subtle">Tools used: {result.tools_used.join(", ") || "none"}</p>
          {result.sections.map((section) => (
            <section key={section.title} className="result-section">
              <h4>{section.title}</h4>
              <pre>{section.body}</pre>
              {section.citations.length > 0 ? (
                <ul>
                  {section.citations.map((citation, index) => (
                    <li key={`${citation.reference}-${index}`}>
                      {citation.source_name}: {citation.reference}
                    </li>
                  ))}
                </ul>
              ) : null}
            </section>
          ))}
        </article>
      ) : null}
    </section>
  );
}
