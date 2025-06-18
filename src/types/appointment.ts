import { z } from "zod";

// Appointment Status Enum
export const AppointmentStatus = z.enum([
  "pending",
  "confirmed",
  "cancelled",
  "completed",
  "no-show",
]);

// Time Slot Schema
export const TimeSlotSchema = z.object({
  id: z.string(),
  date: z.string(), // ISO date string
  startTime: z.string(), // HH:MM format
  endTime: z.string(), // HH:MM format
  isAvailable: z.boolean(),
  maxCapacity: z.number().min(1),
  currentBookings: z.number().min(0),
});

// Customer Information Schema
export const CustomerSchema = z.object({
  id: z.string().optional(),
  firstName: z.string().min(2, "First name must be at least 2 characters"),
  lastName: z.string().min(2, "Last name must be at least 2 characters"),
  email: z.string().email("Please enter a valid email address"),
  phone: z.string().min(10, "Please enter a valid phone number"),
  dateOfBirth: z.string().optional(),
  emergencyContact: z
    .object({
      name: z.string().optional(),
      phone: z.string().optional(),
    })
    .optional(),
});

// Photo Session Type
export const PhotoSessionType = z.enum([
  "portrait",
  "family",
  "professional",
  "creative",
  "product",
  "event",
]);

// Equipment Schema
export const EquipmentSchema = z.object({
  id: z.string(),
  name: z.string(),
  type: z.enum(["camera", "lighting", "backdrop", "props"]),
  isAvailable: z.boolean(),
  requiresSupervision: z.boolean().optional(),
});

// Appointment Schema
export const AppointmentSchema = z.object({
  id: z.string(),
  customerId: z.string(),
  customer: CustomerSchema,
  timeSlot: TimeSlotSchema,
  sessionType: PhotoSessionType,
  duration: z.number().min(30).max(480), // minutes, 30 min to 8 hours
  equipmentRequested: z.array(z.string()), // equipment IDs
  specialRequirements: z.string().optional(),
  totalPrice: z.number().min(0),
  status: AppointmentStatus,
  notes: z.string().optional(),
  createdAt: z.string(), // ISO date string
  updatedAt: z.string(), // ISO date string
  confirmedAt: z.string().optional(),
  cancelledAt: z.string().optional(),
  cancellationReason: z.string().optional(),
});

// Booking Form Schema
export const BookingFormSchema = z.object({
  customer: CustomerSchema.omit({ id: true }),
  sessionType: PhotoSessionType,
  preferredDate: z.string(),
  preferredTimeSlot: z.string(),
  duration: z.number().min(30).max(480),
  equipmentRequested: z.array(z.string()),
  specialRequirements: z.string().optional(),
  agreedToTerms: z.boolean().refine((val) => val === true, {
    message: "You must agree to the terms and conditions",
  }),
});

// Type exports
export type Appointment = z.infer<typeof AppointmentSchema>;
export type Customer = z.infer<typeof CustomerSchema>;
export type TimeSlot = z.infer<typeof TimeSlotSchema>;
export type Equipment = z.infer<typeof EquipmentSchema>;
export type BookingForm = z.infer<typeof BookingFormSchema>;
export type AppointmentStatusType = z.infer<typeof AppointmentStatus>;
export type PhotoSessionTypeEnum = z.infer<typeof PhotoSessionType>;
