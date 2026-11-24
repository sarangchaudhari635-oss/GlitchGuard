//! glitchguard-monitor — Main GlitchGuard Xous monitoring service.
//!
//! # Architecture Overview
//!
//! This binary is the central coordination point for all GlitchGuard activity
//! on the Dabao/Baochip-1x board. It runs as a Xous server process.
//!
//! ## Startup Sequence
//!
//! 1. Initialise the hardware observer (probe capability registry).
//! 2. Initialise the event engine (empty ring buffer).
//! 3. Initialise the crypto verifier (software fallback by default).
//! 4. Initialise the recovery FSM (NORMAL state).
//! 5. Register as a Xous server.
//! 6. Enter the main event loop.
//!
//! ## Main Event Loop
//!
//! Each iteration:
//! - Poll hardware observer for sensor readings.
//! - Process any pending heartbeat messages.
//! - Evaluate the recovery FSM.
//! - Serialise and transmit telemetry to UART.
//!
//! ## Phase Gate
//!
//! This binary currently compiles and runs in a hosted (std) test mode.
//! Full Xous integration requires:
//! 1. Xous runtime crates (Phase 1 / Phase 3).
//! 2. Physical board connection and verified COM port (Phase 0).
//! 3. Verified hardware sensor interfaces (Phase 2).
//!
//! The `main()` function below demonstrates the control flow but cannot
//! execute on hardware until Phase 3 integration is complete.

// In Xous / no_std environment this would be:
// #![no_std]
// #![no_main]
// For now, allow std for development/testing on host.

use crypto_verification::CryptoVerifier;
use event_engine::EventEngine;
use glitchguard_common::{
    DefensiveResponse, EventType, SecurityState, Severity,
};
use hardware_observer::HardwareObserver;
use heapless::String;
use recovery_engine::RecoveryEngine;

// ─────────────────────────────────────────────────────────────────────────────
// GlitchGuard Monitor
// ─────────────────────────────────────────────────────────────────────────────

pub struct GlitchGuardMonitor {
    hardware: HardwareObserver,
    events: EventEngine,
    crypto: CryptoVerifier,
    recovery: RecoveryEngine,
    heartbeat_sequence: u32,
}

impl GlitchGuardMonitor {
    pub fn new(session_id: &str) -> Self {
        let mut sid = String::new();
        let _ = sid.push_str(session_id);

        let mut hardware = HardwareObserver::new();
        hardware.initialize();

        Self {
            hardware,
            events: EventEngine::new(sid),
            crypto: CryptoVerifier::default(),
            recovery: RecoveryEngine::new(),
            heartbeat_sequence: 0,
        }
    }

    /// Process a single monitoring cycle.
    ///
    /// In Phase 3, this will be driven by the Xous message loop.
    /// Currently structured as a pure function for host-side testing.
    pub fn tick(&mut self, timestamp_ns: u64) {
        self.heartbeat_sequence = self.heartbeat_sequence.wrapping_add(1);

        // Poll hardware sensors
        if let Some(reading) = self.hardware.read_glitch_detector() {
            if reading.alert_active {
                // Hardware glitch detected — this is a real hardware event
                // Source: hardware_sensor
                // Currently unreachable until Phase 2 implementation
                let _response = self.recovery.on_anomaly(Severity::High, timestamp_ns);
                // Push hardware warning event to event engine
                // (event_id generation requires TRNG — placeholder for Phase 3)
            }
        }

        // Check reset source on first tick
        if self.heartbeat_sequence == 1 {
            if let Some(_reset_source) = self.hardware.read_reset_source() {
                // Record reset event
                // (Phase 3 implementation)
            }
        }
    }

