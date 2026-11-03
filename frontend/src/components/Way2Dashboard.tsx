import { useMemo, useState } from "react";
import data from "../data/way2content.json";
import type { Way2Content, Way2Page, Way2Site } from "../way2types";

const CONTENT = data as Way2Content;

export interface PageHit { site: Way2Site; page: Way2Page }

export function searchPages(sites: Way2Site[], query: string): PageHit[] {
  const q = query.trim().toLowerCase();
  const all = sites.flatMap(site => site.pages.map(page => ({ site, page })));
  if (!q) return all;
  return all.filter(({ page }) =>
    page.title.toLowerCase().includes(q) ||
    page.description.toLowerCase().includes(q) ||
    page.highlights.some(h => h.toLowerCase().includes(q))
  );
}

export default function Way2Dashboard() {
  const [siteId, setSiteId] = useState(CONTENT.sites[0].id);
  const [query, setQuery] = useState("");

  const searching = query.trim().length > 0;
  const results = useMemo(() => searchPages(CONTENT.sites, query), [query]);
  const activeSite = CONTENT.sites.find(s => s.id === siteId) ?? CONTENT.sites[0];
  const visible: PageHit[] = searching ? results : activeSite.pages.map(page => ({ site: activeSite, page }));

  return (
    <div className="way2">
      <nav className="way2-sites" aria-label="Way2 sites">
        {CONTENT.sites.map(site => (
          <button key={site.id} type="button" className={`way2-site-tab${site.id === siteId ? " active" : ""}`}
            aria-pressed={site.id === siteId} onClick={() => { setSiteId(site.id); setQuery(""); }}>
            <strong>{site.name}</strong><span>{site.role}</span>
          </button>
        ))}
      </nav>

      {!searching && (
        <section className="card way2-intro">
          <h2>{activeSite.name}</h2>
          <p className="muted">
            {activeSite.tagline} · <a href={`https://${activeSite.domain}`} target="_blank" rel="noreferrer">{activeSite.domain}</a>
          </p>
          <p>{activeSite.description}</p>
        </section>
      )}

      <div className="row-between">
        <h2>{searching ? `Search results (${visible.length})` : "Pages"}</h2>
        <input type="search" placeholder="Search all pages & highlights…" value={query}
          onChange={e => setQuery(e.target.value)} aria-label="Search Way2 ecosystem content" />
      </div>

      <div className="way2-pages">
        {visible.map(({ site, page }) => (
          <article className="card way2-page" key={page.url}>
            <div className="row-between">
              <h3><a href={page.url} target="_blank" rel="noreferrer">{page.title}</a></h3>
              {searching && <span className="muted">{site.name}</span>}
            </div>
            <p>{page.description}</p>
            {page.highlights.length > 0 && (
              <ul className="way2-highlights">
                {page.highlights.map(h => <li key={h}>{h}</li>)}
              </ul>
            )}
          </article>
        ))}
        {visible.length === 0 && <p className="muted">No matches.</p>}
      </div>

      <section className="way2-siblings">
        <h2>Related services in the group</h2>
        <div className="way2-chip-row">
          {CONTENT.siblingServices.map(s => (
            <a key={s.domain} className="way2-chip" href={`https://${s.domain}`} target="_blank" rel="noreferrer">{s.name}</a>
          ))}
        </div>
      </section>
    </div>
  );
}
