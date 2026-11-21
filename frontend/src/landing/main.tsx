import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "../index.css";
import WedgeLanding from "./WedgeLanding";
import { WEDGES, type WedgeId } from "./wedges";

const root = document.getElementById("root")!;
const wedge = WEDGES[root.dataset.wedge as WedgeId];

// Landing pages follow the visitor's system theme (no toggle on these pages).
if (window.matchMedia?.("(prefers-color-scheme: dark)").matches) {
  document.documentElement.classList.add("dark");
}

createRoot(root).render(
  <StrictMode>
    <WedgeLanding wedge={wedge} />
  </StrictMode>,
);
