export type Report = {
  id: number;
  org_id: number;
  title: string;
  query_text: string;
  status: string;
  summary: string | null;
  created_at: string;
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
