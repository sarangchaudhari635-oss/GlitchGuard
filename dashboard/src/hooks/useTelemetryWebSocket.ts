import { useState, useEffect, useRef, useCallback } from 'react';
import { DeviceInfo, ConnectionDiagnostics } from '../services/api';

export interface TelemetryState {
  wsConnected: boolean;
  connectionState: string;
  deviceInfo: DeviceInfo | null;
  diagnostics: ConnectionDiagnostics | null;
  metrics: Record<string, any> | null;
  recentEvents: any[];
  lastHeartbeatTime: number | null;
}

export function useTelemetryWebSocket() {
  const [state, setState] = useState<TelemetryState>({
    wsConnected: false,
    connectionState: 'DISCONNECTED',
    deviceInfo: null,
    diagnostics: null,
    metrics: null,
    recentEvents: [],
    lastHeartbeatTime: null,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  const connect = useCallback(() => {
    // Resolve websocket URL
    const isViteDev = window.location.port === '5173';
    const wsUrl = isViteDev
      ? 'ws://127.0.0.1:8000/ws/telemetry'
      : `${window.location.protocol === 'https:' ? 'wss://' : 'ws://'}${window.location.host}/ws/telemetry`;

    try {
      const socket = new WebSocket(wsUrl);
      wsRef.current = socket;

      socket.onopen = () => {
        setState((prev) => ({ ...prev, wsConnected: true }));
      };

      socket.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);

          if (msg.type === 'INIT_SNAPSHOT') {
            setState((prev) => ({
              ...prev,
              connectionState: msg.connection_state || prev.connectionState,
              deviceInfo: msg.device_info || prev.deviceInfo,
              diagnostics: msg.diagnostics || prev.diagnostics,
              metrics: msg.metrics || prev.metrics,
              recentEvents: msg.recent_events || prev.recentEvents,
              lastHeartbeatTime: Date.now(),
            }));
          } else if (msg.type === 'TELEMETRY_EVENT') {
            setState((prev) => {
              const newEvents = [msg.data, ...prev.recentEvents.slice(0, 49)];
              return {
                ...prev,
                connectionState: msg.connection?.state || prev.connectionState,
                diagnostics: msg.connection?.diagnostics || prev.diagnostics,
                recentEvents: newEvents,
                lastHeartbeatTime: Date.now(),
              };
            });
          } else if (msg.type === 'PONG') {
            setState((prev) => ({ ...prev, lastHeartbeatTime: Date.now() }));
          }
        } catch (e) {
          console.warn('Failed to parse WebSocket message:', e);
        }
      };

      socket.onclose = () => {
        setState((prev) => ({ ...prev, wsConnected: false }));
        // Retry connection in 2.5 seconds
        reconnectTimeoutRef.current = window.setTimeout(() => {
          connect();
        }, 2500);
      };

      socket.onerror = () => {
        socket.close();
      };
    } catch (err) {
      console.warn('WebSocket connection error:', err);
      reconnectTimeoutRef.current = window.setTimeout(() => {
        connect();
      }, 2500);
    }
  }, []);

  useEffect(() => {
    connect();

    // Heartbeat ping interval every 5 seconds
    const pingInterval = window.setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'PING' }));
      }
    }, 5000);

    return () => {
      window.clearInterval(pingInterval);
      if (reconnectTimeoutRef.current) {
        window.clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const sendPing = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'PING' }));
    }
  }, []);

  return { ...state, sendPing };
}
