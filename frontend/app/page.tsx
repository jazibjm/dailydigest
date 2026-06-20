import Link from "next/link";
import { listDigests } from "@/lib/api";

export default async function HomePage() {
  let digests;
  try {
    digests = await listDigests();
  } catch {
    return (
      <>
        <h1>Daily Tech Digest</h1>
        <p className="muted">
          Could not reach the API. Check that the backend is running and that
          NEXT_PUBLIC_API_URL is set correctly.
        </p>
      </>
    );
  }

  return (
    <>
      <h1>Daily Tech Digest</h1>
      <p className="muted">Automated daily summaries of top tech stories.</p>

      {digests.length === 0 ? (
        <p className="muted" style={{ marginTop: "1.5rem" }}>
          No digests yet. Run the pipeline to generate the first one.
        </p>
      ) : (
        <ul className="digest-list">
          {digests.map((d) => (
            <li key={d.digest_date}>
              <Link href={`/digests/${d.digest_date}`}>
                <span>{formatDate(d.digest_date)}</span>
                <span className="muted">{d.model}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}

function formatDate(iso: string): string {
  return new Date(iso + "T00:00:00").toLocaleDateString(undefined, {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}
