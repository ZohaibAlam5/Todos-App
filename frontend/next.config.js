/** @type {import('next').NextConfig} */
const nextConfig = {
  // Remove static export for Vercel deployment
  // output: 'export',

  images: {
    unoptimized: true,
  },

  // Enable trailingSlash for consistent URLs
  trailingSlash: false,

  // Optimize for Vercel deployment
  experimental: {
    appDir: false, // Use pages router
  },
};

export default nextConfig;