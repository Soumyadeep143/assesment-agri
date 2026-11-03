import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "../App";
import { mockFetch } from "./fixtures";

afterEach(() => vi.unstubAllGlobals());

describe("App (integration with mocked API)", () => {
  it("shows loading, then KPIs, table and planner", async () => {
    vi.stubGlobal("fetch", mockFetch()); render(<App />);
    expect(screen.getByRole("status")).toHaveTextContent(/Loading/);
    expect(await screen.findByTestId("kpi-last")).toHaveTextContent("15,750");
    expect(screen.getAllByRole("row")).toHaveLength(13); expect(screen.getByText("Budget planner")).toBeInTheDocument();
  });
  it("header shows data month and model version", async () => {
    vi.stubGlobal("fetch", mockFetch()); render(<App />);
    expect(await screen.findByText(/Data to Sep 2025 · model 2025-09-v1/)).toBeInTheDocument();
  });
  it("requests 12-month horizon by default", async () => {
    const f = mockFetch(); vi.stubGlobal("fetch", f); render(<App />); await screen.findByTestId("kpi-last");
    expect(f.mock.calls.some(c => String(c[0]).includes("horizon=12"))).toBe(true);
  });
  it("changing horizon refetches and updates table rows", async () => {
    const f = mockFetch(); vi.stubGlobal("fetch", f); render(<App />); await screen.findByTestId("kpi-last");
    await userEvent.selectOptions(screen.getByLabelText("Forecast horizon"), "6");
    await waitFor(() => expect(screen.getAllByRole("row")).toHaveLength(7));
    expect(f.mock.calls.some(c => String(c[0]).includes("horizon=6"))).toBe(true);
  });
  it("offers horizons 3, 6, 12, 24", async () => {
    vi.stubGlobal("fetch", mockFetch()); render(<App />); await screen.findByTestId("kpi-last");
    expect(Array.from((screen.getByLabelText("Forecast horizon") as HTMLSelectElement).options).map(o => o.value)).toEqual(["3", "6", "12", "24"]);
  });
  it("stress toggle changes the KPI range", async () => {
    vi.stubGlobal("fetch", mockFetch()); render(<App />); const k = await screen.findByTestId("kpi-range"); const before = k.textContent;
    await userEvent.click(screen.getByLabelText("Stress band")); expect(screen.getByTestId("kpi-range").textContent).not.toBe(before);
  });
  it("shows an error with retry when the API is down, then recovers", async () => {
    const down = mockFetch({ "/v1/forecast": new TypeError("Failed to fetch") }); vi.stubGlobal("fetch", down); render(<App />);
    expect(await screen.findByRole("alert")).toHaveTextContent(/Cannot reach/);
    vi.stubGlobal("fetch", mockFetch()); await userEvent.click(screen.getByText("Retry"));
    expect(await screen.findByTestId("kpi-last")).toBeInTheDocument(); expect(screen.queryByRole("alert")).toBeNull();
  });
  it("shows an error for server 500", async () => {
    vi.stubGlobal("fetch", mockFetch({ "/v1/model": 500 })); render(<App />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Forecast service error (500).");
  });
  it("does not render KPIs while in error state", async () => {
    vi.stubGlobal("fetch", mockFetch({ "/v1/forecast": 500 })); render(<App />); await screen.findByRole("alert"); expect(screen.queryByTestId("kpi-last")).toBeNull();
  });
  it("explains that the forecast is a band, not a direction", async () => {
    vi.stubGlobal("fetch", mockFetch()); render(<App />); expect(await screen.findByText(/central level and a risk band/)).toBeInTheDocument();
  });
  it("renders the chart container with accessible label", async () => {
    vi.stubGlobal("fetch", mockFetch()); render(<App />); expect(await screen.findByRole("img", { name: /Price history with 12-month forecast/ })).toBeInTheDocument();
  });
  it("95% toggle is off by default and can be enabled", async () => {
    vi.stubGlobal("fetch", mockFetch()); render(<App />); await screen.findByTestId("kpi-last");
    const cb = screen.getByLabelText("95% band") as HTMLInputElement; expect(cb.checked).toBe(false); await userEvent.click(cb); expect(cb.checked).toBe(true);
  });
  it("defaults to the Price Forecast tab and can switch to Way2 Ecosystem", async () => {
    vi.stubGlobal("fetch", mockFetch()); render(<App />); await screen.findByTestId("kpi-last");
    expect(screen.getByRole("button", { name: "Price Forecast" })).toHaveAttribute("aria-pressed", "true");
    await userEvent.click(screen.getByRole("button", { name: "Way2 Ecosystem" }));
    expect(screen.queryByTestId("kpi-last")).toBeNull();
    expect(screen.getByLabelText("Search Way2 ecosystem content")).toBeInTheDocument();
  });
});
