import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";
import type {
  Appointment,
  TimeSlot,
  Equipment,
  Customer,
  AppointmentStatusType,
} from "@/types/appointment";

interface AppointmentState {
  // State
  appointments: Appointment[];
  timeSlots: TimeSlot[];
  equipment: Equipment[];
  customers: Customer[];
  isLoading: boolean;
  error: string | null;

  // Actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Appointment Actions
  addAppointment: (appointment: Appointment) => void;
  updateAppointment: (id: string, updates: Partial<Appointment>) => void;
  deleteAppointment: (id: string) => void;
  getAppointmentById: (id: string) => Appointment | undefined;
  getAppointmentsByCustomer: (customerId: string) => Appointment[];
  getAppointmentsByDate: (date: string) => Appointment[];
  updateAppointmentStatus: (id: string, status: AppointmentStatusType) => void;

  // Time Slot Actions
  setTimeSlots: (slots: TimeSlot[]) => void;
  updateTimeSlot: (id: string, updates: Partial<TimeSlot>) => void;
  getAvailableTimeSlots: (date: string) => TimeSlot[];
  bookTimeSlot: (id: string) => void;
  releaseTimeSlot: (id: string) => void;

  // Equipment Actions
  setEquipment: (equipment: Equipment[]) => void;
  updateEquipment: (id: string, updates: Partial<Equipment>) => void;
  getAvailableEquipment: () => Equipment[];

  // Customer Actions
  addCustomer: (customer: Customer) => void;
  updateCustomer: (id: string, updates: Partial<Customer>) => void;
  getCustomerById: (id: string) => Customer | undefined;
  getCustomerByEmail: (email: string) => Customer | undefined;

  // Utility Actions
  clearError: () => void;
  reset: () => void;
}

const initialState = {
  appointments: [],
  timeSlots: [],
  equipment: [],
  customers: [],
  isLoading: false,
  error: null,
};

export const useAppointmentStore = create<AppointmentState>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // Loading and Error Management
        setLoading: (loading) => set({ isLoading: loading }),
        setError: (error) => set({ error }),
        clearError: () => set({ error: null }),

        // Appointment Management
        addAppointment: (appointment) =>
          set((state) => ({
            appointments: [...state.appointments, appointment],
          })),

        updateAppointment: (id, updates) =>
          set((state) => ({
            appointments: state.appointments.map((apt) =>
              apt.id === id ? { ...apt, ...updates } : apt
            ),
          })),

        deleteAppointment: (id) =>
          set((state) => ({
            appointments: state.appointments.filter((apt) => apt.id !== id),
          })),

        getAppointmentById: (id) => {
          const { appointments } = get();
          return appointments.find((apt) => apt.id === id);
        },

        getAppointmentsByCustomer: (customerId) => {
          const { appointments } = get();
          return appointments.filter((apt) => apt.customerId === customerId);
        },

        getAppointmentsByDate: (date) => {
          const { appointments } = get();
          return appointments.filter((apt) => apt.timeSlot.date === date);
        },

        updateAppointmentStatus: (id, status) => {
          const now = new Date().toISOString();
          set((state) => ({
            appointments: state.appointments.map((apt) =>
              apt.id === id
                ? {
                    ...apt,
                    status,
                    updatedAt: now,
                    ...(status === "confirmed" && { confirmedAt: now }),
                    ...(status === "cancelled" && { cancelledAt: now }),
                  }
                : apt
            ),
          }));
        },

        // Time Slot Management
        setTimeSlots: (slots) => set({ timeSlots: slots }),

        updateTimeSlot: (id, updates) =>
          set((state) => ({
            timeSlots: state.timeSlots.map((slot) =>
              slot.id === id ? { ...slot, ...updates } : slot
            ),
          })),

        getAvailableTimeSlots: (date) => {
          const { timeSlots } = get();
          return timeSlots.filter(
            (slot) =>
              slot.date === date &&
              slot.isAvailable &&
              slot.currentBookings < slot.maxCapacity
          );
        },

        bookTimeSlot: (id) =>
          set((state) => ({
            timeSlots: state.timeSlots.map((slot) =>
              slot.id === id
                ? {
                    ...slot,
                    currentBookings: slot.currentBookings + 1,
                    isAvailable: slot.currentBookings + 1 < slot.maxCapacity,
                  }
                : slot
            ),
          })),

        releaseTimeSlot: (id) =>
          set((state) => ({
            timeSlots: state.timeSlots.map((slot) =>
              slot.id === id
                ? {
                    ...slot,
                    currentBookings: Math.max(0, slot.currentBookings - 1),
                    isAvailable: true,
                  }
                : slot
            ),
          })),

        // Equipment Management
        setEquipment: (equipment) => set({ equipment }),

        updateEquipment: (id, updates) =>
          set((state) => ({
            equipment: state.equipment.map((item) =>
              item.id === id ? { ...item, ...updates } : item
            ),
          })),

        getAvailableEquipment: () => {
          const { equipment } = get();
          return equipment.filter((item) => item.isAvailable);
        },

        // Customer Management
        addCustomer: (customer) =>
          set((state) => ({
            customers: [...state.customers, customer],
          })),

        updateCustomer: (id, updates) =>
          set((state) => ({
            customers: state.customers.map((customer) =>
              customer.id === id ? { ...customer, ...updates } : customer
            ),
          })),

        getCustomerById: (id) => {
          const { customers } = get();
          return customers.find((customer) => customer.id === id);
        },

        getCustomerByEmail: (email) => {
          const { customers } = get();
          return customers.find((customer) => customer.email === email);
        },

        // Utility
        reset: () => set(initialState),
      }),
      {
        name: "appointment-store",
        partialize: (state) => ({
          appointments: state.appointments,
          customers: state.customers,
          timeSlots: state.timeSlots,
          equipment: state.equipment,
        }),
      }
    ),
    {
      name: "appointment-store",
    }
  )
);
