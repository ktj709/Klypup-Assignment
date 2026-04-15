"use client";

import { FormEvent, useState } from "react";

import { createWatchlistItem, deleteWatchlistItem, WatchlistItem } from "@/lib/api";

type WatchlistPanelProps = {
  accessToken: string;
  initialItems: WatchlistItem[];
};

export function WatchlistPanel({ accessToken, initialItems }: WatchlistPanelProps) {
  const [items, setItems] = useState(initialItems);
  const [ticker, setTicker] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [isBusy, setIsBusy] = useState(false);
  const [status, setStatus] = useState("");

  async function onAdd(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!ticker.trim()) {
      return;
    }
    setIsBusy(true);
    setStatus("");
    try {
      const created = await createWatchlistItem(accessToken, {
        ticker: ticker.trim().toUpperCase(),
        company_name: companyName.trim() || undefined,
      });
      if (!items.some((item) => item.id === created.id)) {
        setItems([created, ...items]);
      }
      setTicker("");
      setCompanyName("");
      setStatus("Watchlist item added.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to add watchlist item.");
    } finally {
      setIsBusy(false);
    }
  }

  async function onDelete(watchlistId: number) {
    setIsBusy(true);
    setStatus("");
    try {
      await deleteWatchlistItem(accessToken, watchlistId);
      setItems(items.filter((item) => item.id !== watchlistId));
      setStatus("Watchlist item removed.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to remove watchlist item.");
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <section className="panel">
      <h2>Company Watchlist</h2>
      <form className="inline-form" onSubmit={onAdd}>
        <input
          className="input"
          disabled={isBusy}
          onChange={(event) => setTicker(event.target.value)}
          placeholder="Ticker (e.g. NVDA)"
          value={ticker}
        />
        <input
          className="input"
          disabled={isBusy}
          onChange={(event) => setCompanyName(event.target.value)}
          placeholder="Company name (optional)"
          value={companyName}
        />
        <button className="button" disabled={isBusy} type="submit">
          Add
        </button>
      </form>

      {status ? <p className="subtle">{status}</p> : null}

      {items.length === 0 ? (
        <p className="empty-state">No watchlist items yet.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Company</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td>{item.ticker}</td>
                <td>{item.company_name || "-"}</td>
                <td>
                  <button className="button button-secondary" onClick={() => onDelete(item.id)} type="button">
                    Remove
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
