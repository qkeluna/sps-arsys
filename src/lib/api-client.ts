/**
 * API Client for SPS Appointment System
 *
 * This client provides a clean interface to interact with the backend API,
 * handling authentication, error management, and type safety.
 */

// ============================================================================
// Types
// ============================================================================

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  role: "admin" | "studio_owner" | "staff" | "customer";
  is_active: boolean;
  is_verified: boolean;
  avatar_url?: string;
  timezone: string;
  created_at: string;
}

export interface Studio {
  id: string;
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
  timezone: string;
  currency: string;
  booking_window_days: number;
  min_booking_notice_hours: number;
  owner_id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CustomQuestion {
  id: string;
  question: string;
  type:
    | "text"
    | "textarea"
    | "select"
    | "radio"
    | "checkbox"
    | "number"
    | "email"
    | "phone"
    | "date";
  required: boolean;
  options?: string[];
  placeholder?: string;
  help_text?: string;
}

export interface Package {
  id: string;
  studio_id: string;
  name: string;
  slug: string;
  description?: string;
  session_type:
    | "portrait"
    | "family"
    | "professional"
    | "creative"
    | "product"
    | "event";
  duration_minutes: number;
  min_duration_minutes?: number;
  max_duration_minutes?: number;
  allow_custom_duration: boolean;
  base_price: number;
  currency: string;
  buffer_time_before: number;
  buffer_time_after: number;
  max_bookings_per_day?: number;
  min_booking_notice_hours: number;
  max_booking_days_ahead: number;
  included_equipment?: string[];
  optional_equipment?: string[];
  special_instructions?: string;
  custom_questions?: CustomQuestion[];
  status: "active" | "inactive" | "draft";
  is_public: boolean;
  requires_approval: boolean;
  featured_image_url?: string;
  display_order: number;
  color?: string;
  created_at: string;
  updated_at: string;
}

export interface PublicPackage {
  id: string;
  name: string;
  slug: string;
  description?: string;
  session_type:
    | "portrait"
    | "family"
    | "professional"
    | "creative"
    | "product"
    | "event";
  duration_minutes: number;
  min_duration_minutes?: number;
  max_duration_minutes?: number;
  allow_custom_duration: boolean;
  base_price: number;
  currency: string;
  featured_image_url?: string;
  color?: string;
  custom_questions?: CustomQuestion[];
}

export interface TimeSlot {
  id: string;
  studio_id: string;
  package_id?: string;
  date: string;
  start_time: string;
  end_time: string;
  max_capacity: number;
  current_bookings: number;
  is_available: boolean;
  override_price?: number;
  created_at: string;
}

export interface AvailableTimeSlot {
  id: string;
  date: string;
  start_time: string;
  end_time: string;
  available_capacity: number;
  price: number;
}

export interface Appointment {
  id: string;
  studio_id: string;
  customer_id: string;
  time_slot_id: string;
  package_id: string;
  session_type: string;
  duration_minutes: number;
  equipment_requested?: string[];
  special_requirements?: string;
  custom_form_responses?: Record<string, any>;
  base_price: number;
  equipment_cost: number;
  total_price: number;
  status: "pending" | "confirmed" | "cancelled" | "completed" | "no_show";
  notes?: string;
  created_at: string;
  updated_at: string;
  confirmed_at?: string;
  cancelled_at?: string;
  cancellation_reason?: string;
  customer?: User;
  package?: Package;
  time_slot?: TimeSlot;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface ApiError {
  error: string;
  detail?: string;
  status: string;
}

// ============================================================================
// API Client Class
// ============================================================================

class ApiClient {
  private baseUrl: string;
  private accessToken: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/$/, ""); // Remove trailing slash

    // Load token from localStorage if available
    if (typeof window !== "undefined") {
      this.accessToken = localStorage.getItem("access_token");
    }
  }

