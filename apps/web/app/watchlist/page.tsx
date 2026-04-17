import { auth0 } from "@/lib/auth0";
import { type WatchlistItem, getWatchlist } from "@/lib/api";
import { WatchlistPanel } from "@/components/WatchlistPanel";

export default async function WatchlistPage() {
  const session = await auth0.getSession();

  if (!session) {
    return (
      <section>
        <h1>Watchlist</h1>
        <p>You need to sign in to manage your company watchlist.</p>
        <a className="button" href="/auth/login">
          Sign in
        </a>
      </section>
    );
  }

  let items: WatchlistItem[] = [];
  let loadError = "";

  try {
    items = await getWatchlist(session.tokenSet.accessToken);
  } catch {
    loadError = "Unable to load watchlist right now. Please retry.";
  }

  return (
    <section>
      <h1>Watchlist</h1>
      <p className="subtle">Track companies for recurring research and quick access.</p>
      {loadError ? <p className="error-text">{loadError}</p> : null}
      <WatchlistPanel accessToken={session.tokenSet.accessToken} initialItems={items} />
    </section>
  );
}
