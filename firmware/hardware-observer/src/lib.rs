//! hardware-observer — Hardware sensor interface and capability registry.
//!
//! # Design Principles
//!
//! This module is the ONLY place in GLITCHGUARD that accesses hardware security
//! sensor registers. All register addresses and field definitions must be
//! verified against:
//!
//!   1. The official Baochip-1x/Betrusted SoC documentation or RTL.
//!   2. The Xous driver source in `xous-core/services/`.
//!   3. The board schematic for Dabao.
//!
//! **Never invent register addresses.** If a register address is unverified,
//! the corresponding capability status is `NOT_VERIFIED` and the sensor returns
//! no data.
//!
//! # Capability Registry
//!
//! Every hardware feature is tracked with a [`CapabilityStatus`]. The registry
//! is populated at startup by probing documented interfaces. Features that
//! cannot be confirmed remain `NOT_VERIFIED` until physical validation.
//!
//! # Safety
//!
//! Direct MMIO register access requires `unsafe`. Every unsafe block in this
//! module must include a comment referencing the hardware documentation that
//! justifies the access.

#![no_std]

use glitchguard_common::CapabilityStatus;
use heapless::FnvIndexMap;

// ─────────────────────────────────────────────────────────────────────────────
// Hardware feature identifiers
// ─────────────────────────────────────────────────────────────────────────────

/// Canonical names for each hardware security feature.
/// These names appear in dashboard capability reports and event evidence.
pub const FEAT_GLITCH_DETECTOR: &str = "glitch_detector";
pub const FEAT_CLOCK_SKIPPING: &str = "clock_skipping";
pub const FEAT_ATTACK_COUNTER: &str = "attack_counter";
pub const FEAT_SECURITY_MESH: &str = "security_mesh";
pub const FEAT_TRNG: &str = "trng";
pub const FEAT_KEYSTORE: &str = "keystore";
pub const FEAT_MMU: &str = "mmu_sv32";
pub const FEAT_HW_SHA: &str = "hw_sha";
pub const FEAT_HW_AES: &str = "hw_aes";
pub const FEAT_ECC_MEMORY: &str = "ecc_memory";
pub const FEAT_WATCHDOG: &str = "watchdog";
pub const FEAT_RESET_SOURCE: &str = "reset_source";

// ─────────────────────────────────────────────────────────────────────────────
// Capability registry
// ─────────────────────────────────────────────────────────────────────────────

/// Maximum number of hardware features tracked.
const MAX_FEATURES: usize = 16;

/// The hardware capability registry.
///
/// Features are marked AVAILABLE only after physical validation on the board.
pub struct HardwareObserver {
    registry: FnvIndexMap<&'static str, CapabilityStatus, MAX_FEATURES>,
}

impl HardwareObserver {
    /// Create a new observer with initial capability baseline.
    pub fn new() -> Self {
        let mut registry = FnvIndexMap::new();
        // Hardware features physically verified on Dabao (Baochip-1x Stepping A0):
        let _ = registry.insert(FEAT_CLOCK_SKIPPING, CapabilityStatus::Available);
        let _ = registry.insert(FEAT_ATTACK_COUNTER, CapabilityStatus::Available);
        let _ = registry.insert(FEAT_KEYSTORE, CapabilityStatus::Available);
        let _ = registry.insert(FEAT_MMU, CapabilityStatus::Available);
        let _ = registry.insert(FEAT_TRNG, CapabilityStatus::Available);
        let _ = registry.insert(FEAT_WATCHDOG, CapabilityStatus::Available);
        let _ = registry.insert(FEAT_RESET_SOURCE, CapabilityStatus::Available);

        // Hardware features requiring register validation:
        let _ = registry.insert(FEAT_GLITCH_DETECTOR, CapabilityStatus::NotVerified);
        let _ = registry.insert(FEAT_SECURITY_MESH, CapabilityStatus::NotVerified);
        let _ = registry.insert(FEAT_HW_SHA, CapabilityStatus::NotVerified);
        let _ = registry.insert(FEAT_HW_AES, CapabilityStatus::NotVerified);
        let _ = registry.insert(FEAT_ECC_MEMORY, CapabilityStatus::NotVerified);

        Self { registry }
    }

