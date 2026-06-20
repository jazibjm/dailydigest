// Tiny typed client for the digest API. Reads NEXT_PUBLIC_API_URL.

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface DigestSummary {
  digest_date: string;
  model: string;
}

export interface Story {
  title: string;
  url: string;
  source: string;
  score: number;
}

export interface DigestDetail {
  digest_date: string;
  model: string;
  summary: string;
  stories: Story[];
}

// Revalidate server-fetched data hourly; the pipeline only runs once a day.
const REVALIDATE = { next: { revalidate: 3600 } };

export async function listDigests(): Promise<DigestSummary[]> {
  const res = await fetch(`${API_URL}/digests`, REVALIDATE);
  if (!res.ok) throw new Error(`Failed to load digests (${res.status})`);
  return res.json();
}

export async function getDigest(date: string): Promise<DigestDetail | null> {
  const res = await fetch(`${API_URL}/digests/${date}`, REVALIDATE);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`Failed to load digest (${res.status})`);
  return res.json();
}
