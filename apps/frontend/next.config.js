/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  distDir: '.next',
  experimental: {
    optimizeCss: true, // Enable with critters for production CSS optimization
  },
}

module.exports = nextConfig
