'use client';

import { createContext, useContext, ReactNode, useEffect, useRef, useState, useCallback } from 'react';
import { toast } from 'sonner';

const WS_URL = (process.env.NEXT_PUBLIC_API_URL?.replace('http', 'ws') || 'ws://localhost:8000') + '/ws';

interface WebSocketContextValue {
  connected: boolean;
  subscribe: (event: string, callback: (data: unknown) => void) => () => void;
  emit: (event: string, data: unknown) => void;
}

const SocketContext = createContext<WebSocketContextValue | null>(null);

export function WebSocketProvider({ children }: { children: ReactNode }) {
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const listenersRef = useRef<Map<string, Set<(data: unknown) => void>>>(new Map());
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    
    wsRef.current = new WebSocket(WS_URL);
    
    wsRef.current.onopen = () => {
      setConnected(true);
      console.log('[WS] Connected');
      // Subscribe to training events
      wsRef.current?.send(JSON.stringify({
        event: 'subscribe',
        data: { room: 'training:imaging' }
      }));
      wsRef.current?.send(JSON.stringify({
        event: 'subscribe',
        data: { room: 'training:clinical' }
      }));
      wsRef.current?.send(JSON.stringify({
        event: 'subscribe',
        data: { room: 'llmops' }
      }));
      wsRef.current?.send(JSON.stringify({
        event: 'subscribe',
        data: { room: 'notifications' }
      }));
      wsRef.current?.send(JSON.stringify({
        event: 'subscribe',
        data: { room: 'xai:prediction' }
      }));
      wsRef.current?.send(JSON.stringify({
        event: 'subscribe',
        data: { room: 'xai:gradcam' }
      }));
      wsRef.current?.send(JSON.stringify({
        event: 'subscribe',
        data: { room: 'xai:severity' }
      }));
    };
    
    wsRef.current.onclose = () => {
      setConnected(false);
      console.log('[WS] Disconnected, reconnecting in 3s...');
      reconnectTimeoutRef.current = setTimeout(connect, 3000);
    };
    
    wsRef.current.onerror = () => {
      console.log('[WS] Connection error');
    };
    
    wsRef.current.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        console.log('[WS] Message received:', message);
        const data = message.data || message;
        
        if (message.event === 'prediction.completed') {
          toast.success('Prediction Complete', {
            description: `DR Grade: ${data.dr_grade}, Severity: ${data.overall_severity}`
          });
        } else if (message.event === 'prediction.failed') {
          toast.error('Prediction Failed', { description: data.error });
        } else if (message.event === 'training.pipeline') {
          if (data.status === 'completed') {
            toast.success('Training completed', { description: data.message });
          } else if (data.status === 'failed') {
            toast.error('Training failed', { description: data.message });
          }
        } else if (message.event?.startsWith('xai.')) {
          if (data.status === 'completed') {
            toast.success('XAI completed', { description: data.message });
          } else if (data.status === 'failed') {
            toast.error('XAI failed', { description: data.message });
          }
        } else if (message.event === 'notification') {
          toast(data.message as string);
        }

        const callbacks = listenersRef.current.get(message.event);
        if (callbacks) {
          callbacks.forEach(cb => cb(data));
        }
        const allCallbacks = listenersRef.current.get('*');
        if (allCallbacks) {
          allCallbacks.forEach(cb => cb(message));
        }
      } catch {
        console.warn('[WS] Invalid JSON:', event.data);
      }
    };
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      wsRef.current?.close();
    };
  }, [connect]);

  const subscribe = useCallback((event: string, callback: (data: unknown) => void) => {
    if (!listenersRef.current.has(event)) {
      listenersRef.current.set(event, new Set());
    }
    listenersRef.current.get(event)!.add(callback);
    
    return () => {
      listenersRef.current.get(event)?.delete(callback);
    };
  }, []);

  const emit = useCallback((event: string, data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ event, data }));
    }
  }, []);

  return (
    <SocketContext.Provider value={{ connected, subscribe, emit }}>
      {children}
    </SocketContext.Provider>
  );
}

export function useWebSocket() {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider');
  }
  return context;
}