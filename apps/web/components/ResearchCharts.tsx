"use client";

import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { ResearchResponse } from "@/lib/api";

type ResearchChartsProps = {
  result: ResearchResponse;
};

const SENTIMENT_COLORS: Record<string, string> = {
  positive: "#16a34a",
  neutral: "#6b7280",
  negative: "#dc2626",
};

function getSentimentData(result: ResearchResponse) {
  const allText = result.sections.map((section) => section.body.toLowerCase()).join("\n");
  const positive = (allText.match(/\[positive\]/g) || []).length;
  const neutral = (allText.match(/\[neutral\]/g) || []).length;
  const negative = (allText.match(/\[negative\]/g) || []).length;

  return [
    { name: "positive", value: positive },
    { name: "neutral", value: neutral },
    { name: "negative", value: negative },
  ];
}

function getCitationData(result: ResearchResponse) {
  const counts = new Map<string, number>();
  for (const section of result.sections) {
    for (const citation of section.citations) {
      const key = citation.source_type || "unknown";
      counts.set(key, (counts.get(key) || 0) + 1);
    }
  }

  return Array.from(counts.entries()).map(([sourceType, count]) => ({
    sourceType,
    count,
  }));
}

export function ResearchCharts({ result }: ResearchChartsProps) {
  const sentimentData = getSentimentData(result);
  const citationData = getCitationData(result);

  return (
    <section className="chart-grid">
      <article className="chart-card">
        <h4>News Sentiment Mix</h4>
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie data={sentimentData} dataKey="value" nameKey="name" outerRadius={75}>
              {sentimentData.map((entry) => (
                <Cell key={entry.name} fill={SENTIMENT_COLORS[entry.name] || "#0f766e"} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </article>

      <article className="chart-card">
        <h4>Citations by Source Type</h4>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={citationData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="sourceType" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="count" fill="#0f766e" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </article>
    </section>
  );
}