  // ============================================================================
  // Core HTTP Methods
  // ============================================================================

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    // Add authorization header if token exists
    if (this.accessToken) {
      headers.Authorization = `Bearer ${this.accessToken}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      // Handle different response types
      let data: any;
      const contentType = response.headers.get("content-type");

      if (contentType && contentType.includes("application/json")) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      if (!response.ok) {
        const errorMessage =
          data?.detail ||
          data?.error ||
          `HTTP ${response.status}: ${response.statusText}`;
        throw new Error(errorMessage);
      }

      return data;
    } catch (error) {
      console.error(`API request failed: ${url}`, error);

      if (error instanceof Error) {
        throw error;
      }

      throw new Error("Network request failed");
    }
  }

  private async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "GET" });
  }

  private async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  private async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  private async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "DELETE" });
  }

  // ============================================================================
  // Authentication Methods
  // ============================================================================

  async login(email: string, password: string): Promise<AuthTokens> {
    const tokens = await this.post<AuthTokens>("/auth/login", {
      email,
      password,
    });

    this.setTokens(tokens);
    return tokens;
  }

  async register(userData: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    phone?: string;
  }): Promise<AuthTokens> {
    const tokens = await this.post<AuthTokens>("/auth/register", userData);
    this.setTokens(tokens);
    return tokens;
  }

  async getCurrentUser(): Promise<User> {
    return this.get<User>("/auth/me");
  }

  async promoteToStudioOwner(): Promise<{ message: string }> {
    return this.post<{ message: string }>("/auth/promote-to-studio-owner", {
      confirm: true,
    });
  }

  logout(): void {
    this.accessToken = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
    }
  }

  private setTokens(tokens: AuthTokens): void {
    this.accessToken = tokens.access_token;
    if (typeof window !== "undefined") {
      localStorage.setItem("access_token", tokens.access_token);
      localStorage.setItem("user", JSON.stringify(tokens.user));
    }
  }

  isAuthenticated(): boolean {
    return !!this.accessToken;
  }

  // ============================================================================
  // Studio Methods
  // ============================================================================

  async getMyStudios(): Promise<Studio[]> {
    return this.get<Studio[]>("/studios/my-studios");
  }

  async createStudio(studioData: {
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
  }): Promise<Studio> {
    return this.post<Studio>("/studios/", studioData);
  }

  async getStudio(studioId: string): Promise<Studio> {
    return this.get<Studio>(`/studios/${studioId}`);
  }

  async updateStudio(
    studioId: string,
    studioData: Partial<Studio>
  ): Promise<Studio> {
    return this.put<Studio>(`/studios/${studioId}`, studioData);
  }

  // ============================================================================
  // Package/Event Type Methods
  // ============================================================================

  async getStudioPackages(
    studioId: string,
    options?: {
      status?: "active" | "inactive" | "draft";
      is_public?: boolean;
      skip?: number;
      limit?: number;
    }
  ): Promise<Package[]> {
    const params = new URLSearchParams();

    if (options?.status) params.append("status_filter", options.status);
    if (options?.is_public !== undefined)
      params.append("is_public", options.is_public.toString());
    if (options?.skip) params.append("skip", options.skip.toString());
    if (options?.limit) params.append("limit", options.limit.toString());

    const query = params.toString() ? `?${params.toString()}` : "";
    return this.get<Package[]>(`/packages/studio/${studioId}${query}`);
  }

  async createPackage(
    studioId: string,
    packageData: {
      name: string;
      slug: string;
      description?: string;
      session_type:
        | "portrait"
        | "family"
        | "professional"
        | "creative"
        | "product"
        | "event";
      duration_minutes: number;
      min_duration_minutes?: number;
      max_duration_minutes?: number;
      allow_custom_duration?: boolean;
      base_price: number;
      currency?: string;
      buffer_time_before?: number;
      buffer_time_after?: number;
      max_bookings_per_day?: number;
      min_booking_notice_hours?: number;
      max_booking_days_ahead?: number;
      included_equipment?: string[];
      optional_equipment?: string[];
      special_instructions?: string;
      custom_questions?: CustomQuestion[];
      status?: "active" | "inactive" | "draft";
      is_public?: boolean;
      requires_approval?: boolean;
      featured_image_url?: string;
      display_order?: number;
      color?: string;
    }
  ): Promise<Package> {
    return this.post<Package>(`/packages/?studio_id=${studioId}`, packageData);
  }

  async getPackage(packageId: string): Promise<Package> {
    return this.get<Package>(`/packages/${packageId}`);
  }

  async updatePackage(
    packageId: string,
    packageData: Partial<Package>
  ): Promise<Package> {
    return this.put<Package>(`/packages/${packageId}`, packageData);
  }

  async deletePackage(packageId: string): Promise<{ message: string }> {
    return this.delete<{ message: string }>(`/packages/${packageId}`);
  }

  async duplicatePackage(
    packageId: string,
    options?: {
      new_name?: string;
      new_slug?: string;
    }
  ): Promise<Package> {
    const params = new URLSearchParams();
    if (options?.new_name) params.append("new_name", options.new_name);
    if (options?.new_slug) params.append("new_slug", options.new_slug);

    const query = params.toString() ? `?${params.toString()}` : "";
    return this.post<Package>(`/packages/${packageId}/duplicate${query}`);
  }

  // ============================================================================
  // Public API Methods (for booking pages)
  // ============================================================================

  async getPublicStudio(studioSlug: string): Promise<Studio> {
    return this.get<Studio>(`/public/studios/${studioSlug}`);
  }

  async getPublicStudioPackages(studioSlug: string): Promise<PublicPackage[]> {
    return this.get<PublicPackage[]>(`/public/studios/${studioSlug}/packages`);
  }

  async getAvailableTimeSlots(
    studioId: string,
    options?: {
      package_id?: string;
      date_from?: string;
      date_to?: string;
    }
  ): Promise<AvailableTimeSlot[]> {
    const params = new URLSearchParams();
    if (options?.package_id) params.append("package_id", options.package_id);
    if (options?.date_from) params.append("date_from", options.date_from);
    if (options?.date_to) params.append("date_to", options.date_to);

    const query = params.toString() ? `?${params.toString()}` : "";
    return this.get<AvailableTimeSlot[]>(
      `/public/studios/${studioId}/available-slots${query}`
    );
  }

  async createPublicBooking(bookingData: {
    customer_email: string;
    customer_first_name: string;
    customer_last_name: string;
    customer_phone?: string;
    package_id: string;
    time_slot_id: string;
    duration_minutes?: number;
    equipment_requested?: string[];
    special_requirements?: string;
    custom_form_responses?: Record<string, any>;
  }): Promise<Appointment> {
    return this.post<Appointment>("/public/bookings", bookingData);
  }

  async getPublicBooking(
    bookingId: string,
    customerEmail: string
  ): Promise<Appointment> {
    return this.get<Appointment>(
      `/public/bookings/${bookingId}?customer_email=${encodeURIComponent(
        customerEmail
      )}`
    );
  }

  async cancelPublicBooking(
    bookingId: string,
    customerEmail: string,
    cancellationReason?: string
  ): Promise<{ message: string }> {
    const params = new URLSearchParams();
    params.append("customer_email", customerEmail);
    if (cancellationReason)
      params.append("cancellation_reason", cancellationReason);

    return this.post<{ message: string }>(
      `/public/bookings/${bookingId}/cancel?${params.toString()}`
    );
  }

  // ============================================================================
  // Appointment Methods (Studio Owner)
  // ============================================================================

  async getAppointments(options?: {
    studio_id?: string;
    status?: string;
    date_from?: string;
    date_to?: string;
    skip?: number;
    limit?: number;
  }): Promise<Appointment[]> {
    const params = new URLSearchParams();
    if (options?.studio_id) params.append("studio_id", options.studio_id);
    if (options?.status) params.append("status", options.status);
    if (options?.date_from) params.append("date_from", options.date_from);
    if (options?.date_to) params.append("date_to", options.date_to);
    if (options?.skip) params.append("skip", options.skip.toString());
    if (options?.limit) params.append("limit", options.limit.toString());

    const query = params.toString() ? `?${params.toString()}` : "";
    return this.get<Appointment[]>(`/appointments/${query}`);
  }

  async getAppointment(appointmentId: string): Promise<Appointment> {
    return this.get<Appointment>(`/appointments/${appointmentId}`);
  }

  async updateAppointment(
    appointmentId: string,
    appointmentData: {
      status?: "pending" | "confirmed" | "cancelled" | "completed" | "no_show";
      duration_minutes?: number;
      equipment_requested?: string[];
      special_requirements?: string;
      notes?: string;
      cancellation_reason?: string;
    }
  ): Promise<Appointment> {
    return this.put<Appointment>(
      `/appointments/${appointmentId}`,
      appointmentData
    );
  }

  // ============================================================================
  // Time Slot Methods
  // ============================================================================

  async createTimeSlot(
    studioId: string,
    timeSlotData: {
      package_id?: string;
      date: string;
      start_time: string;
      end_time: string;
      max_capacity?: number;
      is_available?: boolean;
      override_price?: number;
    }
  ): Promise<TimeSlot> {
    return this.post<TimeSlot>(`/studios/${studioId}/time-slots`, timeSlotData);
  }

  async getTimeSlots(
    studioId: string,
    options?: {
      date_from?: string;
      date_to?: string;
      package_id?: string;
    }
  ): Promise<TimeSlot[]> {
    const params = new URLSearchParams();
    if (options?.date_from) params.append("date_from", options.date_from);
    if (options?.date_to) params.append("date_to", options.date_to);
    if (options?.package_id) params.append("package_id", options.package_id);

    const query = params.toString() ? `?${params.toString()}` : "";
    return this.get<TimeSlot[]>(`/studios/${studioId}/time-slots${query}`);
  }

  async updateTimeSlot(
    studioId: string,
    timeSlotId: string,
    timeSlotData: {
      max_capacity?: number;
      is_available?: boolean;
      override_price?: number;
    }
  ): Promise<TimeSlot> {
    return this.put<TimeSlot>(
      `/studios/${studioId}/time-slots/${timeSlotId}`,
      timeSlotData
    );
  }

  async deleteTimeSlot(
    studioId: string,
    timeSlotId: string
  ): Promise<{ message: string }> {
    return this.delete<{ message: string }>(
      `/studios/${studioId}/time-slots/${timeSlotId}`
    );
  }

  // ============================================================================
  // Utility Methods
  // ============================================================================

  async healthCheck(): Promise<{
    status: string;
    app: string;
    version: string;
  }> {
    return this.get<{ status: string; app: string; version: string }>(
      "/health"
    );
  }
}

// ============================================================================
// Export
// ============================================================================

// Create and export a singleton instance
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const apiClient = new ApiClient(API_URL);
