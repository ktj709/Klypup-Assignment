export type Report = {
  id: number;
  org_id: number;
  title: string;
  query_text: string;
  status: string;
  summary: string | null;
  created_at: string;
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
  title: string;
  executive_summary: string;
  sections: ResearchSection[];
  tools_used: string[];
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export async function getReports(accessToken: string): Promise<Report[]> {
  const response = await fetch(`${API_BASE_URL}/reports`, {
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
  const response = await fetch(`${API_BASE_URL}/research/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error(`Failed to run research: ${response.status}`);
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
