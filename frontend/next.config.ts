import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    // Pin the workspace root so a stray lockfile in a parent directory
    // doesn't change what Turbopack treats as the project.
    root: path.join(__dirname),
  },
};

export default nextConfig;
