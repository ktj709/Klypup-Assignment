"use client";

import { useState } from "react";

import { createOrgInvite, Membership, OrgInvite } from "@/lib/api";

type AdminPanelProps = {
  accessToken: string;
  members: Membership[];
};

export function AdminPanel({ accessToken, members }: AdminPanelProps) {
  const [latestInvite, setLatestInvite] = useState<OrgInvite | null>(null);
  const [status, setStatus] = useState("");
  const [isBusy, setIsBusy] = useState(false);

  async function onCreateInvite() {
    setIsBusy(true);
    setStatus("");
    try {
      const invite = await createOrgInvite(accessToken);
      setLatestInvite(invite);
      setStatus("Invite code created.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Unable to create invite.");
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <section className="panel">
      <h2>Admin Workspace</h2>
      <p className="subtle">Generate invite codes and review organization members.</p>

      <button className="button" disabled={isBusy} onClick={onCreateInvite} type="button">
        {isBusy ? "Creating..." : "Create Invite Code"}
      </button>

      {latestInvite ? (
        <div className="result-card">
          <p>
            <strong>Invite Code:</strong> {latestInvite.code}
          </p>
          <p className="subtle">Expires at: {latestInvite.expires_at ? new Date(latestInvite.expires_at).toLocaleString() : "Never"}</p>
        </div>
      ) : null}

      {status ? <p className="subtle">{status}</p> : null}

      <h3>Organization Members</h3>
      {members.length === 0 ? (
        <p className="empty-state">No members found.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>User ID</th>
              <th>Role</th>
            </tr>
          </thead>
          <tbody>
            {members.map((member) => (
              <tr key={member.id}>
                <td>{member.user_id}</td>
                <td>{member.role}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
