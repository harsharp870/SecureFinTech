import React, { useState } from 'react';
import { useAuth } from './context/AuthContext';
import { Login } from './components/Login';
import { Signup } from './components/Signup';
import { UserPortal } from './components/UserPortal';
import { AdminConsole } from './components/AdminConsole';
import { XAIModal } from './components/XAIModal';

export const AppContent: React.FC = () => {
  const { user, loading } = useAuth();
  const [authView, setAuthView] = useState<'login' | 'signup'>('login');
  const [activeXAIModalTxId, setActiveXAIModalTxId] = useState<string | null>(null);

  if (loading) {
    return (
      <div style={{ display: 'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-cyan)' }}>
        <p style={{ fontSize: '1.2rem', fontWeight: '600' }}>Loading SecureFinTech Security Portal...</p>
      </div>
    );
  }

  if (!user) {
    if (authView === 'signup') {
      return <Signup onSwitchToLogin={() => setAuthView('login')} />;
    }
    return <Login onSwitchToSignup={() => setAuthView('signup')} />;
  }

  return (
    <>
      {user.role === 'ADMIN' ? (
        <AdminConsole onOpenXAI={(txId) => setActiveXAIModalTxId(txId)} />
      ) : (
        <UserPortal onOpenXAI={(txId) => setActiveXAIModalTxId(txId)} />
      )}

      {activeXAIModalTxId && (
        <XAIModal
          transactionId={activeXAIModalTxId}
          onClose={() => setActiveXAIModalTxId(null)}
        />
      )}
    </>
  );
};

export default function App() {
  return <AppContent />;
}
