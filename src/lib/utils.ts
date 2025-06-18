import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { format, parseISO, addDays, startOfDay, endOfDay } from "date-fns";

/**
 * Combines class names using clsx and tailwind-merge
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Generates a unique ID using timestamp and random number
 */
export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Formats a date string for display
 */
export function formatDate(dateString: string): string {
  try {
    return format(parseISO(dateString), "PPP");
  } catch {
    return dateString;
  }
}

/**
 * Formats time string for display
 */
export function formatTime(timeString: string): string {
  try {
    const [hours, minutes] = timeString.split(":");
    const date = new Date();
    date.setHours(parseInt(hours), parseInt(minutes));
    return format(date, "h:mm a");
  } catch {
    return timeString;
  }
}

/**
 * Formats date and time for display
 */
export function formatDateTime(dateString: string, timeString: string): string {
  try {
    const [hours, minutes] = timeString.split(":");
    const date = parseISO(dateString);
    date.setHours(parseInt(hours), parseInt(minutes));
    return format(date, "PPP 'at' h:mm a");
  } catch {
    return `${dateString} at ${timeString}`;
  }
}

/**
 * Gets the current date in ISO format
 */
export function getCurrentDate(): string {
  return format(new Date(), "yyyy-MM-dd");
}

/**
 * Gets the current time in HH:mm format
 */
export function getCurrentTime(): string {
  return format(new Date(), "HH:mm");
}

/**
 * Generates an array of dates starting from today for a given number of days
 */
export function getUpcomingDates(days: number = 30): string[] {
  const dates: string[] = [];
  const today = new Date();

  for (let i = 0; i < days; i++) {
    const date = addDays(today, i);
    dates.push(format(date, "yyyy-MM-dd"));
  }

  return dates;
}

/**
 * Validates if a date is in the future
 */
export function isFutureDate(dateString: string): boolean {
  try {
    const date = parseISO(dateString);
    const today = startOfDay(new Date());
    return date >= today;
  } catch {
    return false;
  }
}

/**
 * Calculates the duration between two times in minutes
 */
export function calculateDuration(startTime: string, endTime: string): number {
  try {
    const [startHours, startMinutes] = startTime.split(":").map(Number);
    const [endHours, endMinutes] = endTime.split(":").map(Number);

    const startTotalMinutes = startHours * 60 + startMinutes;
    const endTotalMinutes = endHours * 60 + endMinutes;

    return endTotalMinutes - startTotalMinutes;
  } catch {
    return 0;
  }
}

/**
 * Formats duration in minutes to human readable format
 */
export function formatDuration(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;

  if (hours === 0) {
    return `${mins} minutes`;
  } else if (mins === 0) {
    return `${hours} ${hours === 1 ? "hour" : "hours"}`;
  } else {
    return `${hours}h ${mins}m`;
  }
}

/**
 * Validates email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validates phone number format (basic validation)
 */
export function isValidPhone(phone: string): boolean {
  const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
  return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ""));
}

/**
 * Capitalizes the first letter of each word
 */
export function capitalizeWords(str: string): string {
  return str.replace(/\b\w/g, (char) => char.toUpperCase());
}

/**
 * Truncates text to a specified length
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + "...";
}
