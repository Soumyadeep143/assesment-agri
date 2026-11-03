import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import BudgetPlanner from "../components/BudgetPlanner";
import KpiCards from "../components/KpiCards";
import ForecastTable from "../components/ForecastTable";
import { buildChartRows } from "../components/ForecastChart";
import { fcPoints, history, model } from "./fixtures";

describe("buildChartRows", () => {
  it("keeps only the requested history window", () => expect(buildChartRows(history, fcPoints(12), 24).filter(r => r.price !== undefined)).toHaveLength(24));
  it("appends all forecast rows after history", () => { const r = buildChartRows(history, fcPoints(12), 24); expect(r).toHaveLength(36); expect(r[35].forecast).toBeDefined(); });
  it("joins the lines: last actual row also carries a forecast value", () => { const r = buildChartRows(history, fcPoints(3), 12); expect(r[11].forecast).toBe(r[11].price); });
  it("forecast rows carry band tuples", () => { const r = buildChartRows(history, fcPoints(3), 12); expect(r[12].band80).toHaveLength(2); expect(r[12].stress![0]).toBeLessThan(r[12].band80![0]); });
  it("handles empty history", () => expect(buildChartRows([], fcPoints(3), 12)).toHaveLength(3));
});

describe("KpiCards", () => {
  it("shows last price, central forecast, MAPE", () => {
    render(<KpiCards model={model} forecast={fcPoints(12)} stress={false} />);
    expect(screen.getByTestId("kpi-last")).toHaveTextContent("15,750"); expect(screen.getByTestId("kpi-forecast")).toHaveTextContent("15,910");
    expect(screen.getByTestId("kpi-mape")).toHaveTextContent("14.8%");
  });
  it("switches to stress range", () => {
    const { rerender } = render(<KpiCards model={model} forecast={fcPoints(12)} stress={false} />);
    const std = screen.getByTestId("kpi-range").textContent; rerender(<KpiCards model={model} forecast={fcPoints(12)} stress />);
    expect(screen.getByTestId("kpi-range").textContent).not.toBe(std); expect(screen.getByText(/Stress 80% range/)).toBeInTheDocument();
  });
});

describe("BudgetPlanner", () => {
  it("computes central budget = sum(forecast) x volume", () => {
    render(<BudgetPlanner rows={fcPoints(3)} stress={false} />);
    const sum = fcPoints(3).reduce((s, r) => s + r.forecast, 0) * 100; expect(screen.getByTestId("budget-central")).toHaveTextContent(Math.round(sum).toLocaleString("en-IN"));
  });
  it("buffer = upper - central", async () => {
    render(<BudgetPlanner rows={fcPoints(3)} stress={false} />);
    const input = screen.getByLabelText("Monthly volume"); await userEvent.clear(input); await userEvent.type(input, "10");
    const r = fcPoints(3); const buf = r.reduce((s, x) => s + (x.hi_80 - x.forecast) * 10, 0);
    expect(screen.getByTestId("budget-buffer")).toHaveTextContent(Math.round(buf).toLocaleString("en-IN"));
  });
  it("invalid / negative volume gives zero budget", async () => {
    render(<BudgetPlanner rows={fcPoints(3)} stress={false} />);
    const input = screen.getByLabelText("Monthly volume"); await userEvent.clear(input); await userEvent.type(input, "-5");
    expect(screen.getByTestId("budget-central")).toHaveTextContent("0");
  });
  it("stress upper bound is higher than standard", () => {
    const a = render(<BudgetPlanner rows={fcPoints(3)} stress={false} />); const std = a.getByTestId("budget-upper").textContent; a.unmount();
    render(<BudgetPlanner rows={fcPoints(3)} stress />); expect(screen.getByTestId("budget-upper").textContent).not.toBe(std);
  });
});

describe("ForecastTable", () => {
  it("renders one row per month plus header", () => { render(<ForecastTable rows={fcPoints(12)} stress={false} />); expect(screen.getAllByRole("row")).toHaveLength(13); });
  it("labels months readably", () => { render(<ForecastTable rows={fcPoints(12)} stress={false} />); expect(screen.getByText("Oct 2025")).toBeInTheDocument(); });
  it("stress mode changes column headings and values", () => {
    render(<ForecastTable rows={fcPoints(2)} stress />); expect(screen.getByText("Low (stress 80%)")).toBeInTheDocument();
    expect(within(screen.getAllByRole("row")[1]).getAllByRole("cell")[2]).toHaveTextContent((fcPoints(2)[0].lo_80_stress).toLocaleString("en-IN"));
  });
  it("download button triggers a CSV download", async () => {
    const url = vi.fn(() => "blob:x"); (URL as unknown as { createObjectURL: unknown }).createObjectURL = url; (URL as unknown as { revokeObjectURL: unknown }).revokeObjectURL = vi.fn();
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});
    render(<ForecastTable rows={fcPoints(3)} stress={false} />); await userEvent.click(screen.getByText("Download CSV"));
    expect(url).toHaveBeenCalled(); expect(click).toHaveBeenCalled();
  });
});
