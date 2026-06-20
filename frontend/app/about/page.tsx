import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "How it works · Daily Tech Digest",
  description:
    "The architecture behind Daily Tech Digest: how stories are gathered, summarized, stored, and served.",
};

export default function AboutPage() {
  return (
    <>
      <Link href="/" className="back">
        ← Back to digests
      </Link>

      <h1>How it works</h1>
      <p className="muted">
        Daily Tech Digest is an automated pipeline that reads the day&apos;s top
        tech stories, summarizes them with an LLM, and publishes the result
        here, to a database, and to Discord — every morning, with no manual
        input.
      </p>

      <article className="markdown">
        <h2>The daily pipeline</h2>
        <p>
          Once a day a scheduled job walks the stories through five stages. Each
          stage is an isolated module, so a failure in one source never takes
          down the whole run.
        </p>
        <ol>
          <li>
            <strong>Gather.</strong> Pluggable sources fetch the latest stories
            — the Hacker News API plus six RSS feeds (Ars Technica, TechCrunch,
            The Verge, Wired, PCMag, MIT Technology Review). Adding a feed is a
            one-line config change.
          </li>
          <li>
            <strong>Dedupe.</strong> The same article often appears on multiple
            sites. Stories are deduplicated by URL so nothing gets summarized —
            or paid for — twice.
          </li>
          <li>
            <strong>Extract.</strong> For each story, the main article text is
            pulled from the page (stripping nav, ads, and boilerplate) so the
            model summarizes the actual content, not the chrome around it.
          </li>
          <li>
            <strong>Summarize.</strong> Everything is sent to an OpenAI model in
            one pass, which writes a short overview paragraph and then groups the
            stories into topic sections (AI, Security, Hardware, and so on) as
            markdown.
          </li>
          <li>
            <strong>Store &amp; deliver.</strong> The digest and its source
            stories are saved to PostgreSQL, then posted to a Discord channel
            (split across messages to respect Discord&apos;s length limit).
          </li>
        </ol>
        <p>
          The whole run is <strong>idempotent</strong>: if today&apos;s digest
          already exists it does nothing, so re-running is always safe.
        </p>

        <h2>Serving the data</h2>
        <p>
          A small REST API (FastAPI) reads the digests back out of Postgres and
          exposes them as JSON — a list of all digests, the latest one, and any
          specific day. This website is a server-rendered Next.js app that calls
          that API and renders each digest&apos;s markdown with its source links.
        </p>

        <h2>Where it runs</h2>
        <p>
          The backend — pipeline, database, and API — lives on a Linux VPS. The
          API runs as a managed service that restarts on failure or reboot, sits
          behind nginx as a reverse proxy with an automatically-renewing HTTPS
          certificate, and the daily run is driven by cron. The frontend is
          deployed separately on Vercel&apos;s CDN, talking to the backend over
          HTTPS.
        </p>

        <h2>The stack</h2>
        <ul>
          <li>
            <strong>Backend:</strong> Python, SQLAlchemy, FastAPI, PostgreSQL
          </li>
          <li>
            <strong>Data:</strong> Hacker News API, RSS (feedparser), article
            extraction (trafilatura)
          </li>
          <li>
            <strong>Summarization:</strong> OpenAI API
          </li>
          <li>
            <strong>Frontend:</strong> Next.js (App Router), server components,
            react-markdown
          </li>
          <li>
            <strong>Ops:</strong> VPS, nginx, Let&apos;s Encrypt, systemd, cron,
            Vercel
          </li>
        </ul>
      </article>
    </>
  );
}
