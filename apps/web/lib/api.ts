export type Report = {
  id: number;
  org_id: number;
  title: string;
  query_text: string;
  status: string;
  summary: string | null;
  created_at: string;
  tags: Array<{ name: string }>;
};

export type ReportCitation = {
  id: number;
  source_type: string;
  source_name: string;
  reference: string;
};

export type ReportSection = {
  id: number;
  title: string;
  body: string;
  order_index: number;
  citations: ReportCitation[];
};

export type ReportDetail = Report & {
  sections: ReportSection[];
};

export type ResearchSection = {
  title: string;
  body: string;
  citations: Array<{
    source_type: string;
    source_name: string;
    reference: string;
  }>;
};

export type ResearchResponse = {
  report_id?: number | null;
  title: string;
  executive_summary: string;
  sections: ResearchSection[];
  tools_used: string[];
};

export type WatchlistItem = {
  id: number;
  org_id: number;
  ticker: string;
  company_name: string | null;
  created_at: string;
};

export type Membership = {
  id: number;
  org_id: number;
  user_id: number;
  role: "admin" | "analyst";
};

export type OrgInvite = {
  id: number;
  org_id: number;
  code: string;
  expires_at: string | null;
  used_at: string | null;
  created_at: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

async function buildErrorMessage(prefix: string, response: Response): Promise<string> {
  let detail = "";
  try {
    const payload = await response.json();
    if (payload && typeof payload === "object" && "detail" in payload && typeof payload.detail === "string") {
      detail = payload.detail;
    }
  } catch {
    // Fall back to status-only message when response body is not JSON.
  }

  return detail ? `${prefix}: ${response.status} (${detail})` : `${prefix}: ${response.status}`;
}

export async function getReports(
  accessToken: string,
  filters?: { search?: string; tag?: string },
): Promise<Report[]> {
  const params = new URLSearchParams();
  if (filters?.search) {
    params.set("search", filters.search);
  }
  if (filters?.tag) {
    params.set("tag", filters.tag);
  }
  const query = params.toString() ? `?${params.toString()}` : "";

  const response = await fetch(`${API_BASE_URL}/reports${query}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch reports: ${response.status}`);
  }

  return response.json();
}

export async function runResearch(accessToken: string, query: string): Promise<ResearchResponse> {
  const response = await fetch(`/api/research/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error(await buildErrorMessage("Failed to run research", response));
  }

  return response.json();
}

export async function runResearchAndSave(accessToken: string, query: string): Promise<ResearchResponse> {
  const response = await fetch(`/api/research/run-and-save`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error(await buildErrorMessage("Failed to run and save research", response));
  }

  return response.json();
}

export async function createReport(
  accessToken: string,
  payload: { title: string; query_text: string; summary?: string },
): Promise<Report> {
  const response = await fetch(`${API_BASE_URL}/reports`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Failed to create report: ${response.status}`);
  }

  return response.json();
}

export async function getReportById(accessToken: string, reportId: number): Promise<ReportDetail> {
  const response = await fetch(`${API_BASE_URL}/reports/${reportId}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch report details: ${response.status}`);
  }

  return response.json();
}

export async function addReportTag(accessToken: string, reportId: number, name: string): Promise<Report> {
  const response = await fetch(
    `${API_BASE_URL}/reports/${reportId}/tags?name=${encodeURIComponent(name)}`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to add tag: ${response.status}`);
  }

  return response.json();
}

export async function deleteReportTag(accessToken: string, reportId: number, tagName: string): Promise<Report> {
  const response = await fetch(`${API_BASE_URL}/reports/${reportId}/tags/${encodeURIComponent(tagName)}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to delete tag: ${response.status}`);
  }

  return response.json();
}

export async function getWatchlist(accessToken: string): Promise<WatchlistItem[]> {
  const response = await fetch(`${API_BASE_URL}/watchlist`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch watchlist: ${response.status}`);
  }

  return response.json();
}

export async function createWatchlistItem(
  accessToken: string,
  payload: { ticker: string; company_name?: string },
): Promise<WatchlistItem> {
  const response = await fetch(`${API_BASE_URL}/watchlist`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Failed to create watchlist item: ${response.status}`);
  }

  return response.json();
}

export async function deleteWatchlistItem(accessToken: string, watchlistId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/watchlist/${watchlistId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to delete watchlist item: ${response.status}`);
  }
}

export async function getOrgMembers(accessToken: string): Promise<Membership[]> {
  const response = await fetch(`${API_BASE_URL}/orgs/members`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch members: ${response.status}`);
  }

  return response.json();
}

export async function createOrgInvite(accessToken: string): Promise<OrgInvite> {
  const response = await fetch(`${API_BASE_URL}/orgs/invites`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to create invite: ${response.status}`);
  }

  return response.json();
}
