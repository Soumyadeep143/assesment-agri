import { fmtMonth, fmtPct, fmtPrice, pctChange, toCsv } from "../format";

describe("format helpers", () => {
  it("formats prices with Indian digit grouping and rounding", () => { expect(fmtPrice(15750)).toBe("15,750"); expect(fmtPrice(15749.6)).toBe("15,750"); });
  it("formats very large prices", () => expect(fmtPrice(1234567)).toBe("12,34,567"));
  it("formats ISO month to label", () => expect(fmtMonth("2025-10")).toBe("Oct 2025"));
  it("formats every month name", () => expect([1,2,3,4,5,6,7,8,9,10,11,12].map(m => fmtMonth(`2024-${String(m).padStart(2,"0")}`).slice(0,3)).join(" ")).toBe("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec"));
  it("returns input for malformed month", () => { expect(fmtMonth("garbage")).toBe("garbage"); expect(fmtMonth("2025-13")).toBe("2025-13"); });
  it("formats percentages with sign", () => { expect(fmtPct(1.234)).toBe("+1.2%"); expect(fmtPct(-3.04)).toBe("-3.0%"); expect(fmtPct(0)).toBe("+0.0%"); });
  it("computes pct change", () => { expect(pctChange(100, 110)).toBeCloseTo(10); expect(pctChange(200, 100)).toBeCloseTo(-50); });
  it("pct change guards divide-by-zero", () => expect(pctChange(0, 5)).toBe(0));
  it("builds CSV", () => expect(toCsv([{ a: 1, b: "x" }, { a: 2, b: "y" }])).toBe("a,b\n1,x\n2,y"));
  it("CSV of empty list is empty", () => expect(toCsv([])).toBe(""));
});
