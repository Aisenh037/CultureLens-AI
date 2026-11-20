import { describe, it, expect, vi, afterEach } from "vitest";
import { render, screen, act } from "@testing-library/react";
import { LoadingIndicator } from "../components/LoadingIndicator";

afterEach(() => vi.useRealTimers());

describe("LoadingIndicator", () => {
  it("tells people how long generation takes and counts the wait", () => {
    vi.useFakeTimers();
    render(<LoadingIndicator />);
    expect(screen.getByTestId("loading-eta")).toHaveTextContent("This usually takes 1–2 minutes · 0s elapsed");
    act(() => { vi.advanceTimersByTime(3000); });
    expect(screen.getByTestId("loading-eta")).toHaveTextContent("3s elapsed");
  });
});
