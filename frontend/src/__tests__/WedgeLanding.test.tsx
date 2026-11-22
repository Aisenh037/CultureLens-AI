import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import WedgeLanding, { contactEmail } from "../landing/WedgeLanding";
import { WEDGES } from "../landing/wedges";
import { campaignSource, visitorId } from "../landing/tracking";

const fetchMock = vi.fn();

function bodies(path: string) {
  return fetchMock.mock.calls
    .filter(([url]) => String(url).endsWith(path))
    .map(([, init]) => JSON.parse((init as RequestInit).body as string));
}

beforeEach(() => {
  fetchMock.mockReset();
  fetchMock.mockResolvedValue(new Response(null, { status: 204 }));
  vi.stubGlobal("fetch", fetchMock);
  Element.prototype.scrollIntoView = vi.fn();
  localStorage.clear();
});

afterEach(() => vi.unstubAllGlobals());

describe("WedgeLanding", () => {
  it.each(Object.values(WEDGES))("renders the $id page and records one view", (wedge) => {
    render(<WedgeLanding wedge={wedge} />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(wedge.headline);
    expect(screen.getByRole("button", { name: wedge.price.button })).toBeInTheDocument();
    const views = bodies("/api/experiments/events");
    expect(views).toHaveLength(1);
    expect(views[0]).toMatchObject({ wedge: wedge.id, event: "view" });
  });

  it("is honest after a price click: records it and says nothing was charged", () => {
    const wedge = WEDGES["tour-operators"];
    render(<WedgeLanding wedge={wedge} />);
    fireEvent.click(screen.getByRole("button", { name: wedge.price.button }));
    expect(bodies("/api/experiments/events").map((b) => b.event)).toEqual(["view", "pay_click"]);
    expect(screen.getByText(/not taking payments yet/i)).toBeInTheDocument();
    expect(screen.getByText(/haven't been charged/i)).toBeInTheDocument();
  });

  it("does not submit without consent", () => {
    render(<WedgeLanding wedge={WEDGES["heritage-stories"]} />);
    fireEvent.change(screen.getByLabelText(/email \*/i), { target: { value: "a@b.co" } });
    fireEvent.click(screen.getByRole("button", { name: /join the waitlist/i }));
    expect(screen.getByRole("alert")).toHaveTextContent(/tick the box/i);
    expect(bodies("/api/experiments/waitlist")).toHaveLength(0);
  });

  it("submits the form and shows the success state", async () => {
    fetchMock.mockImplementation((url: string) =>
      Promise.resolve(url.endsWith("/waitlist")
        ? new Response(JSON.stringify({ status: "ok" }), { status: 201 })
        : new Response(null, { status: 204 })));
    render(<WedgeLanding wedge={WEDGES["travellers-abroad"]} />);
    fireEvent.change(screen.getByLabelText(/email \*/i), { target: { value: " asha@example.com " } });
    fireEvent.change(screen.getByLabelText(/name/i), { target: { value: "Asha" } });
    fireEvent.click(screen.getByLabelText(/15-minute call/i));
    fireEvent.click(screen.getByLabelText(/email me about the launch/i));
    fireEvent.click(screen.getByRole("button", { name: /join the waitlist/i }));

    expect(await screen.findByText(/you're on the list/i)).toBeInTheDocument();
    const [sent] = bodies("/api/experiments/waitlist");
    expect(sent).toMatchObject({
      wedge: "travellers-abroad", email: "asha@example.com", name: "Asha",
      wants_interview: true, consent: true,
    });
    expect(sent.role).toBeUndefined(); // blank optional fields are not sent
  });

  it("shows a readable error when the server rejects the signup", async () => {
    fetchMock.mockImplementation((url: string) =>
      Promise.resolve(new Response(null, { status: url.endsWith("/waitlist") ? 429 : 204 })));
    render(<WedgeLanding wedge={WEDGES["travellers-abroad"]} />);
    fireEvent.change(screen.getByLabelText(/email \*/i), { target: { value: "a@b.co" } });
    fireEvent.click(screen.getByLabelText(/email me about the launch/i));
    fireEvent.click(screen.getByRole("button", { name: /join the waitlist/i }));
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent(/too many attempts/i));
  });
});

describe("tracking helpers", () => {
  it("keeps one anonymous visitor id per browser", () => {
    const first = visitorId();
    expect(first).toMatch(/^[A-Za-z0-9_-]{8,64}$/);
    expect(visitorId()).toBe(first);
  });

  it.each([
    ["?utm_source=reddit", "reddit"],
    ["?ref=whatsapp.group-1", "whatsapp.group-1"],
    ["?utm_source=<script>alert(1)</script>", "scriptalert1script"],
    ["?utm_source=%20%20", undefined],
    ["", undefined],
  ])("cleans the campaign source %s", (search, expected) => {
    expect(campaignSource(search)).toBe(expected);
  });
});

describe("contact line", () => {
  afterEach(() => vi.unstubAllEnvs());

  it("shows the configured address as a mailto link", () => {
    vi.stubEnv("VITE_CONTACT_EMAIL", "hello@culturelens.example");
    render(<WedgeLanding wedge={WEDGES["tour-operators"]} />);
    const link = screen.getByRole("link", { name: "hello@culturelens.example" });
    expect(link).toHaveAttribute("href", "mailto:hello@culturelens.example");
  });

  it("is hidden when no address is configured", () => {
    vi.stubEnv("VITE_CONTACT_EMAIL", "");
    render(<WedgeLanding wedge={WEDGES["tour-operators"]} />);
    expect(screen.queryByText(/questions or ideas/i)).not.toBeInTheDocument();
  });

  it.each([
    [" a@b.co ", "a@b.co"],
    ["not-an-email", null],
    ["x@y.z\"><script>", null],
    [undefined, null],
  ])("validates %s", (raw, expected) => {
    expect(contactEmail(raw as string | undefined)).toBe(expected);
  });
});
