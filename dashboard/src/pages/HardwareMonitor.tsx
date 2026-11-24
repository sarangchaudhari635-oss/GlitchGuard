import React from 'react';
import { Cpu, ShieldAlert, CheckCircle2, XCircle, HelpCircle } from 'lucide-react';
import { Badge } from '../components/Badge';

export const HardwareMonitor: React.FC = () => {
  const hardwareFeatures = [
    {
      id: 'glitch_detector',
      name: 'Voltage / Clock Glitch Detector',
      status: 'NOT_VERIFIED',
      description: 'Transient dV/dt and clock edge jitter sensors on the Baochip-1x power rails.',
      xousDriver: 'Xous Custom Service',
      registerRef: 'Betrusted-SoC Glitch CSR (Offset 0x004)',
      notes: 'Hardware attack counter reported 1 attempt during live audit.',
    },
    {
      id: 'security_mesh',
      name: 'Active Security Mesh / Die Shield',
      status: 'NOT_VERIFIED',
      description: 'Continuous serpentine conductive mesh across top metal layers to detect microprobing.',
      xousDriver: 'Security Supervisor Service',
      registerRef: 'Mesh Status Register',
      notes: 'Present in silicon packaging; software status mapping pending RTL check.',
    },
    {
      id: 'trng',
      name: 'True Random Number Generator (TRNG)',
      status: 'AVAILABLE',
      description: 'Hardware ring oscillator avalanche entropy source.',
      xousDriver: 'xous-core/services/trng',
      registerRef: 'TRNG CSR 0x4004_0000',
      notes: 'Active hardware entropy provider for Xous microkernel.',
    },
    {
      id: 'hw_sha',
      name: 'Hardware SHA-256 Engine',
      status: 'NOT_VERIFIED',
      description: 'Cryptographic hashing co-processor for payload verification.',
      xousDriver: 'xous-core/services/engine-25519',
      registerRef: 'SHA Accelerator Base 0x4003_0000',
      notes: 'Software SHA-256 fallback currently verified and active in firmware.',
    },
    {
      id: 'hw_aes',
      name: 'Hardware AES Engine (128/256-bit)',
      status: 'NOT_VERIFIED',
      description: 'Symmetric cryptographic cipher block with side-channel countermeasures.',
      xousDriver: 'xous-core/services/aes',
      registerRef: 'AES Engine Base 0x4003_1000',
      notes: 'Reserved for memory encryption and secure state persistence.',
    },
    {
      id: 'ecc_memory',
      name: 'ECC Protected SRAM',
      status: 'NOT_VERIFIED',
      description: 'Single-bit error correction, double-bit error detection memory bus.',
      xousDriver: 'Memory Manager / MMU',
      registerRef: 'SRAM Controller CSR',
      notes: 'Hardware parity trap maps to Xous MMU fault handler.',
    },
    {
      id: 'watchdog',
      name: 'Hardware Watchdog Timer',
      status: 'AVAILABLE',
      description: 'Windowed hardware countdown timer preventing CPU execution deadlock.',
      xousDriver: 'xous-core/services/watchdog',
      registerRef: 'Watchdog CSR (SoC Reset Block)',
      notes: 'Active in bootloader to recover from instruction stalls.',
    },
    {
      id: 'reset_source',
      name: 'Reset Reason Controller',
      status: 'AVAILABLE',
      description: 'Hardware latch recording cause of previous system reset (POR, WDT, Software).',
      xousDriver: 'xous-core/services/ticktimer',
      registerRef: 'Reset Source Latch 0x4000_0008',
      notes: 'Confirmed accessible via bootloader audit receipts.',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold font-mono tracking-tight text-slate-100">
          Hardware Security Peripherals & Sensors
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Detailed capability matrix and verification status for Baochip-1x on-chip security circuits.
        </p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-950/60">
          <div className="flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-cyan-400" />
            <span className="font-mono text-sm font-semibold text-slate-200">
              Silicon Capability Matrix (Baochip-1x Stepping A0)
            </span>
          </div>
          <Badge label="EPISTEMIC RULE: PHYSICAL VERIFICATION REQUIRED" variant="hardware" />
        </div>

        <div className="divide-y divide-slate-800/80">
          {hardwareFeatures.map((feat) => (
            <div key={feat.id} className="p-5 hover:bg-slate-850/40 transition-colors">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center space-x-3">
                    <span className="font-mono text-base font-bold text-slate-100">{feat.name}</span>
                    <span
                      className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded text-xs font-mono font-semibold ${
                        feat.status === 'AVAILABLE'
                          ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                          : 'bg-amber-950 text-amber-400 border border-amber-800'
                      }`}
                    >
                      {feat.status === 'AVAILABLE' ? (
                        <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                      ) : (
                        <HelpCircle className="w-3.5 h-3.5 mr-1" />
                      )}
                      {feat.status}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1.5">{feat.description}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4 pt-3 border-t border-slate-850 text-xs font-mono">
                <div>
                  <span className="text-slate-500 block">Xous Driver Service</span>
                  <span className="text-slate-300">{feat.xousDriver}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Register / CSR Reference</span>
                  <span className="text-cyan-400">{feat.registerRef}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Physical Observation Notes</span>
                  <span className="text-slate-300">{feat.notes}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
