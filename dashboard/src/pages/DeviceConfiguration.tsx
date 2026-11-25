import React, { useState } from 'react';
import { Settings, Cpu, HardDrive, Shield, Terminal, Send, CheckCircle2, AlertCircle } from 'lucide-react';
import { Badge } from '../components/Badge';
import { pingDevice, requestDeviceStatus, requestDeviceCapabilities, DeviceInfo, ConnectionDiagnostics } from '../services/api';

interface DeviceConfigurationProps {
  deviceInfo?: DeviceInfo | null;
  diagnostics?: ConnectionDiagnostics | null;
}

export const DeviceConfiguration: React.FC<DeviceConfigurationProps> = ({
  deviceInfo = null,
  diagnostics = null,
}) => {
  const [consoleOutput, setConsoleOutput] = useState<string>(
    'GLITCHGUARD Hardware Interrogation Console Ready.\nConnected to Baochip-1x silicon.\n'
  );
  const [commandInProgress, setCommandInProgress] = useState<boolean>(false);

  const runCommand = async (name: string, apiFunc: () => Promise<any>) => {
    setCommandInProgress(true);
    setConsoleOutput((prev) => `${prev}\n> EXEC: ${name} ...\n`);
    try {
      const res = await apiFunc();
      const outputText = res.response || res.message || JSON.stringify(res, null, 2);
      setConsoleOutput((prev) => `${prev}${outputText}\n[Status: ${res.status || 'OK'}]\n`);
    } catch (err: any) {
      setConsoleOutput((prev) => `${prev}ERROR: ${err.message || String(err)}\n`);
    } finally {
      setCommandInProgress(false);
    }
  };

  const selectedPort = diagnostics?.selected_port || 'COM10';
  const baudRate = diagnostics?.baudrate || 115200;
  const serialNum = deviceInfo?.public_serial || 'NNBT1T';
  const bootloaderVer = deviceInfo?.bootloader_ver || 'v0.10.0-61-g5397e1b48';

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

      {/* Hardware Connection Card */}
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
              <span className="text-slate-200 font-bold text-sm">{selectedPort} (USB Serial Device)</span>
            </div>
            <div>
              <span className="text-slate-500 block">Baud Rate</span>
              <span className="text-slate-200 font-bold text-sm">{baudRate} Baud (8N1)</span>
            </div>
            <div>
              <span className="text-slate-500 block">USB Vendor ID : Product ID</span>
              <span className="text-cyan-400 font-bold text-sm">1D50 : 6196 (Openmoko / Betrusted)</span>
            </div>
          </div>

          <div className="space-y-3">
            <div>
              <span className="text-slate-500 block">Public Serial Number</span>
              <span className="text-slate-200 font-bold text-sm">{serialNum}</span>
            </div>
            <div>
              <span className="text-slate-500 block">Bootloader Version</span>
              <span className="text-slate-200 font-bold text-sm">{bootloaderVer}</span>
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

      {/* Interactive Hardware Interrogation Console */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <Terminal className="w-5 h-5 text-indigo-400" />
            <h3 className="font-mono text-base font-bold text-slate-100">
              Direct Physical Silicon Interrogation Console
            </h3>
          </div>
          <span className="text-xs font-mono text-slate-400">Non-Destructive Safe Commands Only</span>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => runCommand('PING (echo PONG)', pingDevice)}
            disabled={commandInProgress}
            className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-mono text-cyan-300 border border-slate-700 transition-colors flex items-center space-x-1.5 disabled:opacity-50"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Send PING</span>
          </button>

          <button
            onClick={() => runCommand('GET_STATUS (audit / ver xous)', requestDeviceStatus)}
            disabled={commandInProgress}
            className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-mono text-emerald-300 border border-slate-700 transition-colors flex items-center space-x-1.5 disabled:opacity-50"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Query Device Status</span>
          </button>

          <button
            onClick={() => runCommand('GET_CAPABILITIES (skipping check / test proc)', requestDeviceCapabilities)}
            disabled={commandInProgress}
            className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-mono text-indigo-300 border border-slate-700 transition-colors flex items-center space-x-1.5 disabled:opacity-50"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Query Hardware Capabilities</span>
          </button>
        </div>

        <div className="bg-slate-950 rounded-lg p-4 font-mono text-xs text-slate-300 border border-slate-850 h-56 overflow-y-auto whitespace-pre-wrap font-mono">
          {consoleOutput}
        </div>
      </div>
    </div>
  );
};
