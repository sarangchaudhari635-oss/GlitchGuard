export type EventSource = 'hardware_sensor' | 'software_simulator' | 'runtime_monitor' | 'reset_controller';

export type EventType =
  | 'NORMAL'
  | 'ANOMALY'
  | 'INTEGRITY_FAILURE'
  | 'HARDWARE_WARNING'
  | 'RESET_EVENT'
  | 'HEARTBEAT_TIMEOUT'
  | 'RECOVERY'
  | 'SENSOR_UNAVAILABLE';

export type Severity = 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type VerificationStatus = 'PASSED' | 'FAILED' | 'SKIPPED' | 'PENDING' | 'ERROR';

export type DefensiveResponse =
  | 'NONE'
  | 'LOGGED'
  | 'ALERT'
  | 'QUARANTINED'
  | 'VERIFYING'
  | 'RECOVERED'
  | 'LOCKDOWN';

export type SecurityState =
  | 'NORMAL'
  | 'SUSPECTED_ANOMALY'
  | 'QUARANTINED'
  | 'VERIFYING'
  | 'RECOVERED'
  | 'LOCKDOWN';

export type CapabilityStatus = 'AVAILABLE' | 'UNAVAILABLE' | 'UNSUPPORTED' | 'NOT_VERIFIED' | 'ERROR';

export interface GlitchEvent {
  schema_version: string;
  event_id: string;
  timestamp_ns: number;
  source: EventSource;
  event_type: EventType;
  severity: Severity;
  experiment_id: string;
  device_session_id: string;
  evidence: Record<string, any>;
  verification_status: VerificationStatus;
  response: DefensiveResponse;
}

export interface SystemStatus {
  connected: boolean;
  port: string | null;
  available_ports: Array<{ device: string; description: string; hwid: string }>;
  total_events: number;
  current_security_state: SecurityState;
  current_experiment: Record<string, any> | null;
  timestamp_utc: string;
}

export interface CapabilityRegistry {
  glitch_detector: CapabilityStatus;
  security_mesh: CapabilityStatus;
  trng: CapabilityStatus;
  hw_sha: CapabilityStatus;
  hw_aes: CapabilityStatus;
  ecc_memory: CapabilityStatus;
  watchdog: CapabilityStatus;
  reset_source: CapabilityStatus;
}
