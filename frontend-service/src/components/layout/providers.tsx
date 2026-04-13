'use client';

import React from 'react';
import { WebSocketProvider } from '@/hooks/use-websocket';

export default function Providers({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <WebSocketProvider>
      {children}
    </WebSocketProvider>
  );
}