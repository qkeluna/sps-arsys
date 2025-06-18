import {
  AppointmentSchema,
  CustomerSchema,
  TimeSlotSchema,
  BookingFormSchema,
} from "@/types/appointment";
import { generateId } from "@/lib/utils";

describe("Appointment System Types", () => {
  describe("CustomerSchema", () => {
    it("should validate valid customer data", () => {
      const validCustomer = {
        firstName: "John",
        lastName: "Doe",
        email: "john.doe@example.com",
        phone: "1234567890",
      };

      const result = CustomerSchema.safeParse(validCustomer);
      expect(result.success).toBe(true);
    });

    it("should reject invalid email", () => {
      const invalidCustomer = {
        firstName: "John",
        lastName: "Doe",
        email: "invalid-email",
        phone: "1234567890",
      };

      const result = CustomerSchema.safeParse(invalidCustomer);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toBe(
          "Please enter a valid email address"
        );
      }
    });

    it("should reject short names", () => {
      const invalidCustomer = {
        firstName: "J",
        lastName: "D",
        email: "john.doe@example.com",
        phone: "1234567890",
      };

      const result = CustomerSchema.safeParse(invalidCustomer);
      expect(result.success).toBe(false);
    });
  });

  describe("TimeSlotSchema", () => {
    it("should validate valid time slot", () => {
      const validTimeSlot = {
        id: generateId(),
        date: "2024-01-15",
        startTime: "09:00",
        endTime: "10:00",
        isAvailable: true,
        maxCapacity: 1,
        currentBookings: 0,
      };

      const result = TimeSlotSchema.safeParse(validTimeSlot);
      expect(result.success).toBe(true);
    });

    it("should reject negative capacity", () => {
      const invalidTimeSlot = {
        id: generateId(),
        date: "2024-01-15",
        startTime: "09:00",
        endTime: "10:00",
        isAvailable: true,
        maxCapacity: 0,
        currentBookings: 0,
      };

      const result = TimeSlotSchema.safeParse(invalidTimeSlot);
      expect(result.success).toBe(false);
    });
  });

  describe("BookingFormSchema", () => {
    it("should validate complete booking form", () => {
      const validBooking = {
        customer: {
          firstName: "Jane",
          lastName: "Smith",
          email: "jane.smith@example.com",
          phone: "0987654321",
        },
        sessionType: "portrait" as const,
        preferredDate: "2024-01-20",
        preferredTimeSlot: "10:00",
        duration: 60,
        equipmentRequested: ["camera-1", "lighting-1"],
        agreedToTerms: true,
      };

      const result = BookingFormSchema.safeParse(validBooking);
      expect(result.success).toBe(true);
    });

    it("should reject if terms not agreed", () => {
      const invalidBooking = {
        customer: {
          firstName: "Jane",
          lastName: "Smith",
          email: "jane.smith@example.com",
          phone: "0987654321",
        },
        sessionType: "portrait" as const,
        preferredDate: "2024-01-20",
        preferredTimeSlot: "10:00",
        duration: 60,
        equipmentRequested: ["camera-1"],
        agreedToTerms: false,
      };

      const result = BookingFormSchema.safeParse(invalidBooking);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toBe(
          "You must agree to the terms and conditions"
        );
      }
    });

    it("should reject invalid duration", () => {
      const invalidBooking = {
        customer: {
          firstName: "Jane",
          lastName: "Smith",
          email: "jane.smith@example.com",
          phone: "0987654321",
        },
        sessionType: "portrait" as const,
        preferredDate: "2024-01-20",
        preferredTimeSlot: "10:00",
        duration: 15, // Too short
        equipmentRequested: [],
        agreedToTerms: true,
      };

      const result = BookingFormSchema.safeParse(invalidBooking);
      expect(result.success).toBe(false);
    });
  });
});

describe("Utility Functions", () => {
  describe("generateId", () => {
    it("should generate unique IDs", () => {
      const id1 = generateId();
      const id2 = generateId();

      expect(id1).not.toBe(id2);
      expect(typeof id1).toBe("string");
      expect(id1.length).toBeGreaterThan(0);
    });
  });
});
