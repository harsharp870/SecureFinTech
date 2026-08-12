import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import {
  Wallet,
  Send,
  History,
  ShieldAlert,
  PlusCircle,
  ArrowUpRight,
  ArrowDownLeft,
  LogOut,
  RefreshCw,
  AlertOctagon,
  CheckCircle2,
  AlertTriangle,
  Info
} from 'lucide-react';

interface WalletData {
  id: string;
  user_id: string;
  balance: number;
  currency: string;
}

interface TransactionItem {
  id: string;
  reference_id: string;
  sender_id: string;
  recipient_id: string;
  amount: number;
  currency: string;
  status: 'PENDING' | 'APPROVED' | 'FLAGGED' | 'BLOCKED' | 'FAILED';
  risk_score: number;
  risk_level: string;
  failure_reason?: string;
  note?: string;
  created_at: string;
}

interface UserPortalProps {
  onOpenXAI: (txId: string) => void;
}

export const UserPortal: React.FC<UserPortalProps> = ({ onOpenXAI }) => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<'wallet' | 'transfer' | 'history'>('wallet');
  
  const [wallet, setWallet] = useState<WalletData | null>(null);
  const [transactions, setTransactions] = useState<TransactionItem[]>([]);
  const [loadingWallet, setLoadingWallet] = useState(true);
  const [loadingTx, setLoadingTx] = useState(true);

  // Transfer form state
  const [recipientEmail, setRecipientEmail] = useState('');
  const [amount, setAmount] = useState('');
  const [note, setNote] = useState('');
  const [transferResult, setTransferResult] = useState<TransactionItem | null>(null);
  const [transferError, setTransferError] = useState('');
  const [submittingTransfer, setSubmittingTransfer] = useState(false);

  // Deposit modal state
  const [depositAmount, setDepositAmount] = useState('1000');
  const [showDepositModal, setShowDepositModal] = useState(false);
  const [submittingDeposit, setSubmittingDeposit] = useState(false);

  // History filter state
  const [directionFilter, setDirectionFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('');

  const fetchWallet = async () => {
    try {
      setLoadingWallet(true);
      const data = await apiFetch<WalletData>('/wallet/me');
      setWallet(data);
    } catch (err) {
      console.error('Failed to load wallet:', err);
    } finally {
      setLoadingWallet(false);
    }
  };

  const fetchTransactions = async () => {
    try {
      setLoadingTx(true);
      let query = `/payments/history?page=1&size=20&direction=${directionFilter}`;
      if (statusFilter) {
        query += `&status=${statusFilter}`;
      }
      const data = await apiFetch<{ items: TransactionItem[] }>(query);
      setTransactions(data.items || []);
    } catch (err) {
      console.error('Failed to load transactions:', err);
    } finally {
      setLoadingTx(false);
    }
  };

  useEffect(() => {
    fetchWallet();
    fetchTransactions();
  }, [directionFilter, statusFilter]);

  const handleDeposit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingDeposit(true);
    try {
      await apiFetch('/wallet/deposit', {
        method: 'POST',
        body: JSON.stringify({ amount: parseFloat(depositAmount) }),
      });
      setShowDepositModal(false);
      await fetchWallet();
    } catch (err: any) {
      alert(err.message || 'Deposit failed');
    } finally {
      setSubmittingDeposit(false);
    }
  };

  const handleTransfer = async (e: React.FormEvent) => {
    e.preventDefault();
    setTransferError('');
    setTransferResult(null);
    setSubmittingTransfer(true);

    try {
      const res = await apiFetch<TransactionItem>('/payments/transfer', {
        method: 'POST',
        body: JSON.stringify({
          recipient_email: recipientEmail,
          amount: parseFloat(amount),
          note: note || undefined,
        }),
      });
      setTransferResult(res);
      setRecipientEmail('');
      setAmount('');
      setNote('');
      await fetchWallet();
      await fetchTransactions();
    } catch (err: any) {
      setTransferError(err.message || 'Transfer failed');
    } finally {
      setSubmittingTransfer(false);
    }
  };

  const formatMoney = (val: number) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
  };

  const formatDate = (isoStr: string) => {
    return new Date(isoStr).toLocaleString();
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return <span className="badge badge-approved"><CheckCircle2 size={12} /> Approved</span>;
      case 'FLAGGED':
        return <span className="badge badge-flagged"><AlertTriangle size={12} /> Flagged</span>;
      case 'BLOCKED':
        return <span className="badge badge-blocked"><AlertOctagon size={12} /> Blocked</span>;
      default:
        return <span className="badge badge-medium"><Info size={12} /> {status}</span>;
    }
  };

  return (
    <div style={{ minHeight: '100vh', padding: '1.5rem', maxWidth: '1200px', margin: '0 auto' }}>
      <header className="glass-card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem', padding: '1.25rem 2rem' }}>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ width: '44px', height: '44px', borderRadius: '12px', background: 'rgba(0, 242, 254, 0.15)', color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Wallet size={24} />
          </div>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: '700' }}>SecureFinTech Portal</h1>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Welcome, {user?.full_name} ({user?.email})</p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span className="badge badge-low" style={{ padding: '0.4rem 0.8rem' }}>Role: {user?.role}</span>
          <button onClick={logout} className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem' }}>
            <LogOut size={16} /> <span>Sign Out</span>
          </button>
        </div>
      </header>

      {/* Main Navigation Tabs */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
        <button
          onClick={() => setActiveTab('wallet')}
          className={activeTab === 'wallet' ? 'btn-primary' : 'btn-secondary'}
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
        >
          <Wallet size={18} /> <span>Wallet Overview</span>
        </button>
        <button
          onClick={() => setActiveTab('transfer')}
          className={activeTab === 'transfer' ? 'btn-primary' : 'btn-secondary'}
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
        >
          <Send size={18} /> <span>Send Money</span>
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={activeTab === 'history' ? 'btn-primary' : 'btn-secondary'}
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
        >
          <History size={18} /> <span>Transaction History</span>
        </button>
      </div>

      {/* TAB 1: WALLET OVERVIEW */}
      {activeTab === 'wallet' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
          <div className="glass-card" style={{ padding: '2rem', background: 'linear-gradient(135deg, rgba(17, 24, 39, 0.9), rgba(15, 23, 42, 0.95))', border: '1px solid rgba(0, 242, 254, 0.2)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
              <div>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Simulated Wallet Balance</span>
                <h2 style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--accent-cyan)', marginTop: '0.25rem' }}>
                  {loadingWallet ? '...' : formatMoney(wallet?.balance || 0)}
                </h2>
              </div>
              <button onClick={() => setShowDepositModal(true)} className="btn-primary" style={{ padding: '0.6rem 1rem', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <PlusCircle size={16} /> <span>Deposit</span>
              </button>
            </div>
            <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1rem', display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              <span>Currency: {wallet?.currency || 'USD'}</span>
              <span>Account Status: Active</span>
            </div>
          </div>

          <div className="glass-card" style={{ padding: '2rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: '600', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <ShieldAlert size={20} style={{ color: 'var(--accent-cyan)' }} /> Quick Security Actions
            </h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
              All outgoing transactions are continuously analyzed by our AI Fraud Engine (Rules + ML Anomaly Detector).
            </p>
            <button onClick={() => setActiveTab('transfer')} className="btn-secondary" style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
              <Send size={16} /> <span>Initiate Transfer</span>
            </button>
          </div>
        </div>
      )}

      {/* TAB 2: SEND MONEY FORM */}
      {activeTab === 'transfer' && (
        <div style={{ maxWidth: '600px', margin: '0 auto' }}>
          <div className="glass-card" style={{ padding: '2rem' }}>
            <h2 style={{ fontSize: '1.4rem', fontWeight: '700', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Send size={22} style={{ color: 'var(--accent-cyan)' }} /> Send Money P2P
            </h2>

            {transferError && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', color: 'var(--risk-critical)', padding: '1rem', borderRadius: '10px', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
                <AlertOctagon size={20} />
                <span>{transferError}</span>
              </div>
            )}

            {transferResult && (
              <div style={{ background: transferResult.status === 'BLOCKED' ? 'rgba(239, 68, 68, 0.15)' : (transferResult.status === 'FLAGGED' ? 'rgba(245, 158, 11, 0.15)' : 'rgba(16, 185, 129, 0.15)'), border: `1px solid ${transferResult.status === 'BLOCKED' ? 'rgba(239, 68, 68, 0.3)' : (transferResult.status === 'FLAGGED' ? 'rgba(245, 158, 11, 0.3)' : 'rgba(16, 185, 129, 0.3)')}`, padding: '1.25rem', borderRadius: '12px', marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                  <span style={{ fontWeight: '700', fontSize: '1.1rem' }}>Result: {transferResult.status}</span>
                  {getStatusBadge(transferResult.status)}
                </div>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
                  Transaction Amount: <strong>{formatMoney(transferResult.amount)}</strong> | Risk Score: <strong>{transferResult.risk_score.toFixed(1)} / 100</strong> ({transferResult.risk_level})
                </p>
                <button onClick={() => onOpenXAI(transferResult.id)} className="btn-secondary" style={{ width: '100%', fontSize: '0.85rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem' }}>
                  <ShieldAlert size={16} /> <span>View Explainable AI (XAI) Risk Attribution</span>
                </button>
              </div>
            )}

            <form onSubmit={handleTransfer} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '500', marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>Recipient Email</label>
                <input
                  type="email"
                  required
                  value={recipientEmail}
                  onChange={(e) => setRecipientEmail(e.target.value)}
                  placeholder="recipient@example.com"
                  className="input-field"
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '500', marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>Transfer Amount ($ USD)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  required
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="100.00"
                  className="input-field"
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '500', marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>Note (Optional)</label>
                <input
                  type="text"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  placeholder="Payment for consulting services"
                  className="input-field"
                />
              </div>

              <button type="submit" disabled={submittingTransfer} className="btn-primary" style={{ width: '100%', marginTop: '0.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                {submittingTransfer ? 'Evaluating & Executing...' : <><span>Send Funds Now</span> <Send size={18} /></>}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* TAB 3: TRANSACTION HISTORY */}
      {activeTab === 'history' && (
        <div className="glass-card" style={{ padding: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
            <h2 style={{ fontSize: '1.4rem', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <History size={22} style={{ color: 'var(--accent-cyan)' }} /> Transaction History
            </h2>

            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              <select value={directionFilter} onChange={(e) => setDirectionFilter(e.target.value)} className="input-field" style={{ width: 'auto', padding: '0.5rem 1rem' }}>
                <option value="all">All Directions</option>
                <option value="sent">Sent Transfers</option>
                <option value="received">Received Transfers</option>
              </select>

              <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="input-field" style={{ width: 'auto', padding: '0.5rem 1rem' }}>
                <option value="">All Statuses</option>
                <option value="APPROVED">Approved</option>
                <option value="FLAGGED">Flagged</option>
                <option value="BLOCKED">Blocked</option>
              </select>

              <button onClick={fetchTransactions} className="btn-secondary" style={{ padding: '0.5rem' }}>
                <RefreshCw size={18} />
              </button>
            </div>
          </div>

          {loadingTx ? (
            <p style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '2rem' }}>Loading transaction history...</p>
          ) : transactions.length === 0 ? (
            <p style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '2rem' }}>No transactions found matching filters.</p>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
                    <th style={{ padding: '0.75rem 1rem' }}>Reference ID</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Date & Time</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Amount</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Risk Score</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((tx) => (
                    <tr key={tx.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)', transition: 'background 0.2s' }}>
                      <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace' }}>{tx.reference_id.substring(0, 8)}...</td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)' }}>{formatDate(tx.created_at)}</td>
                      <td style={{ padding: '0.75rem 1rem', fontWeight: '600' }}>{formatMoney(tx.amount)}</td>
                      <td style={{ padding: '0.75rem 1rem' }}>{getStatusBadge(tx.status)}</td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span style={{ color: tx.risk_score >= 85 ? 'var(--risk-critical)' : (tx.risk_score >= 60 ? 'var(--risk-high)' : 'var(--risk-low)'), fontWeight: '700' }}>
                          {tx.risk_score.toFixed(1)} / 100
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <button onClick={() => onOpenXAI(tx.id)} className="btn-secondary" style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                          <ShieldAlert size={14} /> <span>XAI Analysis</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Deposit Simulation Modal */}
      {showDepositModal && (
        <div className="modal-backdrop">
          <div className="glass-card modal-container" style={{ padding: '2rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '700', marginBottom: '1rem' }}>Deposit Test Funds</h3>
            <form onSubmit={handleDeposit}>
              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>Amount to Deposit ($ USD)</label>
                <input
                  type="number"
                  min="1"
                  value={depositAmount}
                  onChange={(e) => setDepositAmount(e.target.value)}
                  className="input-field"
                />
              </div>
              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                <button type="button" onClick={() => setShowDepositModal(false)} className="btn-secondary">Cancel</button>
                <button type="submit" disabled={submittingDeposit} className="btn-primary">
                  {submittingDeposit ? 'Depositing...' : 'Confirm Deposit'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
