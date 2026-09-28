/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/api/:path*',
      },
      {
        source: '/screenshots/:path*',
        destination: 'http://127.0.0.1:8000/screenshots/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
