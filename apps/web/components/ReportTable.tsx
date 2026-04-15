import { Report } from "@/lib/api";
import Link from "next/link";

type ReportTableProps = {
  reports: Report[];
};

export function ReportTable({ reports }: ReportTableProps) {
  if (reports.length === 0) {
    return <p className="empty-state">No reports yet. Create your first research query from the API.</p>;
  }

  return (
    <table className="table">
      <thead>
        <tr>
          <th>Title</th>
          <th>Tags</th>
          <th>Status</th>
          <th>Created</th>
          <th>Query</th>
          <th>View</th>
        </tr>
      </thead>
      <tbody>
        {reports.map((report) => (
          <tr key={report.id}>
            <td>{report.title}</td>
            <td>
              {report.tags.length === 0
                ? "-"
                : report.tags.map((tag) => (
                    <span className="tag" key={`${report.id}-${tag.name}`}>
                      {tag.name}
                    </span>
                  ))}
            </td>
            <td>{report.status}</td>
            <td>{new Date(report.created_at).toLocaleString()}</td>
            <td>{report.query_text}</td>
            <td>
              <Link href={`/reports?reportId=${report.id}`}>Open</Link>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
