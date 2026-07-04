import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { TravelForm } from "../components/TravelForm";
import { TravelRequest } from "../types/travel";

const mockFormData: TravelRequest = {
  destination: "Tokyo, Japan",
  budget: "Mid-range",
  duration_days: 3,
  travel_style: "Solo",
  companions: "None",
  interests: ["Culture"],
  languages: ["English"],
  accessibility_needs: [],
  food_preference: "No Restrictions",
};

describe("TravelForm Component", () => {
  it("renders key form input elements correctly", () => {
    const handleFieldChange = vi.fn();
    const handleFormSubmit = vi.fn();

    render(
      <TravelForm
        formData={mockFormData}
        errors={{}}
        loading={false}
        onChange={handleFieldChange}
        onSubmit={handleFormSubmit}
      />
    );

    expect(screen.getByLabelText(/Where is your destination?/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Trip Duration/i)).toBeInTheDocument();
  });

  it("submits the form when clicking the submit button", () => {
    const handleFieldChange = vi.fn();
    const handleFormSubmit = vi.fn((e) => e.preventDefault());

    render(
      <TravelForm
        formData={mockFormData}
        errors={{}}
        loading={false}
        onChange={handleFieldChange}
        onSubmit={handleFormSubmit}
      />
    );

    const submitBtn = screen.getByRole("button", { name: /DISCOVER LIKE A LOCAL/i });
    fireEvent.click(submitBtn);

    expect(handleFormSubmit).toHaveBeenCalledTimes(1);
  });
});
