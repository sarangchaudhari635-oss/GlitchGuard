//! event-engine — Structured event processing, timestamping, and ring-buffer history.
//!
//! This crate receives raw event data from other GLITCHGUARD services, assigns
//! monotonic timestamps, maintains a fixed-size event history, and provides
//! serialisation helpers for the UART telemetry stream.
//!
//! # Design
//!
//! Events are stored in a fixed-capacity ring buffer (`heapless::Deque`).
//! When the buffer is full, the oldest event is dropped to make room.
//! This ensures bounded memory usage on the embedded target.

#![no_std]
#![forbid(unsafe_code)]

use glitchguard_common::{
    DefensiveResponse, EventSource, EventType, GlitchEvent, Severity, VerificationStatus,
    SCHEMA_VERSION,
};
use heapless::{Deque, String};

// ─────────────────────────────────────────────────────────────────────────────
// Configuration
// ─────────────────────────────────────────────────────────────────────────────

/// Maximum number of events retained in the ring buffer.
/// Each GlitchEvent is approximately 128–256 bytes in memory.
const EVENT_HISTORY_CAPACITY: usize = 64;

// ─────────────────────────────────────────────────────────────────────────────
// Event Engine
// ─────────────────────────────────────────────────────────────────────────────

pub struct EventEngine {
    history: Deque<GlitchEvent, EVENT_HISTORY_CAPACITY>,
    sequence: u32,
    session_id: String<32>,
}

impl EventEngine {
    pub fn new(session_id: String<32>) -> Self {
        Self {
            history: Deque::new(),
            sequence: 0,
            session_id,
        }
    }

    /// Push a new event into the ring buffer.
    ///
    /// If the buffer is full, the oldest event is evicted.
    pub fn push(&mut self, event: GlitchEvent) {
        if self.history.is_full() {
            // Evict oldest event to maintain bounded memory
            self.history.pop_front();
        }
        let _ = self.history.push_back(event);
        self.sequence = self.sequence.wrapping_add(1);
    }

    /// Build and push a heartbeat event.
    ///
    /// `timestamp_ns` should come from the Xous system clock (ticktimer service).
    /// Until the ticktimer interface is verified, the caller passes a u64.
    pub fn push_heartbeat(&mut self, timestamp_ns: u64, event_id: String<36>) {
        let event = GlitchEvent::heartbeat(event_id, timestamp_ns, self.session_id.clone(), self.sequence);
        self.push(event);
    }

    /// Build and push an anomaly event.
    pub fn push_anomaly(
        &mut self,
        timestamp_ns: u64,
        event_id: String<36>,
        source: EventSource,
        event_type: EventType,
        severity: Severity,
        experiment_id: String<32>,
        verification_status: VerificationStatus,
        response: DefensiveResponse,
    ) {
        let event = GlitchEvent {
            schema_version: SCHEMA_VERSION,
            event_id,
            timestamp_ns,
            source,
            event_type,
            severity,
            experiment_id,
            device_session_id: self.session_id.clone(),
            verification_status,
            response,
        };
        self.push(event);
    }

    /// Return the total number of events processed (including evicted ones).
    pub fn sequence(&self) -> u32 {
        self.sequence
    }

    /// Return the number of events currently in the history buffer.
    pub fn history_len(&self) -> usize {
        self.history.len()
    }

    /// Peek at the most recent event without removing it.
    pub fn latest(&self) -> Option<&GlitchEvent> {
        self.history.back()
    }

    /// Iterate over all events in chronological order (oldest first).
    pub fn iter(&self) -> impl Iterator<Item = &GlitchEvent> {
        self.history.iter()
    }

    /// Count events by severity level.
    pub fn count_by_severity(&self, severity: Severity) -> usize {
        self.history.iter().filter(|e| e.severity == severity).count()
    }

    /// Count anomaly events (non-NORMAL types) since startup.
    pub fn anomaly_count(&self) -> usize {
        self.history
            .iter()
            .filter(|e| e.event_type != EventType::Normal)
            .count()
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tests
// ─────────────────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    fn make_session_id() -> String<32> {
        let mut s = String::new();
        let _ = s.push_str("test-session-001");
        s
    }

    fn make_event_id(_n: u8) -> String<36> {
        let mut s = String::new();
        // Simplified non-UUID for test purposes
        let _ = s.push_str("00000000-0000-0000-0000-000000000000");
        s
    }

    #[test]
    fn engine_starts_empty() {
        let engine = EventEngine::new(make_session_id());
        assert_eq!(engine.history_len(), 0);
        assert_eq!(engine.sequence(), 0);
        assert!(engine.latest().is_none());
    }

    #[test]
    fn heartbeat_increments_sequence() {
        let mut engine = EventEngine::new(make_session_id());
        engine.push_heartbeat(1000, make_event_id(1));
        assert_eq!(engine.sequence(), 1);
        assert_eq!(engine.history_len(), 1);
    }

    #[test]
    fn ring_buffer_evicts_oldest() {
        let mut engine = EventEngine::new(make_session_id());
        // Fill beyond capacity
        for i in 0..(EVENT_HISTORY_CAPACITY + 5) {
            engine.push_heartbeat(i as u64 * 1000, make_event_id(0));
        }
        // Buffer should not exceed capacity
        assert_eq!(engine.history_len(), EVENT_HISTORY_CAPACITY);
        // Sequence should reflect total events, not just buffered ones
        assert_eq!(engine.sequence() as usize, EVENT_HISTORY_CAPACITY + 5);
    }

    #[test]
    fn anomaly_count_excludes_normal_events() {
        let mut engine = EventEngine::new(make_session_id());
        engine.push_heartbeat(1000, make_event_id(1));
        engine.push_heartbeat(2000, make_event_id(2));

        let mut exp_id = String::new();
        let _ = exp_id.push_str("GG-TEST-001");

        engine.push_anomaly(
            3000,
            make_event_id(3),
            EventSource::RuntimeMonitor,
            EventType::Anomaly,
            Severity::Medium,
            exp_id,
            VerificationStatus::Pending,
            DefensiveResponse::Alert,
        );

        assert_eq!(engine.anomaly_count(), 1);
    }

    #[test]
    fn simulated_source_is_not_hardware() {
        let mut engine = EventEngine::new(make_session_id());
        let mut exp_id = String::new();
        let _ = exp_id.push_str("GG-SIM-001");

        engine.push_anomaly(
            1000,
            make_event_id(1),
            EventSource::SoftwareSimulator,  // must never be HardwareSensor
            EventType::IntegrityFailure,
            Severity::High,
            exp_id,
            VerificationStatus::Failed,
            DefensiveResponse::Quarantined,
        );

        let event = engine.latest().unwrap();
        assert_eq!(event.source, EventSource::SoftwareSimulator);
        assert_ne!(event.source, EventSource::HardwareSensor);
    }
}
