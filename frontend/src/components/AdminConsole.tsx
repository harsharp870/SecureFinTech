import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import {
  ShieldCheck,
  AlertOctagon,
  FileText,
  Users,
  Activity,
  LogOut,
  RefreshCw,
  Search,
  Filter,
  CheckCircle2,
  AlertTriangle,
  Info
} from 'lucide-react';

interface AuditItem {
  id: string;
  category: string;
  severity: string;
  action: string;
  actor_id?: string;
  ip_address?: string;
  details?: string;
  created_at: string;
}

interface TransactionItem {
  id: string;
  reference_id: string;
  sender_id: string;
  recipient_id: string;
  amount: number;
  currency: string;
  status: string;
  risk_score: number;
  risk_level: string;
  created_at: string;
}

interface AdminConsoleProps {
  onOpenXAI: (txId: string) => void;
}

export const AdminConsole: React.FC<AdminConsoleProps> = ({ onOpenXAI }) => {
  const { user, logout } = useAuth();
  const [activeView, setActiveView] = useState<'transactions' | 'audit'>('transactions');

  const [auditLogs, setAuditLogs] = useState<AuditItem[]>([]);
  const [transactions, setTransactions] = useState<TransactionItem[]>([]);

  const [loading, setLoading] = useState(true);

  // Filters for Audit Logs
  const [categoryFilter, setCategoryFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');

  const fetchAdminData = async () => {
    try {
      setLoading(true);
      // Fetch recent transactions
      const txData = await apiFetch<{ items: TransactionItem[] }>('/payments/history?page=1&size=30');
      setTransactions(txData.items || []);

      // Fetch audit logs
      let auditQuery = '/admin/audit-logs?page=1&size=30';
      if (categoryFilter) auditQuery += `&category=${categoryFilter}`;
      if (severityFilter) auditQuery += `&severity=${severityFilter}`;
      const auditData = await apiFetch<{ items: AuditItem[] }>(auditQuery);
      setAuditLogs(auditData.items || []);
    } catch (err) {
      console.error('Failed to load admin data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, [categoryFilter, severityFilter]);

  const totalVolume = transactions.reduce((sum, tx) => sum + tx.amount, 0);
  const blockedCount = transactions.filter((tx) => tx.status === 'BLOCKED').length;
  const flaggedCount = transactions.filter((tx) => tx.status === 'FLAGGED').length;
  const blockRate = transactions.length > 0 ? ((blockedCount / transactions.length) * 100).toFixed(1) : '0.0';

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
        return <span className="badge badge-medium">{status}</span>;
    }
  };

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'INFO':
        return <span className="badge badge-low">INFO</span>;
      case 'WARNING':
        return <span className="badge badge-high">WARNING</span>;
      case 'CRITICAL':
        return <span className="badge badge-critical">CRITICAL</span>;
      default:
        return <span className="badge badge-medium">{sev}</span>;
    }
  };

  return (
    <div style={{ minHeight: '100vh', padding: '1.5rem', maxWidth: '1300px', margin: '0 auto' }}>
      {/* Top Header */}
      <header className="glass-card" style={{ padding: '1.25rem 2rem', marginBottom: '2rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ width: '44px', height: '44px', borderRadius: '12px', background: 'rgba(239, 68, 68, 0.15)', color: 'var(--risk-critical)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <ShieldCheck size={24} />
          </div>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: '700' }}>Admin Security Console</h1>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Security Command Center & Fraud Monitoring</p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span className="badge badge-critical" style={{ padding: '0.4rem 0.8rem' }}>Role: ADMIN</span>
          <button onClick={logout} className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem' }}>
            <LogOut size={16} /> <span>Sign Out</span>
          </button>
        </div>
      </header>

      {/* 4 Security KPI Grid Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.25rem', marginBottom: '2rem' }}>
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontSize: '0.85rem' }}>
            <span>Total Evaluated Volume</span>
            <Activity size={18} style={{ color: 'var(--accent-cyan)' }} />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: '800' }}>{formatMoney(totalVolume)}</div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{transactions.length} Total Transactions</span>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontSize: '0.85rem' }}>
            <span>Blocked Fraud Count</span>
            <AlertOctagon size={18} style={{ color: 'var(--risk-critical)' }} />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: '800', color: 'var(--risk-critical)' }}>{blockedCount}</div>
          <span style={{ fontSize: '0.75rem', color: 'var(--risk-critical)' }}>{blockRate}% Block Rate</span>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontSize: '0.85rem' }}>
            <span>Flagged Review Queue</span>
            <AlertTriangle size={18} style={{ color: 'var(--risk-high)' }} />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: '800', color: 'var(--risk-high)' }}>{flaggedCount}</div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Action Required</span>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontSize: '0.85rem' }}>
            <span>Audit Trail Events</span>
            <FileText size={18} style={{ color: 'var(--accent-purple)' }} />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: '800' }}>{auditLogs.length}</div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Recorded Events</span>
        </div>
      </div>

      {/* View Switcher Tabs */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
        <button
          onClick={() => setActiveView('transactions')}
          className={activeView === 'transactions' ? 'btn-primary' : 'btn-secondary'}
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
        >
          <Activity size={18} /> <span>Live Transactions Monitor</span>
        </button>
        <button
          onClick={() => setActiveView('audit')}
          className={activeView === 'audit' ? 'btn-primary' : 'btn-secondary'}
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
        >
          <FileText size={18} /> <span>Security Audit Trail</span>
        </button>
      </div>

      {/* VIEW 1: LIVE TRANSACTIONS MONITOR */}
      {activeView === 'transactions' && (
        <div className="glass-card" style={{ padding: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: '700' }}>Global Transactions & Fraud Risk Queue</h3>
            <button onClick={fetchAdminData} className="btn-secondary" style={{ padding: '0.5rem' }}>
              <RefreshCw size={18} />
            </button>
          </div>

          {loading ? (
            <p style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '2rem' }}>Loading live transaction stream...</p>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
                    <th style={{ padding: '0.75rem 1rem' }}>Reference ID</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Timestamp</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Amount</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Risk Score</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Risk Level</th>
                    <th style={{ padding: '0.75rem 1rem' }}>XAI Inspection</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((tx) => (
                    <tr key={tx.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                      <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace' }}>{tx.reference_id.substring(0, 8)}...</td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)' }}>{formatDate(tx.created_at)}</td>
                      <td style={{ padding: '0.75rem 1rem', fontWeight: '600' }}>{formatMoney(tx.amount)}</td>
                      <td style={{ padding: '0.75rem 1rem' }}>{getStatusBadge(tx.status)}</td>
                      <td style={{ padding: '0.75rem 1rem', fontWeight: '700', color: tx.risk_score >= 85 ? 'var(--risk-critical)' : (tx.risk_score >= 60 ? 'var(--risk-high)' : 'var(--risk-low)') }}>
                        {tx.risk_score.toFixed(1)} / 100
                      </td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span className={`badge badge-${tx.risk_level.toLowerCase()}`}>{tx.risk_level}</span>
                      </td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <button onClick={() => onOpenXAI(tx.id)} className="btn-secondary" style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                          <ShieldCheck size={14} /> <span>Inspect XAI</span>
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

      {/* VIEW 2: SECURITY AUDIT TRAIL */}
      {activeView === 'audit' && (
        <div className="glass-card" style={{ padding: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: '700' }}>Immutable Security Audit Trail</h3>

            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)} className="input-field" style={{ width: 'auto', padding: '0.5rem 1rem' }}>
                <option value="">All Categories</option>
                <option value="SECURITY_EVENT">Security Event</option>
                <option value="ADMIN_ACTION">Admin Action</option>
              </select>

              <select value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)} className="input-field" style={{ width: 'auto', padding: '0.5rem 1rem' }}>
                <option value="">All Severities</option>
                <option value="INFO">Info</option>
                <option value="WARNING">Warning</option>
                <option value="CRITICAL">Critical</option>
              </select>

              <button onClick={fetchAdminData} className="btn-secondary" style={{ padding: '0.5rem' }}>
                <RefreshCw size={18} />
              </button>
            </div>
          </div>

          {loading ? (
            <p style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '2rem' }}>Loading audit logs...</p>
          ) : auditLogs.length === 0 ? (
            <p style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '2rem' }}>No audit events found matching filters.</p>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
                    <th style={{ padding: '0.75rem 1rem' }}>Timestamp</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Category</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Severity</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Action</th>
                    <th style={{ padding: '0.75rem 1rem' }}>IP Address</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {auditLogs.map((log) => (
                    <tr key={log.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)' }}>{formatDate(log.created_at)}</td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span className="badge badge-medium">{log.category}</span>
                      </td>
                      <td style={{ padding: '0.75rem 1rem' }}>{getSeverityBadge(log.severity)}</td>
                      <td style={{ padding: '0.75rem 1rem', fontWeight: '600' }}>{log.action}</td>
                      <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace' }}>{log.ip_address || 'N/A'}</td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {log.details || '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
