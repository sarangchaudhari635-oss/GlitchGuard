import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Overview } from './pages/Overview';
import { HardwareMonitor } from './pages/HardwareMonitor';
import { AttackSimulation } from './pages/AttackSimulation';
import { EventExplorer } from './pages/EventExplorer';
import { ExperimentAnalytics } from './pages/ExperimentAnalytics';
import { ResearchReports } from './pages/ResearchReports';
import { DeviceConfiguration } from './pages/DeviceConfiguration';

export const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<string>('overview');

  const renderPage = () => {
    switch (currentPage) {
      case 'overview':
        return <Overview />;
      case 'hardware':
        return <HardwareMonitor />;
      case 'simulation':
        return <AttackSimulation />;
      case 'events':
        return <EventExplorer />;
      case 'analytics':
        return <ExperimentAnalytics />;
      case 'reports':
        return <ResearchReports />;
      case 'config':
        return <DeviceConfiguration />;
      default:
        return <Overview />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar
        currentPage={currentPage}
        onSelectPage={setCurrentPage}
        hardwareConnected={true}
        port="COM10"
      />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderPage()}
      </main>
      <footer className="border-t border-slate-900 bg-slate-950/80 py-4 text-center text-xs font-mono text-slate-500">
        GLITCHGUARD Open-Silicon Security Framework · CrossBar Dabao / Baochip-1x · MIT License
      </footer>
    </div>
  );
};

export default App;
