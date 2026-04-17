'use client'
import { useEffect, useState } from 'react'

function TierBadge({ tier }: { tier: string }) {
  return <span className={`badge badge-${tier}`}>{tier}</span>
}

export default function TrustDashboard() {
  const [scores, setScores] = useState<any[]>([])
  const [selected, setSelected] = useState<any>(null)
  const [fraudResult, setFraudResult] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      const s = await fetch('/api/trust/scores').then(r => r.json())
      setScores(s)
    } catch(e) {}
    setLoading(false)
  }

  const loadDetail = async (id: string) => {
    try {
      const [detail, fraud] = await Promise.all([
        fetch(`/api/trust/score/${id}`).then(r => r.json()),
        fetch(`/api/trust/fraud-check/${id}`, { method: 'POST' }).then(r => r.json()),
      ])
      setSelected(detail)
      setFraudResult(fraud)
    } catch(e) {}
  }

  useEffect(() => { load() }, [])

  const COMPONENT_LABELS: Record<string, { label: string; weight: string; color: string }> = {
    validation_accuracy: { label: 'Validation Accuracy', weight: '40%', color: '#6366f1' },
    vouch_chain_depth:   { label: 'Vouch Chain Depth', weight: '20%', color: '#f59e0b' },
    contribution_diversity: { label: 'Contribution Diversity', weight: '15%', color: '#10b981' },
    tenure:              { label: 'Tenure (months, cap 24)', weight: '10%', color: '#8b5cf6' },
    governance_participation: { label: 'Governance Participation', weight: '10%', color: '#f43f5e' },
    stake_history:       { label: 'Stake History', weight: '5%', color: '#06b6d4' },
  }

  if (loading) return (
    <div style={{ padding: '48px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div className="skeleton" style={{ height: '200px' }} />
      <div className="skeleton" style={{ height: '300px' }} />
    </div>
  )

  return (
    <div style={{ padding: '32px 40px', maxWidth: '1200px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '4px' }}>Trust Scores</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Composite 0–100 score · Fraud detection · Access restrictions</p>
      </div>

      {/* Component key */}
      <div className="card fade-in-up" style={{ marginBottom: '20px' }}>
        <div className="section-label">Score Components</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
          {Object.entries(COMPONENT_LABELS).map(([k, v]) => (
            <div key={k} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: v.color, flexShrink: 0 }} />
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{v.label}</span>
              <span style={{ fontSize: '0.72rem', color: v.color, marginLeft: 'auto', fontWeight: 600 }}>{v.weight}</span>
            </div>
          ))}
        </div>
        <div className="divider" />
        <div style={{ display: 'flex', gap: '20px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          <span>⚠️ &lt;30: Governance voting suspended</span>
          <span>⚠️ &lt;40: Redemption cap $200/month</span>
          <span>✓ &gt;70: Priority validator assignment</span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Leaderboard */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border)', fontWeight: 700, fontSize: '0.9rem' }}>Trust Leaderboard</div>
          <div style={{ maxHeight: '480px', overflowY: 'auto' }}>
            {scores.map((s: any, i) => {
              const score = s.trust_score
              let scoreColor = '#94a3b8'
              if (score >= 70) scoreColor = '#34d399'
              else if (score >= 40) scoreColor = '#818cf8'
              else if (score >= 30) scoreColor = '#fbbf24'
              else scoreColor = '#fb7185'

              return (
                <div key={s.contributor_id}
                  style={{
                    display: 'flex', alignItems: 'center', gap: '12px',
                    padding: '12px 14px', borderBottom: '1px solid rgba(51,65,85,0.4)',
                    cursor: 'pointer',
                    background: selected?.contributor_id === s.contributor_id ? 'rgba(99,102,241,0.08)' : 'transparent',
                    transition: 'background 0.15s',
                  }}
                  onClick={() => loadDetail(s.contributor_id)}
                >
                  <span className="mono" style={{ color: 'var(--text-muted)', fontSize: '0.8rem', width: '28px' }}>#{i + 1}</span>
                  {/* Trust ring */}
                  <div style={{
                    width: '42px', height: '42px', borderRadius: '50%', flexShrink: 0,
                    border: `2px solid ${scoreColor}`, display: 'flex', alignItems: 'center',
                    justifyContent: 'center', fontFamily: 'monospace', fontWeight: 700,
                    fontSize: '0.8rem', color: scoreColor,
                  }}>
                    {score?.toFixed(0)}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{s.handle}</div>
                    <TierBadge tier={s.tier} />
                  </div>
                  {score < 30 && <span style={{ fontSize: '0.65rem', color: '#fb7185' }}>⛔ No Vote</span>}
                  {score < 40 && score >= 30 && <span style={{ fontSize: '0.65rem', color: '#fbbf24' }}>⚠ Cap</span>}
                  {score >= 70 && <span style={{ fontSize: '0.65rem', color: '#34d399' }}>★ Priority</span>}
                </div>
              )
            })}
          </div>
        </div>

        {/* Detail panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {selected ? (
            <div className="card fade-in-up">
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '20px' }}>
                <div style={{
                  width: '72px', height: '72px', borderRadius: '50%',
                  border: `3px solid ${selected.trust_score >= 70 ? '#34d399' : selected.trust_score >= 40 ? '#818cf8' : '#fb7185'}`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontFamily: 'monospace', fontWeight: 800, fontSize: '1.3rem',
                  color: selected.trust_score >= 70 ? '#34d399' : selected.trust_score >= 40 ? '#818cf8' : '#fb7185',
                }}>
                  {selected.trust_score?.toFixed(1)}
                </div>
                <div>
                  <div style={{ fontWeight: 800, fontSize: '1.1rem' }}>{selected.handle}</div>
                  <TierBadge tier={selected.tier} />
                  {selected.active_restrictions?.length > 0 && (
                    <div style={{ marginTop: '6px' }}>
                      {selected.active_restrictions.map((r: string) => (
                        <div key={r} style={{ fontSize: '0.72rem', color: '#fbbf24' }}>⚠ {r}</div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Score breakdown bars */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {Object.entries(COMPONENT_LABELS).map(([k, v]) => {
                  const raw = selected.breakdown?.[k] || 0
                  const max = { validation_accuracy: 40, vouch_chain_depth: 20, contribution_diversity: 15, tenure: 10, governance_participation: 10, stake_history: 5 }[k] || 10
                  const pct = (raw / max) * 100
                  return (
                    <div key={k}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', fontSize: '0.75rem' }}>
                        <span style={{ color: 'var(--text-muted)' }}>{v.label}</span>
                        <span className="mono" style={{ color: v.color }}>{raw.toFixed(1)}/{max}</span>
                      </div>
                      <div className="progress-track">
                        <div style={{ height: '100%', borderRadius: '999px', background: v.color, width: `${Math.min(100, pct)}%`, transition: 'width 0.6s' }} />
                      </div>
                    </div>
                  )
                })}
              </div>

              {/* Raw inputs */}
              <div className="divider" />
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
                <div>Accuracy: <span className="mono" style={{ color: 'var(--text)' }}>{(selected.breakdown?.raw_accuracy * 100)?.toFixed(0)}%</span></div>
                <div>Vouch depth: <span className="mono" style={{ color: 'var(--text)' }}>{selected.breakdown?.raw_vouch_depth}</span></div>
                <div>Types: <span className="mono" style={{ color: 'var(--text)' }}>{selected.breakdown?.raw_distinct_types}</span></div>
                <div>Tenure: <span className="mono" style={{ color: 'var(--text)' }}>{selected.breakdown?.raw_tenure_months}mo</span></div>
                <div>Gov pct: <span className="mono" style={{ color: 'var(--text)' }}>{(selected.breakdown?.raw_governance_pct * 100)?.toFixed(0)}%</span></div>
                <div>Stake ratio: <span className="mono" style={{ color: 'var(--text)' }}>{selected.breakdown?.raw_stake_ratio?.toFixed(2)}</span></div>
              </div>
            </div>
          ) : (
            <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '48px' }}>
              Select a contributor to view their trust score breakdown
            </div>
          )}

          {/* Fraud check results */}
          {fraudResult && (
            <div className={`card fade-in-up ${fraudResult.is_clean ? '' : ''}`}
              style={{
                borderColor: fraudResult.is_clean ? 'rgba(16,185,129,0.4)' : 'rgba(244,63,94,0.4)',
                background: fraudResult.is_clean ? 'rgba(16,185,129,0.04)' : 'rgba(244,63,94,0.04)',
              }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', fontWeight: 700, fontSize: '0.875rem' }}>
                <span>{fraudResult.is_clean ? '✅' : '🚨'}</span>
                Fraud Check — {fraudResult.handle}
              </div>
              {fraudResult.is_clean ? (
                <div style={{ fontSize: '0.82rem', color: '#34d399' }}>No fraud signals detected</div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {fraudResult.flags?.map((f: any, i: number) => (
                    <div key={i} className="card-sm" style={{ borderColor: 'rgba(244,63,94,0.2)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <span style={{ fontSize: '0.78rem', fontWeight: 600, color: '#fb7185' }}>{f.type.replace(/_/g,' ')}</span>
                        <span className={`badge ${f.severity === 'critical' ? '' : ''}`}
                          style={{
                            background: f.severity === 'critical' ? 'rgba(244,63,94,0.2)' : 'rgba(245,158,11,0.2)',
                            color: f.severity === 'critical' ? '#fb7185' : '#fbbf24',
                          }}>
                          {f.severity}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{f.detail}</div>
                    </div>
                  ))}
                  {fraudResult.recommended_actions?.length > 0 && (
                    <div style={{ marginTop: '4px' }}>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Recommended Actions:</div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                        {fraudResult.recommended_actions.map((a: string) => (
                          <span key={a} className="badge" style={{ background: 'rgba(244,63,94,0.15)', color: '#fb7185' }}>{a}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
