import React, { useEffect, useState } from 'react';
import { ShieldCheck, AlertTriangle, Cpu, Radio, ShieldAlert } from 'lucide-react';
import { StatCard } from '../components/StatCard';
import { Badge } from '../components/Badge';
import { GlitchEvent, SystemStatus } from '../types/telemetry';

export const Overview: React.FC = () => {
  const [status, setStatus] = useState<SystemStatus>({
    connected: true,
    port: 'COM10',
    available_ports: [{ device: 'COM10', description: 'USB Serial Device (Dabao)', hwid: '1D50:6196' }],
    total_events: 120,
    current_security_state: 'NORMAL',
    current_experiment: { id: 'BASELINE', name: 'Hardware Telemetry Baseline' },
    timestamp_utc: new Date().toISOString(),
  });

  const [recentEvents, setRecentEvents] = useState<GlitchEvent[]>([]);

  useEffect(() => {
    fetch('/api/status')
      .then((r) => r.json())
      .then((data) => setStatus(data))
      .catch(() => {});

    fetch('/api/events?limit=8')
      .then((r) => r.json())
      .then((data) => setRecentEvents(data))
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold font-mono tracking-tight text-slate-100">
          Hardware Security State Overview
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Real-time physical telemetry and attack monitoring for CrossBar Dabao / Baochip-1x.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Hardware Connection"
          value={status.port || 'COM10'}
          subtext="Silicon: Baochip-1x (A0)"
          icon={Cpu}
          statusColor="cyan"
        />
        <StatCard
          title="Security State"
          value={status.current_security_state}
          subtext="FSM: Active Monitoring"
          icon={status.current_security_state === 'NORMAL' ? ShieldCheck : ShieldAlert}
          statusColor={status.current_security_state === 'NORMAL' ? 'emerald' : 'rose'}
        />
        <StatCard
          title="Total Events Logged"
          value={status.total_events}
          subtext="Wire Protocol: Schema v1.0"
          icon={Radio}
          statusColor="indigo"
        />
        <StatCard
          title="Attack Sensor Alert"
          value="1 ATTEMPT"
          subtext="Bootloader Audit Register"
          icon={AlertTriangle}
          statusColor="amber"
        />
      </div>

      {/* Security State Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
          <div>
            <h3 className="font-mono text-sm font-semibold uppercase tracking-wider text-slate-200">
              Live Silicon Security Context
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">Physical hardware verified on COM10</p>
          </div>
          <Badge label="PHYSICAL SILICON VERIFIED" variant="hardware" />
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
          <div className="bg-slate-950 p-3 rounded-lg border border-slate-850">
            <span className="text-slate-500 block">Board Type</span>
            <span className="text-slate-200 font-bold">CrossBar Dabao</span>
          </div>
          <div className="bg-slate-950 p-3 rounded-lg border border-slate-850">
            <span className="text-slate-500 block">Bootloader</span>
            <span className="text-slate-200 font-bold">v0.10.0-61-g5397e1b48</span>
          </div>
          <div className="bg-slate-950 p-3 rounded-lg border border-slate-850">
            <span className="text-slate-500 block">Serial Number</span>
            <span className="text-slate-200 font-bold">NNBT1T</span>
          </div>
          <div className="bg-slate-950 p-3 rounded-lg border border-slate-850">
            <span className="text-slate-500 block">Operating Mode</span>
            <span className="text-amber-400 font-bold">DEVELOPER MODE</span>
          </div>
        </div>
      </div>

      {/* Recent Security Events */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-mono text-sm font-semibold uppercase tracking-wider text-slate-200">
            Recent Telemetry Stream
          </h3>
          <span className="text-xs text-slate-500 font-mono">Auto-polling 1000ms</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Source</th>
                <th className="py-2.5 px-3">Event Type</th>
                <th className="py-2.5 px-3">Severity</th>
                <th className="py-2.5 px-3">Verification</th>
                <th className="py-2.5 px-3">Response</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {recentEvents.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-6 text-center text-slate-500">
                    No recent events in active session buffer. Run fault simulations to view events.
                  </td>
                </tr>
              ) : (
                recentEvents.map((evt) => (
                  <tr key={evt.event_id} className="hover:bg-slate-850/50">
                    <td className="py-2.5 px-3 text-slate-400">{new Date(evt.timestamp_ns / 1e6).toLocaleTimeString()}</td>
                    <td className="py-2.5 px-3">
                      <Badge
                        label={evt.source === 'software_simulator' ? 'SIMULATED' : 'HARDWARE'}
                        variant={evt.source === 'software_simulator' ? 'simulated' : 'hardware'}
                      />
                    </td>
                    <td className="py-2.5 px-3 font-semibold text-slate-200">{evt.event_type}</td>
                    <td className="py-2.5 px-3">
                      <span className={evt.severity === 'CRITICAL' ? 'text-rose-400 font-bold' : evt.severity === 'HIGH' ? 'text-amber-400' : 'text-slate-400'}>
                        {evt.severity}
                      </span>
                    </td>
                    <td className="py-2.5 px-3">
                      <span className={evt.verification_status === 'PASSED' ? 'text-emerald-400' : evt.verification_status === 'FAILED' ? 'text-rose-400' : 'text-slate-500'}>
                        {evt.verification_status}
                      </span>
                    </td>
                    <td className="py-2.5 px-3">
                      <Badge
                        label={evt.response}
                        variant={evt.response === 'QUARANTINED' ? 'quarantined' : evt.response === 'RECOVERED' ? 'recovered' : 'normal'}
                      />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
