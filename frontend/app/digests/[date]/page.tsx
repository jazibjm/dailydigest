import Link from "next/link";
import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getDigest } from "@/lib/api";

export default async function DigestPage({
  params,
}: {
  params: { date: string };
}) {
  const digest = await getDigest(params.date);
  if (!digest) notFound();

  return (
    <>
      <Link href="/" className="back">
        ← All digests
      </Link>

      <h1>{formatDate(digest.digest_date)}</h1>
      <p className="muted">Summarized by {digest.model}</p>

      <article className="markdown">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {digest.summary}
        </ReactMarkdown>
      </article>

      {digest.stories.length > 0 && (
        <section className="sources">
          <h3>Sources</h3>
          <ul>
            {digest.stories.map((s) => (
              <li key={s.url}>
                <a href={s.url} target="_blank" rel="noopener noreferrer">
                  {s.title}
                </a>
                <span className="tag">
                  {s.source}
                  {s.score > 0 ? ` · ${s.score}` : ""}
                </span>
              </li>
            ))}
          </ul>
        </section>
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
