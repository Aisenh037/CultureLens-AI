import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { act, render, screen, fireEvent } from "@testing-library/react";
import { FeedbackCard } from "../components/FeedbackCard";
import { InstallButton } from "../components/InstallButton";

const fetchMock = vi.fn();
const sent = () => JSON.parse((fetchMock.mock.calls[0][1] as RequestInit).body as string);

beforeEach(() => {
  fetchMock.mockReset();
  fetchMock.mockResolvedValue(new Response(JSON.stringify({ status: "ok" }), { status: 201 }));
  vi.stubGlobal("fetch", fetchMock);
  localStorage.clear();
});
afterEach(() => vi.unstubAllGlobals());

describe("FeedbackCard", () => {
  it("asks first, and shows the details form only after a thumb", () => {
    render(<FeedbackCard destination="Kyoto" />);
    expect(screen.getByText(/was this itinerary useful/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /send feedback/i })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /not really/i }));
    expect(screen.getByText(/what was missing or wrong/i)).toBeInTheDocument();
  });

  it("sends a bare thumbs-up with the destination", async () => {
    render(<FeedbackCard destination="Kyoto" />);
    fireEvent.click(screen.getByRole("button", { name: /yes/i }));
    fireEvent.click(screen.getByRole("button", { name: /send feedback/i }));
    expect(await screen.findByText(/thank you/i)).toBeInTheDocument();
    expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/feedback$/);
    expect(sent()).toMatchObject({ kind: "itinerary", helpful: true, destination: "Kyoto", can_quote: false });
    expect(sent().comment).toBeUndefined();
  });

  it("sends the comment, name and quote consent", async () => {
    render(<FeedbackCard destination="Jaipur" />);
    fireEvent.click(screen.getByRole("button", { name: /yes/i }));
    fireEvent.change(screen.getByLabelText(/what was most useful/i), { target: { value: " The veg food tips " } });
    fireEvent.change(screen.getByLabelText(/^first name/i), { target: { value: "Asha" } });
    fireEvent.click(screen.getByLabelText(/you can quote my comment/i));
    fireEvent.click(screen.getByRole("button", { name: /send feedback/i }));
    await screen.findByText(/thank you/i);
    expect(sent()).toMatchObject({ helpful: true, comment: "The veg food tips", name: "Asha", can_quote: true });
  });

  it("keeps the form and shows an error when sending fails", async () => {
    fetchMock.mockResolvedValue(new Response(null, { status: 500 }));
    render(<FeedbackCard destination="Kyoto" />);
    fireEvent.click(screen.getByRole("button", { name: /yes/i }));
    fireEvent.click(screen.getByRole("button", { name: /send feedback/i }));
    expect(await screen.findByRole("alert")).toHaveTextContent(/couldn't send/i);
    expect(screen.getByRole("button", { name: /send feedback/i })).toBeInTheDocument();
  });
});

describe("InstallButton", () => {
  function firePrompt(outcome: "accepted" | "dismissed" = "accepted") {
    const event = new Event("beforeinstallprompt") as Event & { prompt: () => Promise<void>; userChoice: Promise<unknown> };
    event.prompt = vi.fn().mockResolvedValue(undefined);
    event.userChoice = Promise.resolve({ outcome });
    act(() => { window.dispatchEvent(event); });
    return event;
  }

  it("is hidden until the browser says the app is installable", () => {
    render(<InstallButton />);
    expect(screen.queryByRole("button", { name: /install app/i })).not.toBeInTheDocument();
    firePrompt();
    expect(screen.getByRole("button", { name: /install app/i })).toBeInTheDocument();
  });

  it("opens the browser's install prompt and then hides", async () => {
    render(<InstallButton />);
    const event = firePrompt();
    await act(async () => { fireEvent.click(screen.getByRole("button", { name: /install app/i })); });
    expect(event.prompt).toHaveBeenCalledOnce();
    expect(screen.queryByRole("button", { name: /install app/i })).not.toBeInTheDocument();
  });

  it("hides once the app is installed", () => {
    render(<InstallButton />);
    firePrompt();
    act(() => { window.dispatchEvent(new Event("appinstalled")); });
    expect(screen.queryByRole("button", { name: /install app/i })).not.toBeInTheDocument();
  });
});
