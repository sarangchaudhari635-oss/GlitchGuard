//! recovery-engine — Defensive finite state machine for GlitchGuard.
//!
//! # FSM Transitions
//!
//! ```text
//! NORMAL ──anomaly──► SUSPECTED_ANOMALY ──threshold──► QUARANTINED
//!                                                           │
//!                                                     ──verify──►
//!                                                           │
//!                                                     ┌────┴────┐
//!                                                     │         │
//!                                                   pass       fail
//!                                                     │         │
//!                                                RECOVERED   LOCKDOWN
//!                                                     │
//!                                               ──resume──► NORMAL
//! ```
//!
//! # Safety Rules
//!
//! - Quarantine only the affected test application process.
//! - Never irreversibly lock the hardware.
//! - Preserve event evidence before transitioning.
//! - Require successful integrity verification before recovery.
//! - Record every state transition with a timestamp and evidence reference.
//! - After `LOCKDOWN_THRESHOLD` repeated failures, do not auto-recover.

#![no_std]
#![forbid(unsafe_code)]

use glitchguard_common::{DefensiveResponse, SecurityState, Severity};

// ─────────────────────────────────────────────────────────────────────────────
// Configuration
// ─────────────────────────────────────────────────────────────────────────────

/// Number of anomalies in the sliding window that triggers quarantine.
const QUARANTINE_THRESHOLD: u32 = 3;

/// Number of consecutive verification failures that trigger lockdown.
const LOCKDOWN_THRESHOLD: u32 = 5;

/// Window (in nanoseconds) over which anomaly count is evaluated.
const ANOMALY_WINDOW_NS: u64 = 60_000_000_000; // 60 seconds

// ─────────────────────────────────────────────────────────────────────────────
// State transition record
// ─────────────────────────────────────────────────────────────────────────────

/// A recorded state transition with evidence reference.
#[derive(Debug, Clone)]
pub struct StateTransition {
    pub from: SecurityState,
    pub to: SecurityState,
    pub timestamp_ns: u64,
    /// Event ID of the evidence that triggered this transition.
    pub trigger_event_id_prefix: [u8; 8],
    pub response: DefensiveResponse,
}

// ─────────────────────────────────────────────────────────────────────────────
// Recovery Engine (FSM)
// ─────────────────────────────────────────────────────────────────────────────

pub struct RecoveryEngine {
    state: SecurityState,
    anomaly_count: u32,
    verification_failure_count: u32,
    total_transitions: u32,
    last_anomaly_timestamp_ns: u64,
}

impl RecoveryEngine {
    pub fn new() -> Self {
        Self {
            state: SecurityState::Normal,
            anomaly_count: 0,
            verification_failure_count: 0,
            total_transitions: 0,
            last_anomaly_timestamp_ns: 0,
        }
    }

    /// Return the current FSM state.
    pub fn state(&self) -> SecurityState {
        self.state
    }

    /// Total number of state transitions since startup.
    pub fn total_transitions(&self) -> u32 {
        self.total_transitions
    }

    /// Report an anomaly event to the FSM.
    ///
    /// Returns the defensive response action taken.
    pub fn on_anomaly(&mut self, severity: Severity, timestamp_ns: u64) -> DefensiveResponse {
        // Reset anomaly count if outside the window
        if timestamp_ns.saturating_sub(self.last_anomaly_timestamp_ns) > ANOMALY_WINDOW_NS {
            self.anomaly_count = 0;
        }
        self.anomaly_count = self.anomaly_count.saturating_add(1);
        self.last_anomaly_timestamp_ns = timestamp_ns;

        match self.state {
            SecurityState::Normal => {
                self.transition_to(SecurityState::SuspectedAnomaly, timestamp_ns);
                DefensiveResponse::Alert
            }
            SecurityState::SuspectedAnomaly => {
                if self.anomaly_count >= QUARANTINE_THRESHOLD || severity >= Severity::High {
                    self.transition_to(SecurityState::Quarantined, timestamp_ns);
                    DefensiveResponse::Quarantined
                } else {
                    DefensiveResponse::Alert
                }
            }
            SecurityState::Quarantined => {
                // Already quarantined — trigger verification
                self.transition_to(SecurityState::Verifying, timestamp_ns);
                DefensiveResponse::Verifying
            }
            SecurityState::Lockdown => {
                // No automatic recovery from lockdown
                DefensiveResponse::Lockdown
            }
            _ => DefensiveResponse::Logged,
        }
    }

    /// Report the result of a cryptographic integrity verification.
    pub fn on_verification_result(&mut self, passed: bool, timestamp_ns: u64) -> DefensiveResponse {
        match self.state {
            SecurityState::Verifying => {
                if passed {
                    self.verification_failure_count = 0;
                    self.anomaly_count = 0;
                    self.transition_to(SecurityState::Recovered, timestamp_ns);
                    DefensiveResponse::Recovered
                } else {
                    self.verification_failure_count =
                        self.verification_failure_count.saturating_add(1);
                    if self.verification_failure_count >= LOCKDOWN_THRESHOLD {
                        self.transition_to(SecurityState::Lockdown, timestamp_ns);
                        DefensiveResponse::Lockdown
                    } else {
                        // Return to quarantine for another attempt
                        self.transition_to(SecurityState::Quarantined, timestamp_ns);
                        DefensiveResponse::Quarantined
                    }
                }
            }
            _ => DefensiveResponse::Logged,
        }
    }

