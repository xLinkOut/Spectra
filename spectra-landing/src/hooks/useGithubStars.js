import { useState, useEffect } from "react";

const CACHE_KEY = "spectra_gh_stars_v1";
const CACHE_TTL = 1000 * 60 * 30; // 30 minutes

export function useGithubStars(repo = "francescogabrieli/Spectra") {
  const [stars, setStars] = useState(null);

  useEffect(() => {
    // Try cache first
    try {
      const cached = JSON.parse(sessionStorage.getItem(CACHE_KEY) || "null");
      if (cached && Date.now() - cached.ts < CACHE_TTL) {
        setStars(cached.v);
        return;
      }
    } catch {}

    fetch(`https://api.github.com/repos/${repo}`)
      .then((r) => r.json())
      .then((data) => {
        if (typeof data.stargazers_count === "number") {
          setStars(data.stargazers_count);
          try {
            sessionStorage.setItem(
              CACHE_KEY,
              JSON.stringify({ v: data.stargazers_count, ts: Date.now() })
            );
          } catch {}
        }
      })
      .catch(() => {});
  }, [repo]);

  return stars;
}

/** Format star count for display: 1200 → "1.2k" */
export function fmtStars(n) {
  if (n === null || n === undefined) return null;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return String(n);
}
