import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ThemeToggle } from "../components/ThemeToggle";

beforeEach(() => {
  // Clear dark theme class on test start
  document.documentElement.classList.remove("dark");

  // Mock localStorage
  const store: Record<string, string> = { theme: "light" };
  vi.stubGlobal("localStorage", {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => { store[key] = value; }),
    removeItem: vi.fn((key: string) => { delete store[key]; }),
    clear: vi.fn(() => { for (const k in store) delete store[k]; }),
    length: 1,
    key: vi.fn((index: number) => Object.keys(store)[index] || null),
    theme: "light"
  });

  // Mock window.matchMedia safely
  window.matchMedia = vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }));
});

describe("ThemeToggle Component", () => {
  it("renders correctly and starts in light mode by default", () => {
    render(<ThemeToggle />);
    const toggleButton = screen.getByRole("button");
    expect(toggleButton).toBeInTheDocument();
    // Default starts as light mode
    expect(toggleButton).toHaveAttribute("aria-label", "Switch to Dark Mode");
  });

  it("toggles theme and updates aria-label on click", () => {
    render(<ThemeToggle />);
    const toggleButton = screen.getByRole("button");
    
    // Toggle to Dark Mode
    fireEvent.click(toggleButton);
    expect(toggleButton).toHaveAttribute("aria-label", "Switch to Light Mode");
    expect(document.documentElement.classList.contains("dark")).toBe(true);

    // Toggle back to Light Mode
    fireEvent.click(toggleButton);
    expect(toggleButton).toHaveAttribute("aria-label", "Switch to Dark Mode");
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });
});