    /// Resume from RECOVERED to NORMAL after evidence preservation.
    pub fn on_resume(&mut self, timestamp_ns: u64) -> DefensiveResponse {
        if self.state == SecurityState::Recovered {
            self.transition_to(SecurityState::Normal, timestamp_ns);
            DefensiveResponse::None
        } else {
            DefensiveResponse::Logged
        }
    }

    /// Determine the defensive response for a given FSM state.
    pub fn current_response(&self) -> DefensiveResponse {
        match self.state {
            SecurityState::Normal => DefensiveResponse::None,
            SecurityState::SuspectedAnomaly => DefensiveResponse::Alert,
            SecurityState::Quarantined => DefensiveResponse::Quarantined,
            SecurityState::Verifying => DefensiveResponse::Verifying,
            SecurityState::Recovered => DefensiveResponse::Recovered,
            SecurityState::Lockdown => DefensiveResponse::Lockdown,
        }
    }

    // ── Private helpers ──────────────────────────────────────────────────────

    fn transition_to(&mut self, new_state: SecurityState, _timestamp_ns: u64) {
        // In Phase 3, this will emit a STATE_TRANSITION event to the event engine.
        // For now, record the counter.
        self.state = new_state;
        self.total_transitions = self.total_transitions.wrapping_add(1);
    }
}

impl Default for RecoveryEngine {
    fn default() -> Self {
        Self::new()
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tests
// ─────────────────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn starts_in_normal_state() {
        let engine = RecoveryEngine::new();
        assert_eq!(engine.state(), SecurityState::Normal);
        assert_eq!(engine.total_transitions(), 0);
    }

    #[test]
    fn single_low_anomaly_moves_to_suspected() {
        let mut engine = RecoveryEngine::new();
        let response = engine.on_anomaly(Severity::Low, 1_000_000_000);
        assert_eq!(engine.state(), SecurityState::SuspectedAnomaly);
        assert_eq!(response, DefensiveResponse::Alert);
    }

    #[test]
    fn threshold_anomalies_trigger_quarantine() {
        let mut engine = RecoveryEngine::new();
        // First anomaly → SuspectedAnomaly
        engine.on_anomaly(Severity::Low, 1_000_000_000);
        // Second anomaly → still SuspectedAnomaly (count=2, threshold=3)
        engine.on_anomaly(Severity::Low, 2_000_000_000);
        // Third anomaly → Quarantined (count=3, threshold=3)
        let response = engine.on_anomaly(Severity::Low, 3_000_000_000);
        assert_eq!(engine.state(), SecurityState::Quarantined);
        assert_eq!(response, DefensiveResponse::Quarantined);
    }

    #[test]
    fn high_severity_immediately_quarantines() {
        let mut engine = RecoveryEngine::new();
        // First anomaly → SuspectedAnomaly
        engine.on_anomaly(Severity::High, 1_000_000_000);
        // Second HIGH anomaly → Quarantined (severity >= High bypasses count)
        let response = engine.on_anomaly(Severity::High, 2_000_000_000);
        assert_eq!(engine.state(), SecurityState::Quarantined);
        assert_eq!(response, DefensiveResponse::Quarantined);
    }

    #[test]
    fn successful_verification_leads_to_recovery() {
        let mut engine = RecoveryEngine::new();
        // Drive to Quarantined
        for i in 0..3 {
            engine.on_anomaly(Severity::Low, (i + 1) as u64 * 1_000_000_000);
        }
        assert_eq!(engine.state(), SecurityState::Quarantined);
        // Trigger verification
        engine.on_anomaly(Severity::Low, 4_000_000_000);
        assert_eq!(engine.state(), SecurityState::Verifying);
        // Pass verification
        let response = engine.on_verification_result(true, 5_000_000_000);
        assert_eq!(engine.state(), SecurityState::Recovered);
        assert_eq!(response, DefensiveResponse::Recovered);
        // Resume to Normal
        engine.on_resume(6_000_000_000);
        assert_eq!(engine.state(), SecurityState::Normal);
    }

    #[test]
    fn repeated_failures_trigger_lockdown() {
        let mut engine = RecoveryEngine::new();
        // Force into Verifying
        for i in 0..4 {
            engine.on_anomaly(Severity::Low, (i + 1) as u64 * 1_000_000_000);
        }
        // Fail verification LOCKDOWN_THRESHOLD times
        for i in 0..LOCKDOWN_THRESHOLD {
            // Re-enter Verifying from Quarantined
            engine.on_anomaly(Severity::Low, (10 + i) as u64 * 1_000_000_000);
            engine.on_verification_result(false, (20 + i) as u64 * 1_000_000_000);
        }
        assert_eq!(engine.state(), SecurityState::Lockdown);
    }

    #[test]
    fn lockdown_does_not_auto_recover() {
        let mut engine = RecoveryEngine::new();
        engine.state = SecurityState::Lockdown;
        let response = engine.on_anomaly(Severity::Critical, 1_000_000_000);
        assert_eq!(engine.state(), SecurityState::Lockdown);
        assert_eq!(response, DefensiveResponse::Lockdown);
    }
}
