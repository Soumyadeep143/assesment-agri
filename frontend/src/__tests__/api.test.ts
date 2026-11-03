import { ApiError, API_URL, fetchForecast, fetchHistory, fetchModel } from "../api";
import { forecastResp, mockFetch, model } from "./fixtures";

afterEach(() => vi.unstubAllGlobals());

describe("api client", () => {
  it("calls /v1/forecast with the horizon query param", async () => {
    const f = mockFetch(); vi.stubGlobal("fetch", f);
    const r = await fetchForecast(6); expect(r.forecast).toHaveLength(6);
    expect(f.mock.calls[0][0]).toBe(`${API_URL}/v1/forecast?horizon=6`);
  });
  it("calls /v1/history and /v1/model", async () => {
    const f = mockFetch(); vi.stubGlobal("fetch", f);
    expect((await fetchHistory(120)).points.length).toBeGreaterThan(0); expect(await fetchModel()).toEqual(model);
    expect(f.mock.calls[0][0]).toContain("/v1/history?months=120"); expect(f.mock.calls[1][0]).toContain("/v1/model");
  });
  it("sends auth headers object (empty in dev)", async () => {
    const f = mockFetch(); vi.stubGlobal("fetch", f); await fetchModel(); expect(f.mock.calls[0][1]).toHaveProperty("headers");
  });
  it("maps 422 to a friendly error", async () => {
    vi.stubGlobal("fetch", mockFetch({ "/v1/forecast": 422 }));
    await expect(fetchForecast(99)).rejects.toMatchObject({ status: 422, message: "Invalid request parameters." });
  });
  it("maps 500 to a service error", async () => {
    vi.stubGlobal("fetch", mockFetch({ "/v1/forecast": 500 }));
    await expect(fetchForecast(12)).rejects.toThrow("Forecast service error (500).");
  });
  it("maps network failure to a reachability message", async () => {
    vi.stubGlobal("fetch", mockFetch({ "/v1/forecast": new TypeError("Failed to fetch") }));
    const e = await fetchForecast(12).catch(x => x); expect(e).toBeInstanceOf(ApiError); expect(e.status).toBe(0); expect(e.message).toMatch(/Cannot reach/);
  });
  it("re-throws AbortError untouched", async () => {
    const abort = Object.assign(new Error("aborted"), { name: "AbortError" });
    vi.stubGlobal("fetch", mockFetch({ "/v1/forecast": abort }));
    await expect(fetchForecast(12)).rejects.toMatchObject({ name: "AbortError" });
  });
  it("returns parsed JSON payload unchanged", async () => {
    vi.stubGlobal("fetch", mockFetch({ "/v1/forecast": forecastResp(2) })); expect((await fetchForecast(2)).forecast[1].month).toBe("2025-11");
  });
});
