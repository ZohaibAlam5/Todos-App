/** @type {import('next').NextConfig} */
const nextConfig = {
  // Remove static export for Vercel deployment
  // output: 'export',

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