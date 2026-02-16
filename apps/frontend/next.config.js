/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  distDir: '.next',
  experimental: {
    optimizeCss: true,
  },
}

module.exports = nextConfig
