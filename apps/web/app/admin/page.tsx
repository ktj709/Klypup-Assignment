import { auth0 } from "@/lib/auth0";
import { getOrgMembers } from "@/lib/api";
import { AdminPanel } from "@/components/AdminPanel";

export default async function AdminPage() {
  const session = await auth0.getSession();

  if (!session) {
    return (
      <section>
        <h1>Admin</h1>
        <p>You need to sign in to access admin features.</p>
        <a className="button" href="/auth/login">
          Sign in
        </a>
      </section>
    );
  }

  let members = [];
  try {
    members = await getOrgMembers(session.tokenSet.accessToken);
  } catch {
    return (
      <section>
        <h1>Admin</h1>
        <p className="subtle">Your account is likely not an admin in this organization.</p>
      </section>
    );
  }

  return (
    <section>
      <h1>Admin</h1>
      <AdminPanel accessToken={session.tokenSet.accessToken} members={members} />
    </section>
  );
}
