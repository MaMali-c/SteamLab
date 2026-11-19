import { defineConfig } from 'vitest/config';
import { loadEnv } from 'vite';
import { rm } from 'node:fs/promises';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'VITE_');
  const base = env.VITE_BASE_PATH || '/';
  if(!/^\/(?:[A-Za-z0-9_-]+\/)*$/.test(base)) throw new Error('VITE_BASE_PATH must be an absolute directory path ending with /');
  const requested = env.VITE_BROWSER_ENGINE || (mode === 'production' ? 'true' : 'false');
  if (!['true', 'false'].includes(requested)) throw new Error('VITE_BROWSER_ENGINE must be true or false');
  const origin = (env.VITE_API_BASE_URL || '').replace(/\/$/, '');
  if (origin) {
    const url = new URL(origin);
    if (url.origin !== origin || url.username || url.password || (mode === 'production' && url.protocol !== 'https:') || !['https:', 'http:'].includes(url.protocol)) {
      throw new Error('VITE_API_BASE_URL must be an exact API origin, using HTTPS in production');
    }
  }
  if (mode === 'production' && requested === 'false' && !origin) throw new Error('Remote API production builds require VITE_API_BASE_URL');
  return {
    base,
    plugins: [react(), tailwindcss(), { name: 'termoyazd-production-assets', async closeBundle() {
      if (mode === 'production' && requested === 'false') {
        await rm('dist/python', {recursive:true, force:true});
        await rm('dist/pyodide', {recursive:true, force:true});
      }
    } }],
    define: { 'import.meta.env.VITE_BROWSER_ENGINE': JSON.stringify(requested) },
    build: { sourcemap: false },
    server: {
      host: '127.0.0.1', port: 5173,
      proxy: { '/api': { target: process.env.VITE_API_TARGET || 'http://127.0.0.1:8000', changeOrigin: true } },
    },
    test: { environment: 'jsdom', setupFiles: ['./src/test-setup.ts'], globals: true },
  };
});
