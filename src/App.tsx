import React from 'react';
import { DemoProvider, useDemo } from './context/DemoContext';
import { Sidebar } from './components/common/Sidebar';
import { Header } from './components/common/Header';
import { ToastContainer } from './components/common/ToastContainer';

import { LandingPage } from './pages/LandingPage';
import { OverviewPage } from './pages/OverviewPage';
import { AgentsPage } from './pages/AgentsPage';
import { ThreatsPage } from './pages/ThreatsPage';
import { CostUsagePage } from './pages/CostUsagePage';
import { DigitalTwinPage } from './pages/DigitalTwinPage';
import { PoliciesPage } from './pages/PoliciesPage';
import { AttackSimulatorPage } from './pages/AttackSimulatorPage';

import { ThreatDetailModal } from './components/modals/ThreatDetailModal';
import { AgentDetailModal } from './components/modals/AgentDetailModal';

const AppContent: React.FC = () => {
  const { activeTab } = useDemo();

  if (activeTab === 'landing') {
    return (
      <>
        <LandingPage />
        <ToastContainer />
      </>
    );
  }

  return (
    <div className="flex min-h-screen bg-[#050811] text-slate-200 selection:bg-cyan-500/30 selection:text-cyan-200 font-sans">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header />

        <main className="flex-1 p-6 overflow-y-auto bg-cyber-grid">
          <div className="max-w-7xl mx-auto space-y-6">
            {activeTab === 'overview' && <OverviewPage />}
            {activeTab === 'agents' && <AgentsPage />}
            {activeTab === 'threats' && <ThreatsPage />}
            {activeTab === 'cost-usage' && <CostUsagePage />}
            {activeTab === 'digital-twin' && <DigitalTwinPage />}
            {activeTab === 'policies' && <PoliciesPage />}
            {activeTab === 'attack-simulator' && <AttackSimulatorPage />}
          </div>
        </main>
      </div>

      {/* Modals & Toast Notifications */}
      <ThreatDetailModal />
      <AgentDetailModal />
      <ToastContainer />
    </div>
  );
};

export function App() {
  return (
    <DemoProvider>
      <AppContent />
    </DemoProvider>
  );
}

export default App;
