import React, { useEffect, useState } from 'react';
import { Search, Filter, Radio, Download } from 'lucide-react';
import { Badge } from '../components/Badge';
import { GlitchEvent } from '../types/telemetry';

export const EventExplorer: React.FC = () => {
  const [events, setEvents] = useState<GlitchEvent[]>([]);
  const [filterSource, setFilterSource] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');

  useEffect(() => {
    fetch('/api/events?limit=200')
      .then((r) => r.json())
      .then((data) => setEvents(data))
      .catch(() => {});
  }, []);

  const filtered = events.filter((e) => {
    if (filterSource !== 'all' && e.source !== filterSource) return false;
    if (filterType !== 'all' && e.event_type !== filterType) return false;
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      return (
        e.experiment_id.toLowerCase().includes(term) ||
        e.event_id.toLowerCase().includes(term) ||
        e.event_type.toLowerCase().includes(term)
      );
    }
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold font-mono tracking-tight text-slate-100">
            Security Event Explorer
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Search, filter, and inspect structured telemetry records across physical and simulated domains.
          </p>
        </div>

        <a
          href="/api/reports/latest?format=csv"
          className="flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 text-slate-200 px-3.5 py-2 rounded-lg font-mono text-xs font-semibold border border-slate-700 transition-colors"
        >
          <Download className="w-4 h-4" />
          <span>Export CSV</span>
        </a>
      </div>

      {/* Filters & Search */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-wrap gap-4 items-center justify-between">
        <div className="flex items-center space-x-3 flex-1 min-w-[280px]">
          <div className="relative w-full">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search by experiment ID, event ID, or type..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        <div className="flex items-center space-x-3 text-xs font-mono">
          <div className="flex items-center space-x-2">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-slate-400">Source:</span>
            <select
              value={filterSource}
              onChange={(e) => setFilterSource(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200"
            >
              <option value="all">All Sources</option>
              <option value="hardware_sensor">hardware_sensor</option>
              <option value="software_simulator">software_simulator</option>
              <option value="runtime_monitor">runtime_monitor</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-slate-400">Type:</span>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200"
            >
              <option value="all">All Types</option>
              <option value="NORMAL">NORMAL</option>
              <option value="ANOMALY">ANOMALY</option>
              <option value="INTEGRITY_FAILURE">INTEGRITY_FAILURE</option>
              <option value="HEARTBEAT_TIMEOUT">HEARTBEAT_TIMEOUT</option>
              <option value="RECOVERY">RECOVERY</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Event ID</th>
                <th className="py-3 px-4">Experiment</th>
                <th className="py-3 px-4">Source</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Verification</th>
                <th className="py-3 px-4">Defensive Response</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500">
                    No matching events found. Run experiments to generate telemetry.
                  </td>
                </tr>
              ) : (
                filtered.map((e) => (
                  <tr key={e.event_id} className="hover:bg-slate-850/50">
                    <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                      {e.event_id.slice(0, 8)}...
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-200">{e.experiment_id}</td>
                    <td className="py-3 px-4">
                      <Badge
                        label={e.source === 'software_simulator' ? 'SIMULATED' : 'HARDWARE'}
                        variant={e.source === 'software_simulator' ? 'simulated' : 'hardware'}
                      />
                    </td>
                    <td className="py-3 px-4 font-medium text-slate-200">{e.event_type}</td>
                    <td className="py-3 px-4">
                      <span className={e.severity === 'CRITICAL' ? 'text-rose-400 font-bold' : e.severity === 'HIGH' ? 'text-amber-400' : 'text-slate-400'}>
                        {e.severity}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={e.verification_status === 'PASSED' ? 'text-emerald-400' : e.verification_status === 'FAILED' ? 'text-rose-400' : 'text-slate-500'}>
                        {e.verification_status}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <Badge
                        label={e.response}
                        variant={e.response === 'QUARANTINED' ? 'quarantined' : e.response === 'RECOVERED' ? 'recovered' : e.response === 'LOCKDOWN' ? 'critical' : 'normal'}
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
