import { auth0 } from "@/lib/auth0";
import { getReportById, getReports } from "@/lib/api";
import { ReportDetailCard } from "@/components/ReportDetail";
import { ReportTable } from "@/components/ReportTable";

export default async function ReportsPage() {
  const session = await auth0.getSession();

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

  const reports = await getReports(session.tokenSet.accessToken);
  const latestReport = reports.length > 0 ? await getReportById(session.tokenSet.accessToken, reports[0].id) : null;

  return (
    <section>
      <h1>Research reports</h1>
      <p className="subtle">Data is scoped by organization through backend tenant middleware.</p>
      <ReportTable reports={reports} />
      {latestReport ? (
        <>
          <h2>Latest report details</h2>
          <ReportDetailCard report={latestReport} />
        </>
      ) : null}
    </section>
  );
}
