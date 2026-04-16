import { auth0 } from "@/lib/auth0";
import { getReportById, getReports } from "@/lib/api";
import { ReportDetailInteractive } from "@/components/ReportDetailInteractive";
import { ReportTable } from "@/components/ReportTable";

export default async function ReportsPage({
  searchParams,
}: {
  searchParams: Promise<{ reportId?: string; q?: string; tag?: string }>;
}) {
  const session = await auth0.getSession();
  const params = await searchParams;

  if (!session) {
    return (
      <section>
        <h1>Reports</h1>
        <p>You need to sign in to view tenant-scoped reports.</p>
        <a className="button" href="/auth/login">
          Sign in
        </a>
      </section>
    );
  }

  let reports = [];
  let latestReport = null;
  let loadError = "";

  try {
    reports = await getReports(session.tokenSet.accessToken, {
      search: params.q,
      tag: params.tag,
    });
    const selectedId = params.reportId ? Number(params.reportId) : reports[0]?.id;
    latestReport = selectedId ? await getReportById(session.tokenSet.accessToken, selectedId) : null;
  } catch {
    loadError = "Unable to load reports right now. Please retry in a moment.";
  }

  return (
    <section>
      <h1>Research reports</h1>
      <p className="subtle">Data is scoped by organization through backend tenant middleware.</p>
      <form className="inline-form" method="get">
        <input className="input" defaultValue={params.q || ""} name="q" placeholder="Search title or query" />
        <input className="input" defaultValue={params.tag || ""} name="tag" placeholder="Filter by tag" />
        <button className="button" type="submit">
          Apply Filters
        </button>
      </form>
      {loadError ? <p className="error-text">{loadError}</p> : null}
      <ReportTable reports={reports} />
      {latestReport ? (
        <>
          <h2>Selected report details</h2>
          <ReportDetailInteractive accessToken={session.tokenSet.accessToken} report={latestReport} />
        </>
      ) : null}
    </section>
  );
}
