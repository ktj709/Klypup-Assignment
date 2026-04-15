import { ReportDetail } from "@/lib/api";

type ReportDetailProps = {
  report: ReportDetail;
};

export function ReportDetailCard({ report }: ReportDetailProps) {
  return (
    <article className="result-card">
      <h3>{report.title}</h3>
      {report.summary ? <p>{report.summary}</p> : null}
      {report.sections.length === 0 ? (
        <p className="subtle">No sections were persisted for this report yet.</p>
      ) : (
        report.sections.map((section) => (
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
