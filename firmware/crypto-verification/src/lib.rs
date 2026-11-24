//! crypto-verification — Cryptographic integrity verification for GlitchGuard.
//!
//! # Implementation Strategy
//!
//! 1. **Hardware-accelerated path (Phase 5):** Use the Xous engine service for
//!    SHA-256 acceleration, once the interface is confirmed from RTL and the
//!    Xous crate API is verified. Status: NOT_VERIFIED.
//!
//! 2. **Software fallback (active now):** Use the `sha2` crate for SHA-256
//!    in software. This is the current implementation.
//!
//! Every verification report includes `hardware_accelerated: bool` so that
//! the host backend and dashboard can clearly show which path was used.
//!
//! # Key Safety Rules
//!
//! - Never log or transmit private keys or TRNG seeds.
//! - Hardware acceleration must be physically verified before claiming it.
//! - Software fallback is never presented as hardware-accelerated.

#![no_std]
#![forbid(unsafe_code)]

use digest::Digest;
use sha2::Sha256;

// ─────────────────────────────────────────────────────────────────────────────
// Output types
// ─────────────────────────────────────────────────────────────────────────────

/// A 32-byte SHA-256 digest.
pub type Sha256Digest = [u8; 32];

/// Result of an integrity verification operation.
#[derive(Debug, Clone)]
pub struct VerificationReport {
    /// Whether the hash matched the expected value.
    pub passed: bool,
    /// Whether hardware acceleration was used.
    /// Must be `false` until hardware path is physically verified.
    pub hardware_accelerated: bool,
    /// The computed hash of the payload.
    pub computed_hash: Sha256Digest,
    /// The expected hash provided by the caller.
    pub expected_hash: Sha256Digest,
    /// Algorithm identifier for the event evidence record.
    pub algorithm: &'static str,
}

// ─────────────────────────────────────────────────────────────────────────────
// Verifier
// ─────────────────────────────────────────────────────────────────────────────

pub struct CryptoVerifier {
    /// True only after hardware acceleration is physically verified.
    hardware_available: bool,
}

impl CryptoVerifier {
    /// Create a new verifier.
    ///
    /// `hardware_available` must only be set to `true` after the Xous engine
    /// service interface is confirmed and the hardware path is physically
    /// validated on the board. Default: software fallback only.
    pub fn new(hardware_available: bool) -> Self {
        Self { hardware_available }
    }

    /// Compute SHA-256 of the given payload using the available backend.
    pub fn hash(&self, payload: &[u8]) -> Sha256Digest {
        if self.hardware_available {
            // TODO (Phase 5): Call Xous engine service for hardware SHA-256.
            // Reference: xous-core/services/engine-25519/
            // Status: NOT_VERIFIED — using software fallback until confirmed.
            self.software_sha256(payload)
        } else {
            self.software_sha256(payload)
        }
    }

    /// Verify that the SHA-256 of `payload` matches `expected_hash`.
    pub fn verify(&self, payload: &[u8], expected_hash: Sha256Digest) -> VerificationReport {
        let computed = self.hash(payload);
        let passed = constant_time_eq(&computed, &expected_hash);
        VerificationReport {
            passed,
            hardware_accelerated: false, // Software only until Phase 5
            computed_hash: computed,
            expected_hash,
            algorithm: "SHA-256",
        }
    }

    /// Generate a simple integrity check for a test payload.
    ///
    /// This computes SHA-256 of the payload and stores it as the expected value.
    /// A subsequent call to `verify_test_payload` can confirm the payload hasn't
    /// been modified.
    pub fn hash_test_payload(&self, payload: &[u8]) -> Sha256Digest {
        self.hash(payload)
    }

    /// Verify a test payload against a previously computed hash.
    /// Returns true if the payload is unmodified.
    pub fn verify_test_payload(&self, payload: &[u8], original_hash: Sha256Digest) -> VerificationReport {
        self.verify(payload, original_hash)
    }

    // ── Private ──────────────────────────────────────────────────────────────

    fn software_sha256(&self, payload: &[u8]) -> Sha256Digest {
        let mut hasher = Sha256::new();
        hasher.update(payload);
        let result = hasher.finalize();
        let mut out = [0u8; 32];
        out.copy_from_slice(&result);
        out
    }
}

impl Default for CryptoVerifier {
    fn default() -> Self {
        Self::new(false) // Always default to software-only
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Constant-time comparison (resistance to timing side-channels)
// ─────────────────────────────────────────────────────────────────────────────

/// Compare two 32-byte slices in constant time.
/// This prevents timing-based side-channel attacks on hash comparison.
fn constant_time_eq(a: &[u8; 32], b: &[u8; 32]) -> bool {
    let mut diff = 0u8;
    for i in 0..32 {
        diff |= a[i] ^ b[i];
    }
    diff == 0
}

// ─────────────────────────────────────────────────────────────────────────────
// Tests
// ─────────────────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hash_is_deterministic() {
        let verifier = CryptoVerifier::default();
        let payload = b"glitchguard-test-payload-001";
        let h1 = verifier.hash(payload);
        let h2 = verifier.hash(payload);
        assert_eq!(h1, h2);
    }

    #[test]
    fn verification_passes_on_unmodified_payload() {
        let verifier = CryptoVerifier::default();
        let payload = b"test payload for integrity check";
        let expected = verifier.hash_test_payload(payload);
        let report = verifier.verify_test_payload(payload, expected);
        assert!(report.passed, "Unmodified payload must verify");
        assert!(!report.hardware_accelerated, "Hardware acceleration not yet verified");
    }

    #[test]
    fn verification_fails_on_modified_payload() {
        let verifier = CryptoVerifier::default();
        let original = b"original payload data";
        let modified = b"modified payload data";
        let expected = verifier.hash_test_payload(original);
        let report = verifier.verify_test_payload(modified, expected);
        assert!(!report.passed, "Modified payload must fail verification");
    }

    #[test]
    fn constant_time_eq_works() {
        let a = [0u8; 32];
        let mut b = [0u8; 32];
        assert!(constant_time_eq(&a, &b));
        b[31] = 1;
        assert!(!constant_time_eq(&a, &b));
    }

    #[test]
    fn hardware_accelerated_is_false_until_verified() {
        let verifier = CryptoVerifier::default();
        let report = verifier.verify(b"payload", [0u8; 32]);
        assert!(
            !report.hardware_accelerated,
            "hardware_accelerated must be false until physically verified on board"
        );
    }
}
