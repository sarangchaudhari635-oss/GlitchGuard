import React from 'react';
import { Settings, Cpu, HardDrive, Shield } from 'lucide-react';
import { Badge } from '../components/Badge';

export const DeviceConfiguration: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold font-mono tracking-tight text-slate-100">
          Device Configuration & Serial Bus Parameters
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Hardware interface settings, communication rates, and non-destructive flashing checkpoints.
        </p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
        <div className="flex items-center space-x-3 mb-4 pb-3 border-b border-slate-800">
          <Cpu className="w-5 h-5 text-cyan-400" />
          <h3 className="font-mono text-base font-bold text-slate-100">
            Physical Silicon Connection Parameters
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs font-mono">
          <div className="space-y-3">
            <div>
              <span className="text-slate-500 block">Serial Device Port</span>
              <span className="text-slate-200 font-bold text-sm">COM10 (USB Serial Device)</span>
            </div>
            <div>
              <span className="text-slate-500 block">Baud Rate</span>
              <span className="text-slate-200 font-bold text-sm">115200 Baud (8N1)</span>
            </div>
            <div>
              <span className="text-slate-500 block">USB Vendor ID : Product ID</span>
              <span className="text-cyan-400 font-bold text-sm">1D50 : 6196 (Openmoko / Betrusted)</span>
            </div>
          </div>

          <div className="space-y-3">
            <div>
              <span className="text-slate-500 block">Public Serial Number</span>
              <span className="text-slate-200 font-bold text-sm">NNBT1T</span>
            </div>
            <div>
              <span className="text-slate-500 block">Wafer Lot Tracking ID</span>
              <span className="text-slate-200 font-bold text-sm">47521066M06T</span>
            </div>
            <div>
              <span className="text-slate-500 block">Target Application Partition</span>
              <span className="text-emerald-400 font-bold text-sm">0x60060000 (key 3/3 dev)</span>
            </div>
          </div>
        </div>

        <div className="mt-6 pt-4 border-t border-slate-800 bg-slate-950/60 -mx-6 -mb-6 p-6 rounded-b-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs font-mono text-slate-400">
              <Shield className="w-4 h-4 text-emerald-400" />
              <span>Flash Protection: Boot0 (0x60000000) & Boot1 (0x60020000) are hardware write-protected.</span>
            </div>
            <Badge label="DEVELOPER MODE ACTIVE" variant="hardware" />
          </div>
        </div>
      </div>
    </div>
  );
};
