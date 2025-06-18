/** @type {import('next').NextConfig} */
const nextConfig = {
  // Move serverComponentsExternalPackages to the new location
  serverExternalPackages: ["@prisma/client"],
  images: {
    domains: ["localhost"],
    formats: ["image/webp", "image/avif"],
  },
  // Enable strict mode for better development experience
  reactStrictMode: true,
  // Optimize for production
  compiler: {
    removeConsole: process.env.NODE_ENV === "production",
  },
};

module.exports = nextConfig;
