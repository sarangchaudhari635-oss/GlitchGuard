/**
 * GLITCHGUARD API Client
 * Provides REST services and hardware interaction methods.
 */

const API_BASE = '/api';

export interface DeviceInfo {
  device_type: string;
  silicon_id: string;
  bootloader_ver?: string;
  firmware_ver?: string;
  monitor_ver?: string;
  public_serial?: string;
  mode: string;
  clock_skipping_active?: boolean;
  attack_counter: number;
  connection_state: string;
  selected_port?: string;
}

export interface ConnectionDiagnostics {
  selected_port: string | null;
  baudrate: number;
  messages_received: number;
  invalid_messages: number;
  heartbeats_received: number;
  last_heartbeat_ago_sec: number | null;
  mean_heartbeat_interval_sec: number;
  heartbeat_jitter_sec: number;
  reconnect_count: number;
  connection_errors: number;
  last_error: string | null;
}

export interface SystemStatus {
  connected: boolean;
  connection_state: string;
  port: string | null;
  baudrate: number;
  available_ports: string[];
  device_info: DeviceInfo;
  diagnostics: ConnectionDiagnostics;
  total_events: number;
  current_security_state: string;
  current_experiment: Record<string, any> | null;
  timestamp_utc: string;
}

export const fetchStatus = async (): Promise<SystemStatus> => {
  const res = await fetch(`${API_BASE}/status`);
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch status`);
  return res.json();
};

export const fetchDeviceInfo = async (): Promise<DeviceInfo> => {
  const res = await fetch(`${API_BASE}/device/info`);
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch device info`);
  return res.json();
};

export const fetchCapabilities = async (): Promise<Record<string, string>> => {
  const res = await fetch(`${API_BASE}/device/capabilities`);
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch capabilities`);
  return res.json();
};

export const fetchConnectionDiagnostics = async (): Promise<{
  state: string;
  port: string | null;
  baudrate: number;
  diagnostics: ConnectionDiagnostics;
}> => {
  const res = await fetch(`${API_BASE}/device/connection`);
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch diagnostics`);
  return res.json();
};

export const fetchEvents = async (limit = 50, source?: string): Promise<any[]> => {
  let url = `${API_BASE}/events?limit=${limit}`;
  if (source) url += `&source=${source}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch events`);
  return res.json();
};

export const fetchMetrics = async (): Promise<Record<string, any>> => {
  const res = await fetch(`${API_BASE}/metrics`);
  if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch metrics`);
  return res.json();
};

export const pingDevice = async (): Promise<{ status: string; command?: string; response?: string; message?: string }> => {
  const res = await fetch(`${API_BASE}/device/ping`, { method: 'POST' });
  return res.json();
};

export const requestDeviceStatus = async (): Promise<{ status: string; command?: string; response?: string; message?: string }> => {
  const res = await fetch(`${API_BASE}/device/request-status`, { method: 'POST' });
  return res.json();
};

export const requestDeviceCapabilities = async (): Promise<{ status: string; command?: string; response?: string; message?: string }> => {
  const res = await fetch(`${API_BASE}/device/request-capabilities`, { method: 'POST' });
  return res.json();
};