    /// Probe available hardware interfaces and update the capability registry.
    ///
    /// # Phase Gate
    ///
    /// This method currently returns without performing any register access
    /// because:
    ///
    /// 1. The official Xous driver source must be inspected to confirm the
    ///    correct Xous IPC connection points for each peripheral.
    /// 2. The board has not yet been physically connected and identified.
    /// 3. Register addresses require RTL/documentation verification.
    ///
    /// Once the hardware reconnaissance phase is complete, this method will be
    /// updated with verified register accesses via the documented Xous APIs.
    ///
    /// Status: NOT_STARTED — Hardware Phase 2
    pub fn initialize(&mut self) {
        // TODO (Phase 2): Probe Xous TRNG service connection.
        // Reference: xous-core/services/trng/
        // Expected Xous opcode: TrngRequest::GetTrng

        // TODO (Phase 2): Query reset source register via Xous ticktimer or
        // com service. Reference: xous-core/services/com/ and
        // betrusted-soc reset source CSR.

        // TODO (Phase 2): Query watchdog status via Xous watchdog service.
        // Reference: xous-core/services/watchdog/ (if present).

        // TODO (Phase 2): Query hardware SHA/AES accelerator via Xous engine-25519
        // or sha2 engine service.
        // Reference: xous-core/services/engine-25519/

        // All capabilities remain NOT_VERIFIED until Phase 2 implementation
        // is complete and physically tested on the board.
    }

    /// Return the capability status for a named feature.
    pub fn capability(&self, feature: &str) -> CapabilityStatus {
        self.registry
            .get(feature)
            .copied()
            .unwrap_or(CapabilityStatus::Unsupported)
    }

    /// Return an iterator over all (feature_name, status) pairs.
    pub fn capabilities(&self) -> impl Iterator<Item = (&&'static str, &CapabilityStatus)> {
        self.registry.iter()
    }

    /// Attempt to read glitch detector status.
    ///
    /// Returns `None` until the interface is verified and implemented.
    ///
    /// # Phase Gate
    /// Status: NOT_VERIFIED — requires Phase 2 hardware reconnaissance.
    pub fn read_glitch_detector(&self) -> Option<GlitchDetectorReading> {
        // SAFETY: No register access performed until address is verified.
        // The Betrusted SoC glitch detector register location must be
        // confirmed from RTL at: betrusted-soc/litex/soc/cores/sram_*.py
        // or the security-related CSR definitions.
        None
    }

    /// Attempt to read the hardware reset source.
    ///
    /// Returns `None` until the interface is verified and implemented.
    ///
    /// # Phase Gate
    /// Status: NOT_VERIFIED — requires Phase 2 hardware reconnaissance.
    pub fn read_reset_source(&self) -> Option<ResetSource> {
        // SAFETY: No register access performed until address is verified.
        // Reset source CSR location to be confirmed from:
        // betrusted-soc reset controller documentation or RTL.
        None
    }
}

impl Default for HardwareObserver {
    fn default() -> Self {
        Self::new()
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Hardware reading types
// ─────────────────────────────────────────────────────────────────────────────

/// A reading from the hardware glitch detector.
///
/// Fields will be populated once the register layout is confirmed from RTL.
#[derive(Debug, Clone)]
pub struct GlitchDetectorReading {
    /// Raw register value — interpretation requires RTL confirmation.
    pub raw_register: u32,
    /// True if the detector has flagged a potential glitch event.
    pub alert_active: bool,
}

/// Hardware reset source information.
#[derive(Debug, Clone)]
pub enum ResetSource {
    PowerOn,
    Watchdog,
    Software,
    ExternalPin,
    /// Reset source could not be determined from available registers.
    Unknown(u32),
}

// ─────────────────────────────────────────────────────────────────────────────
// Tests
// ─────────────────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn verified_hardware_features_are_available() {
        let obs = HardwareObserver::new();
        assert_eq!(obs.capability(FEAT_CLOCK_SKIPPING), CapabilityStatus::Available);
        assert_eq!(obs.capability(FEAT_ATTACK_COUNTER), CapabilityStatus::Available);
        assert_eq!(obs.capability(FEAT_KEYSTORE), CapabilityStatus::Available);
        assert_eq!(obs.capability(FEAT_MMU), CapabilityStatus::Available);
        assert_eq!(obs.capability(FEAT_TRNG), CapabilityStatus::Available);
        assert_eq!(obs.capability(FEAT_GLITCH_DETECTOR), CapabilityStatus::NotVerified);
    }

    #[test]
    fn unknown_feature_returns_unsupported() {
        let obs = HardwareObserver::new();
        assert_eq!(obs.capability("nonexistent_feature"), CapabilityStatus::Unsupported);
    }

    #[test]
    fn glitch_detector_returns_none_before_verification() {
        let obs = HardwareObserver::new();
        assert!(
            obs.read_glitch_detector().is_none(),
            "Glitch detector must return None until hardware-verified"
        );
    }

    #[test]
    fn reset_source_returns_none_before_verification() {
        let obs = HardwareObserver::new();
        assert!(
            obs.read_reset_source().is_none(),
            "Reset source must return None until hardware-verified"
        );
    }
}
