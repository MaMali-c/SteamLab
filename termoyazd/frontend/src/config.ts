/** Public build-time configuration. Never put credentials in VITE_* variables. */
export function apiAddress(path: string): string {
  if (!path.startsWith('/api/')) throw new Error('Unsupported scientific API path.');
  const origin = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
  return origin + path;
}
