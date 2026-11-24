import React from 'react';
import { 
  ShieldAlert, 
  Cpu, 
  Activity, 
  Radio, 
  BarChart3, 
  FileText, 
  Settings,
  Circle
} from 'lucide-react';

interface NavbarProps {
  currentPage: string;
  onSelectPage: (page: string) => void;
  hardwareConnected: boolean;
  port: string | null;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentPage,
  onSelectPage,
  hardwareConnected,
  port,
}) => {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: ShieldAlert },
    { id: 'hardware', label: 'Hardware Monitor', icon: Cpu },
    { id: 'simulation', label: 'Attack Simulation', icon: Activity },
    { id: 'events', label: 'Event Explorer', icon: Radio },
    { id: 'analytics', label: 'Experiment Analytics', icon: BarChart3 },
    { id: 'reports', label: 'Research Reports', icon: FileText },
    { id: 'config', label: 'Device Configuration', icon: Settings },
  ];

  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-600 to-indigo-600 flex items-center justify-center font-bold text-white shadow-cyan-900/40 shadow-md">
              GG
            </div>
            <div>
              <span className="font-mono font-bold text-lg text-slate-100 tracking-wider">GLITCHGUARD</span>
              <span className="block text-[10px] text-cyan-400 font-mono tracking-tight">CrossBar Dabao · Baochip-1x</span>
            </div>
          </div>

          <nav className="flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectPage(item.id)}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    isActive
                      ? 'bg-slate-800 text-cyan-400 border border-slate-700 shadow-inner'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          <div className="flex items-center space-x-2 bg-slate-950/80 px-3 py-1.5 rounded-full border border-slate-800">
            <Circle className={`w-2.5 h-2.5 fill-current ${hardwareConnected ? 'text-emerald-400 animate-pulse' : 'text-slate-600'}`} />
            <span className="text-[11px] font-mono text-slate-300">
              {hardwareConnected ? `SILICON: ${port || 'CONNECTED'}` : 'DISCONNECTED'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