    /// Inject a software-simulated fault event for testing.
    ///
    /// This path is ONLY called by the test harness or the Python simulator
    /// via the host backend. The source is always `software_simulator`.
    pub fn inject_simulated_fault(
        &mut self,
        _event_type: EventType,
        severity: Severity,
        timestamp_ns: u64,
    ) -> DefensiveResponse {
        // Software simulations always use this source — never hardware_sensor
        let response = self.recovery.on_anomaly(severity, timestamp_ns);
        response
    }

    /// Run an integrity verification test on a sample payload.
    pub fn run_integrity_check(&mut self, payload: &[u8], expected_hash: [u8; 32], timestamp_ns: u64) -> bool {
        let report = self.crypto.verify(payload, expected_hash);
        let passed = report.passed;

        // Drive FSM based on verification result
        if self.recovery.state() == SecurityState::Verifying {
            self.recovery.on_verification_result(passed, timestamp_ns);
        }

        passed
    }

    /// Return the current security FSM state.
    pub fn security_state(&self) -> SecurityState {
        self.recovery.state()
    }

    /// Return capability status report.
    pub fn capability_report(&self) -> impl Iterator<Item = (&&'static str, &glitchguard_common::CapabilityStatus)> {
        self.hardware.capabilities()
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Entry point (host-mode stub)
// ─────────────────────────────────────────────────────────────────────────────

fn main() {
    // This main() runs on the host for development/testing only.
    // Phase 3 will replace this with the Xous server registration and
    // message loop using `xous::create_server()`.

    println!("GlitchGuard Monitor — Development Mode");
    println!("Phase 0/1: Repository scaffold. Hardware integration pending.");
    println!();

    let mut monitor = GlitchGuardMonitor::new("sess-dev-0001");

    // Demonstrate capability registry
    println!("Hardware Capability Registry:");
    for (name, status) in monitor.capability_report() {
        println!("  {:20} {:?}", name, status);
    }

    println!();
    println!("Security FSM State: {:?}", monitor.security_state());
    println!();
    println!("Running 3 monitoring ticks...");
    for i in 0..3 {
        monitor.tick(i as u64 * 100_000_000);
        println!("  Tick {}: state={:?}", i, monitor.security_state());
    }

    println!();
    println!("Injecting simulated HIGH severity anomaly...");
    let response = monitor.inject_simulated_fault(
        EventType::Anomaly,
        Severity::High,
        300_000_000,
    );
    println!("  Response: {:?}", response);
    println!("  New state: {:?}", monitor.security_state());

    println!();
    println!("[PHASE 0 COMPLETE — Scaffold operational]");
    println!("[Connect board and run Phase 2 hardware reconnaissance to proceed]");
}

// ─────────────────────────────────────────────────────────────────────────────
// Tests
// ─────────────────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn monitor_initialises_in_normal_state() {
        let monitor = GlitchGuardMonitor::new("test-session");
        assert_eq!(monitor.security_state(), SecurityState::Normal);
    }

    #[test]
    fn simulated_fault_changes_state() {
        let mut monitor = GlitchGuardMonitor::new("test-session");
        let response = monitor.inject_simulated_fault(
            EventType::Anomaly,
            Severity::High,
            1_000_000_000,
        );
        assert_ne!(monitor.security_state(), SecurityState::Normal);
        assert_ne!(response, DefensiveResponse::None);
    }

    #[test]
    fn integrity_check_passes_on_valid_payload() {
        let mut monitor = GlitchGuardMonitor::new("test-session");
        let payload = b"glitchguard integrity test payload";
        let hash = monitor.crypto.hash(payload);
        let passed = monitor.run_integrity_check(payload, hash, 1_000_000_000);
        assert!(passed);
    }

    #[test]
    fn integrity_check_fails_on_corrupted_payload() {
        let mut monitor = GlitchGuardMonitor::new("test-session");
        let original = b"original payload";
        let corrupted = b"corrupted payload";
        let hash = monitor.crypto.hash(original);
        let passed = monitor.run_integrity_check(corrupted, hash, 1_000_000_000);
        assert!(!passed);
    }
}
