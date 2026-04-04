'use client';

import { ReactNode } from 'react';

export function ActiveThemeProvider({ children }: { children: ReactNode }) {
  return <>{children}</>;
}

export function useThemeConfig() {
  return { activeTheme: 'retinaxai', setActiveTheme: () => {} };
}
