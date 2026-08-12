import React, { useEffect, useState } from 'react';
import { apiFetch } from '../services/api';
import {
  ShieldAlert,
  X,
  CheckCircle2,
  AlertTriangle,
  AlertOctagon,
  Cpu,
  Layers,
  FileText
} from 'lucide-react';

interface RiskFactor {
  factor_type: 'RULE' | 'ML_ANOMALY' | 'THREAT_INTEL';
  rule_name: string;
  impact: number;
  is_critical: boolean;
  description: string;
}

interface XAIExplanation {
  transaction_id: string;
  reference_id: string;
  amount: number;
  status: string;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  action: 'APPROVE' | 'FLAG' | 'BLOCK';
  rules_score: number;
  ml_score: number;
  risk_factors: RiskFactor[];
  explanation_summary: string;
}

interface XAIModalProps {
  transactionId: string;
  onClose: () => void;
}

export const XAIModal: React.FC<XAIModalProps> = ({ transactionId, onClose }) => {
  const [data, setData] = useState<XAIExplanation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchXAI = async () => {
      try {
        setLoading(true);
        const res = await apiFetch<XAIExplanation>(`/payments/${transactionId}/xai`);
        setData(res);
      } catch (err: any) {
        setError(err.message || 'Failed to load XAI explanation');
      } finally {
        setLoading(false);
      }
    };
    fetchXAI();
  }, [transactionId]);

  const formatMoney = (val: number) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
  };

  const getRiskBadge = (level: string) => {
    switch (level) {
      case 'LOW':
        return <span className="badge badge-low">LOW RISK</span>;
      case 'MEDIUM':
        return <span className="badge badge-medium">MEDIUM RISK</span>;
      case 'HIGH':
        return <span className="badge badge-high">HIGH RISK</span>;
      case 'CRITICAL':
        return <span className="badge badge-critical">CRITICAL RISK</span>;
      default:
        return <span className="badge badge-medium">{level}</span>;
    }
  };

  const getActionBadge = (action: string) => {
    switch (action) {
      case 'APPROVE':
        return <span className="badge badge-approved"><CheckCircle2 size={12} /> ACTION: APPROVE</span>;
      case 'FLAG':
        return <span className="badge badge-flagged"><AlertTriangle size={12} /> ACTION: FLAG FOR REVIEW</span>;
      case 'BLOCK':
        return <span className="badge badge-blocked"><AlertOctagon size={12} /> ACTION: BLOCK TRANSACTION</span>;
      default:
        return <span className="badge badge-medium">{action}</span>;
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="glass-card modal-container" style={{ padding: '2rem', border: '1px solid rgba(0, 242, 254, 0.3)' }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(0, 242, 254, 0.15)', color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ShieldAlert size={22} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: '700' }}>Explainable AI (XAI) Risk Attribution</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Transaction ID: {transactionId.substring(0, 8)}...</p>
            </div>
          </div>
          <button onClick={onClose} className="btn-secondary" style={{ padding: '0.4rem', borderRadius: '8px' }}>
            <X size={20} />
          </button>
        </div>

        {loading ? (
          <p style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>Calculating risk score breakdown...</p>
        ) : error ? (
          <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', color: 'var(--risk-critical)', borderRadius: '10px' }}>
            {error}
          </div>
        ) : data ? (
          <div>
            {/* Score Overview Card */}
            <div style={{ background: 'rgba(0, 0, 0, 0.3)', padding: '1.25rem', borderRadius: '12px', marginBottom: '1.5rem', border: '1px solid var(--border-color)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                <div>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Composite Risk Score</span>
                  <div style={{ fontSize: '2.2rem', fontWeight: '800', color: data.risk_score >= 85 ? 'var(--risk-critical)' : (data.risk_score >= 60 ? 'var(--risk-high)' : 'var(--risk-low)') }}>
                    {data.risk_score.toFixed(1)} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/ 100</span>
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.4rem' }}>
                  {getRiskBadge(data.risk_level)}
                  {getActionBadge(data.action)}
                </div>
              </div>

              {/* Progress Bar Gauge */}
              <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '4px', overflow: 'hidden', marginBottom: '1rem' }}>
                <div
                  style={{
                    width: `${Math.min(100, Math.max(5, data.risk_score))}%`,
                    height: '100%',
                    background: data.risk_score >= 85 ? 'var(--risk-critical)' : (data.risk_score >= 60 ? 'var(--risk-high)' : 'var(--risk-low)'),
                    transition: 'width 0.5s ease-out'
                  }}
                />
              </div>

              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                "{data.explanation_summary}"
              </p>
            </div>

            {/* 60 / 40 Hybrid Score Composition Split */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-cyan)', marginBottom: '0.4rem' }}>
                  <Layers size={16} />
                  <span style={{ fontSize: '0.85rem', fontWeight: '600' }}>Deterministic Rules (60%)</span>
                </div>
                <div style={{ fontSize: '1.4rem', fontWeight: '700' }}>{data.rules_score.toFixed(1)} pts</div>
              </div>

              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-purple)', marginBottom: '0.4rem' }}>
                  <Cpu size={16} />
                  <span style={{ fontSize: '0.85rem', fontWeight: '600' }}>ML IsolationForest (40%)</span>
                </div>
                <div style={{ fontSize: '1.4rem', fontWeight: '700' }}>{data.ml_score.toFixed(1)} pts</div>
              </div>
            </div>

            {/* Risk Factors List */}
            <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <FileText size={18} style={{ color: 'var(--accent-cyan)' }} /> Triggered Risk Factors & Feature Attribution
            </h4>

            {data.risk_factors.length === 0 ? (
              <div style={{ padding: '1rem', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '10px', color: 'var(--risk-low)', fontSize: '0.85rem' }}>
                ✓ No high-risk factors or security policy violations tripped.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {data.risk_factors.map((rf, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: rf.is_critical ? 'rgba(239, 68, 68, 0.12)' : 'rgba(255, 255, 255, 0.04)',
                      border: `1px solid ${rf.is_critical ? 'rgba(239, 68, 68, 0.3)' : 'var(--border-color)'}`,
                      padding: '0.85rem 1rem',
                      borderRadius: '10px'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                      <span style={{ fontWeight: '700', fontSize: '0.85rem', color: rf.is_critical ? 'var(--risk-critical)' : 'var(--text-primary)' }}>
                        {rf.rule_name}
                      </span>
                      <span className="badge badge-high" style={{ fontSize: '0.7rem' }}>
                        +{rf.impact} pts
                      </span>
                    </div>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{rf.description}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : null}
      </div>
    </div>
  );
};
