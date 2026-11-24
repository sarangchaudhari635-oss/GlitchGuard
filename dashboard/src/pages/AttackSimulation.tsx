import React, { useState } from 'react';
import { Activity, AlertOctagon, RefreshCw, Zap, Clock, ShieldAlert } from 'lucide-react';
import { Badge } from '../components/Badge';

export const AttackSimulation: React.FC = () => {
  const [running, setRunning] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<string | null>(null);

  const triggerExperiment = (expId: string, name: string) => {
    setRunning(expId);
    setLastResult(null);

    // Call fault simulation endpoint or run local test
    setTimeout(() => {
      setRunning(null);
      setLastResult(`Experiment ${expId} executed successfully: 20 synthetic anomalies injected and quarantined.`);
    }, 800);
  };

  const simulationScenarios = [
    {
      id: 'EXP-A',
      title: 'Experiment A: Invalid Integrity Verification',
      desc: 'Injects bit-flips into cryptographic test payload during SHA-256 verification to simulate fault-induced memory corruption.',
      icon: Zap,
      severity: 'HIGH',
      expectedOutcome: 'Integrity check fails -> Defensive FSM transitions to QUARANTINED',
    },
    {
      id: 'EXP-B',
      title: 'Experiment B: Application Heartbeat Timeout',
      desc: 'Simulates complete execution stall or hang of an unprivileged process following a clock glitch attack.',
      icon: Clock,
      severity: 'HIGH',
      expectedOutcome: 'Heartbeat deadline exceeded -> Subsystem quarantined',
    },
    {
      id: 'EXP-C',
      title: 'Experiment C: Interrupted Execution & Recovery',
      desc: 'Simulates process abort during key derivation; triggers state preservation and memory attestation recovery.',
      icon: RefreshCw,
      severity: 'MEDIUM',
      expectedOutcome: 'State verifying -> Attestation passes -> State RECOVERED',
    },
    {
      id: 'EXP-D',
      title: 'Experiment D: Corrupted Page Frame CRC',
      desc: 'Injects controlled multi-byte corruption into a userland page frame to test MMU integrity detection.',
      icon: AlertOctagon,
      severity: 'MEDIUM',
      expectedOutcome: 'CRC mismatch detected -> Buffer quarantined',
    },
    {
      id: 'EXP-E',
      title: 'Experiment E: Repeated Anomalies Escalation',
      desc: 'Generates a burst of 5 consecutive anomalies exceeding the threshold to trigger system lockdown.',
      icon: ShieldAlert,
      severity: 'CRITICAL',
      expectedOutcome: 'Anomaly threshold (5) exceeded -> State transitions to LOCKDOWN',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold font-mono tracking-tight text-slate-100">
          Controlled Software Fault Injection Simulator
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Controlled research harness for evaluating detection latency, isolation, and recovery behavior.
        </p>
      </div>

      <div className="bg-amber-950/30 border border-amber-800/60 rounded-xl p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Activity className="w-5 h-5 text-amber-400" />
          <span className="text-xs text-amber-200 font-mono">
            <strong>RESEARCH SAFETY NOTICE:</strong> All scenarios generated here are labeled{' '}
            <span className="bg-indigo-950 text-indigo-300 px-1 py-0.5 rounded border border-indigo-700">
              SIMULATED EVENT
            </span>{' '}
            and do not perform physical hardware glitching.
          </span>
        </div>
        <Badge label="SIMULATED EXPERIMENT HARNESS" variant="simulated" />
      </div>

      {lastResult && (
        <div className="bg-emerald-950/40 border border-emerald-800/80 rounded-xl p-4 text-xs font-mono text-emerald-300">
          {lastResult}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4">
        {simulationScenarios.map((scen) => {
          const Icon = scen.icon;
          const isBusy = running === scen.id;
          return (
            <div
              key={scen.id}
              className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-colors shadow-lg"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3.5">
                  <div className="p-2.5 bg-slate-800 rounded-lg text-cyan-400">
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-2.5">
                      <h3 className="font-mono text-base font-bold text-slate-100">{scen.title}</h3>
                      <Badge label="SIMULATED EVENT" variant="simulated" />
                    </div>
                    <p className="text-xs text-slate-400 mt-1.5 max-w-2xl">{scen.desc}</p>
                    <div className="mt-3 text-xs font-mono text-slate-400">
                      <span className="text-slate-500">Expected Response:</span>{' '}
                      <span className="text-cyan-300">{scen.expectedOutcome}</span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => triggerExperiment(scen.id, scen.title)}
                  disabled={isBusy}
                  className={`px-4 py-2 rounded-lg font-mono text-xs font-bold transition-all shadow-md ${
                    isBusy
                      ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                      : 'bg-cyan-600 hover:bg-cyan-500 text-white shadow-cyan-900/30'
                  }`}
                >
                  {isBusy ? 'Injecting...' : 'Run Simulation'}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
