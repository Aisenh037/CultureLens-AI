// Registers jest-dom matchers on Vitest's expect *and* augments its types.
// The bare "@testing-library/jest-dom" entry only types the Jest globals, which
// Vitest 5's Assertion type no longer picks up (tsc failed in `npm run build`).
import "@testing-library/jest-dom/vitest";
