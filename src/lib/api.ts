/**
 * API client configuration for connecting to the FastAPI backend
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from "axios";

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage or auth context
    const token = localStorage.getItem("access_token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }

    return Promise.reject(error);
  }
);

// API Types
export interface ApiError {
  message: string;
  detail?: string;
  status?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// Auth API
export const authApi = {
  // Register new user
  register: async (userData: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    phone?: string;
  }) => {
    const response = await api.post("/auth/register", userData);
    return response.data;
  },

  // Login user
  login: async (credentials: { email: string; password: string }) => {
    const response = await api.post("/auth/login", credentials);
    return response.data;
  },

  // Get current user
  getCurrentUser: async () => {
    const response = await api.get("/auth/me");
    return response.data;
  },

  // Update current user
  updateCurrentUser: async (userData: {
    first_name?: string;
    last_name?: string;
    phone?: string;
    timezone?: string;
    avatar_url?: string;
  }) => {
    const response = await api.put("/auth/me", userData);
    return response.data;
  },

  // Promote to studio owner
  promoteToStudioOwner: async () => {
    const response = await api.post("/auth/promote-to-studio-owner");
    return response.data;
  },

  // Logout
  logout: async () => {
    const response = await api.post("/auth/logout");
    return response.data;
  },
};

// Studios API
export const studiosApi = {
  // Get all studios for current user
  getMyStudios: async () => {
    const response = await api.get("/studios/my-studios");
    return response.data;
  },

  // Create new studio
  createStudio: async (studioData: {
    name: string;
    slug: string;
    description?: string;
    email?: string;
    phone?: string;
    website?: string;
    address_line1?: string;
    address_line2?: string;
    city?: string;
    state?: string;
    postal_code?: string;
    country?: string;
    timezone?: string;
    currency?: string;
    booking_window_days?: number;
    min_booking_notice_hours?: number;
  }) => {
    const response = await api.post("/studios/", studioData);
    return response.data;
  },

  // Get studio by ID
  getStudio: async (studioId: string) => {
    const response = await api.get(`/studios/${studioId}`);
    return response.data;
  },

  // Update studio
  updateStudio: async (studioId: string, studioData: any) => {
    const response = await api.put(`/studios/${studioId}`, studioData);
    return response.data;
  },

  // Delete studio
  deleteStudio: async (studioId: string) => {
    const response = await api.delete(`/studios/${studioId}`);
    return response.data;
  },
};

// Time Slots API
export const timeSlotsApi = {
  // Get studio time slots
  getStudioTimeSlots: async (
    studioId: string,
    params?: {
      date_from?: string;
      date_to?: string;
      available_only?: boolean;
    }
  ) => {
    const response = await api.get(`/studios/${studioId}/time-slots`, {
      params,
    });
    return response.data;
  },

  // Create time slot
  createTimeSlot: async (
    studioId: string,
    timeSlotData: {
      date: string;
      start_time: string;
      end_time: string;
      max_capacity?: number;
      base_price: number;
    }
  ) => {
    const response = await api.post(
      `/studios/${studioId}/time-slots`,
      timeSlotData
    );
    return response.data;
  },

  // Update time slot
  updateTimeSlot: async (timeSlotId: string, timeSlotData: any) => {
    const response = await api.put(`/time-slots/${timeSlotId}`, timeSlotData);
    return response.data;
  },

  // Delete time slot
  deleteTimeSlot: async (timeSlotId: string) => {
    const response = await api.delete(`/time-slots/${timeSlotId}`);
    return response.data;
  },
};

// Appointments API
export const appointmentsApi = {
  // Get appointments for studio owner
  getStudioAppointments: async (
    studioId: string,
    params?: {
      status?: string;
      date_from?: string;
      date_to?: string;
      page?: number;
      per_page?: number;
    }
  ) => {
    const response = await api.get(`/studios/${studioId}/appointments`, {
      params,
    });
    return response.data;
  },

  // Get appointments for customer
  getMyAppointments: async (params?: {
    status?: string;
    page?: number;
    per_page?: number;
  }) => {
    const response = await api.get("/appointments/my-appointments", { params });
    return response.data;
  },

  // Get appointment by ID
  getAppointment: async (appointmentId: string) => {
    const response = await api.get(`/appointments/${appointmentId}`);
    return response.data;
  },

  // Update appointment
  updateAppointment: async (appointmentId: string, appointmentData: any) => {
    const response = await api.put(
      `/appointments/${appointmentId}`,
      appointmentData
    );
    return response.data;
  },

  // Cancel appointment
  cancelAppointment: async (appointmentId: string, reason?: string) => {
    const response = await api.post(`/appointments/${appointmentId}/cancel`, {
      cancellation_reason: reason,
    });
    return response.data;
  },

  // Confirm appointment
  confirmAppointment: async (appointmentId: string) => {
    const response = await api.post(`/appointments/${appointmentId}/confirm`);
    return response.data;
  },
};

// Public API (for booking pages)
export const publicApi = {
  // Get studio by slug
  getStudioBySlug: async (slug: string) => {
    const response = await api.get(`/public/studios/${slug}`);
    return response.data;
  },

  // Get available time slots
  getAvailableTimeSlots: async (
    studioId: string,
    params?: {
      date_from?: string;
      date_to?: string;
    }
  ) => {
    const response = await api.get(
      `/public/studios/${studioId}/available-slots`,
      { params }
    );
    return response.data;
  },

  // Create public booking
  createBooking: async (bookingData: {
    customer_email: string;
    customer_first_name: string;
    customer_last_name: string;
    customer_phone?: string;
    time_slot_id: string;
    session_type: string;
    duration_minutes: number;
    equipment_requested?: string[];
    special_requirements?: string;
    agreed_to_terms: boolean;
  }) => {
    const response = await api.post("/public/bookings", bookingData);
    return response.data;
  },
};

// Health check
export const healthApi = {
  check: async () => {
    const response = await api.get("/health");
    return response.data;
  },
};

// Export the main API instance
export default api;
