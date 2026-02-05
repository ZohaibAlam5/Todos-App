/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable standalone output for Docker production builds
  // This creates a self-contained deployment that doesn't need node_modules
  output:"standalone",

  images: {
    unoptimized: true,
  },

  // Enable trailingSlash for consistent URLs
  trailingSlash: false,

  // App router is enabled by default, no need to specify appDir
  experimental: {
    // appDir is true by default in Next.js 13+ with app directory
  },
};

export default nextConfig;