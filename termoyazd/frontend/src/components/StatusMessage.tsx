import type { ReactNode } from 'react';
import Icon from './Icon';
export default function StatusMessage({ kind, children }: { kind: 'info' | 'error' | 'success'; children: ReactNode }) {
  return <div className={`status-message ${kind}`} role={kind === 'error' ? 'alert' : 'status'}><Icon name={kind === 'success' ? 'check' : 'info'} size={19}/><div>{children}</div></div>;
}
