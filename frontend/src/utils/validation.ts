import { TravelRequest } from "../types/travel";

export interface ValidationErrors {
  destination?: string;
  interests?: string;
}

export function validateTravelRequest(data: TravelRequest): ValidationErrors {
  const errors: ValidationErrors = {};
  
  if (!data.destination || !data.destination.trim()) {
    errors.destination = "Destination is required (e.g. Paris, Kyoto).";
  } else if (data.destination.trim().length > 200) {
    errors.destination = "Destination name must be under 200 characters.";
  }
  
  if (!data.interests || data.interests.length === 0) {
    errors.interests = "Please select at least one interest.";
  }
  
  return errors;
}
