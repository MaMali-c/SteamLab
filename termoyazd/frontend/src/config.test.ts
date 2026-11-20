import {it,expect,vi,afterEach} from 'vitest';
import {apiAddress} from './config';
afterEach(()=>vi.unstubAllEnvs());
it('uses a configured API origin without losing the /api prefix',()=>{
  vi.stubEnv('VITE_API_BASE_URL','https://api.example.org');
  expect(apiAddress('/api/calculate')).toBe('https://api.example.org/api/calculate');
});
it('retains the local development proxy path',()=>{
  vi.stubEnv('VITE_API_BASE_URL','');
  expect(apiAddress('/api/health')).toBe('/api/health');
});
it('never accepts an arbitrary destination path',()=>{
  expect(()=>apiAddress('https://other.example.org')).toThrow();
});
