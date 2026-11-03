import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Way2Dashboard, { searchPages } from "../components/Way2Dashboard";
import way2content from "../data/way2content.json";
import type { Way2Content } from "../way2types";

const CONTENT = way2content as Way2Content;

describe("searchPages", () => {
  it("returns every page across sites when the query is empty", () => {
    const total = CONTENT.sites.reduce((n, s) => n + s.pages.length, 0);
    expect(searchPages(CONTENT.sites, "")).toHaveLength(total);
  });
  it("matches on title case-insensitively", () => {
    const hits = searchPages(CONTENT.sites, "cropintel");
    expect(hits.some(h => h.page.title === "CropIntel")).toBe(true);
  });
  it("matches inside highlights, not just title/description", () => {
    const hits = searchPages(CONTENT.sites, "patent number 574571");
    expect(hits.some(h => h.page.title === "Patent")).toBe(true);
  });
  it("returns nothing for a query that matches no page", () => {
    expect(searchPages(CONTENT.sites, "zzz-no-such-thing-zzz")).toHaveLength(0);
  });
});

describe("Way2Dashboard", () => {
  it("shows the first site's intro and pages by default", () => {
    render(<Way2Dashboard />);
    expect(screen.getByRole("heading", { name: CONTENT.sites[0].name })).toBeInTheDocument();
    expect(screen.getByText(CONTENT.sites[0].pages[0].title)).toBeInTheDocument();
  });
  it("switches site content when another site tab is clicked", async () => {
    render(<Way2Dashboard />);
    const other = CONTENT.sites[1];
    await userEvent.click(screen.getByRole("button", { name: new RegExp(other.name) }));
    expect(screen.getByRole("heading", { name: other.name })).toBeInTheDocument();
  });
  it("filters pages across all sites via the search box", async () => {
    render(<Way2Dashboard />);
    await userEvent.type(screen.getByLabelText("Search Way2 ecosystem content"), "soil test");
    expect(screen.getByText(/Search results/)).toBeInTheDocument();
    expect(screen.getByText("Soil Test")).toBeInTheDocument();
  });
  it("renders related sibling services as links", () => {
    render(<Way2Dashboard />);
    for (const s of CONTENT.siblingServices) {
      expect(screen.getByRole("link", { name: s.name })).toHaveAttribute("href", `https://${s.domain}`);
    }
  });
});
