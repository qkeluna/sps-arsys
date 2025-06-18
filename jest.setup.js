import "@testing-library/jest-dom";

// Add any global test setup here
// For example, you can configure mock data or global test utilities

// Mock IntersectionObserver for tests that might use it
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock ResizeObserver for tests that might use it
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};
