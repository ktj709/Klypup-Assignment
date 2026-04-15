import { auth0 } from "@/lib/auth0";
import { getReports } from "@/lib/api";
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

  return (
    <section>
      <h1>Research reports</h1>
      <p className="subtle">Data is scoped by organization through backend tenant middleware.</p>
      <ReportTable reports={reports} />
    </section>
  );
}
