"use client";

import { FormEvent, useState } from "react";

import { addReportTag, deleteReportTag, ReportDetail } from "@/lib/api";

type ReportDetailInteractiveProps = {
  accessToken: string;
  report: ReportDetail;
};

export function ReportDetailInteractive({ accessToken, report }: ReportDetailInteractiveProps) {
  const [currentReport, setCurrentReport] = useState(report);
  const [newTag, setNewTag] = useState("");
  const [isBusy, setIsBusy] = useState(false);
  const [status, setStatus] = useState("");

  async function onAddTag(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!newTag.trim()) {
      return;
    }
    setIsBusy(true);
    setStatus("");
    try {
      const updated = await addReportTag(accessToken, currentReport.id, newTag.trim());
      setCurrentReport({ ...currentReport, tags: updated.tags });
      setNewTag("");
      setStatus("Tag added.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to add tag.");
    } finally {
      setIsBusy(false);
    }
  }

  async function onDeleteTag(name: string) {
    setIsBusy(true);
    setStatus("");
    try {
      const updated = await deleteReportTag(accessToken, currentReport.id, name);
      setCurrentReport({ ...currentReport, tags: updated.tags });
      setStatus("Tag removed.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to remove tag.");
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <article className="result-card">
      <h3>{currentReport.title}</h3>
      {currentReport.summary ? <p>{currentReport.summary}</p> : null}

      <div className="tags-row">
        {currentReport.tags.length === 0 ? <span className="subtle">No tags yet</span> : null}
        {currentReport.tags.map((tag) => (
          <button
            className="tag tag-button"
            disabled={isBusy}
            key={`${currentReport.id}-${tag.name}`}
            onClick={() => onDeleteTag(tag.name)}
            type="button"
          >
            {tag.name} x
          </button>
        ))}
      </div>

      <form className="inline-form" onSubmit={onAddTag}>
        <input
          className="input"
          disabled={isBusy}
          onChange={(event) => setNewTag(event.target.value)}
          placeholder="Add tag (e.g. q3-earnings)"
          value={newTag}
        />
        <button className="button" disabled={isBusy} type="submit">
          Add Tag
        </button>
      </form>

      {status ? <p className="subtle">{status}</p> : null}

      {currentReport.sections.length === 0 ? (
        <p className="subtle">No sections were persisted for this report yet.</p>
      ) : (
        currentReport.sections.map((section) => (
          <section className="result-section" key={section.id}>
            <h4>{section.title}</h4>
            <pre>{section.body}</pre>
            {section.citations.length > 0 ? (
              <ul>
                {section.citations.map((citation) => (
                  <li key={citation.id}>
                    {citation.source_name}: {citation.reference}
                  </li>
                ))}
              </ul>
            ) : null}
          </section>
        ))
      )}
    </article>
  );
}
