'use client'
import { useEffect, useState } from 'react'

interface Contribution { id: string; type: string; title: string; status: string; base_score?: number; contributor_id?: string; submitted_at: string; abuse_flags?: string[] }
interface Validator { handle: string; tier: string; accuracy_score: number; trust_score: number; total_validations?: number }

function StatusPill({ status }: { status: string }) {
  return <span className={`status-pill status-${status}`}>{status}</span>
}
function TierBadge({ tier }: { tier: string }) {
  return <span className={`badge badge-${tier}`}>{tier}</span>
}

const DEMO_VALIDATOR = 'contrib_010'  // MarcoValidator

export default function ValidatorDashboard() {
  const [validatorId, setValidatorId] = useState(DEMO_VALIDATOR)
  const [queue, setQueue] = useState<Contribution[]>([])
  const [selected, setSelected] = useState<Contribution | null>(null)
  const [validatorInfo, setValidatorInfo] = useState<Validator | null>(null)
  const [validators, setValidators] = useState<any[]>([])
  const [stakes, setStakes] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [actionNote, setActionNote] = useState('')
  const [stakeAmount, setStakeAmount] = useState(0)
  const [confidence, setConfidence] = useState(0.8)
  const [msg, setMsg] = useState('')

  const load = async (vid: string) => {
    setLoading(true)
    try {
      const [q, acc, lb, st] = await Promise.all([
        fetch(`/api/validation/queue/${vid}`).then(r => r.json()),
        fetch(`/api/validation/validator/${vid}/accuracy`).then(r => r.json()),
        fetch(`/api/scoring/leaderboard?limit=25`).then(r => r.json()),
        fetch(`/api/validation/stakes?contributor_id=${vid}`).then(r => r.json()),
      ])
      setQueue(q)
      setValidatorInfo(acc)
      setValidators(lb.filter((c: any) => ['validator','expert','partner'].includes(c.tier)))
      setStakes(st)
    } catch(e) {}
    setLoading(false)
  }

  useEffect(() => { load(validatorId) }, [validatorId])

  const handleDecision = async (decision: string) => {
    if (!selected) return
    try {
      const body: any = {
        validator_id: validatorId,
        decision,
        confidence,
        notes: actionNote || `${decision} — reviewed by validator`,
      }
      if (stakeAmount > 0 && validatorInfo && ['expert','partner'].includes(validatorInfo.tier)) {
        body.stake_credits = stakeAmount
      }
      const res = await fetch(`/api/validation/validate/${selected.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      setMsg(`✅ ${decision.toUpperCase()} recorded — Contribution now: ${data.contribution_status}`)
      setSelected(null)
      setActionNote('')
      setStakeAmount(0)
      load(validatorId)
    } catch(e) {
      setMsg('❌ Error processing decision')
    }
  }

  if (loading) return (
    <div style={{ padding: '48px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div className="skeleton" style={{ height: '120px' }} />
      <div className="skeleton" style={{ height: '300px' }} />
    </div>
  )

  return (
    <div style={{ padding: '32px 40px', maxWidth: '1200px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '4px' }}>Validator Dashboard</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Review queue · Attest or reject · Stake credits</p>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <select className="input" style={{ width: 'auto' }} value={validatorId} onChange={e => setValidatorId(e.target.value)}>
            {validators.map((v: any) => (
              <option key={v.contributor_id} value={v.contributor_id}>{v.handle}</option>
            ))}
          </select>
          <button className="btn btn-primary" onClick={() => load(validatorId)}>↻ Refresh</button>
        </div>
      </div>

      {msg && (
        <div className="card fade-in-up" style={{ marginBottom: '16px', borderColor: msg.startsWith('✅') ? 'rgba(16,185,129,0.4)' : 'rgba(244,63,94,0.4)', background: msg.startsWith('✅') ? 'rgba(16,185,129,0.05)' : 'rgba(244,63,94,0.05)' }}>
          {msg}
        </div>
      )}

      {/* Validator scorecard */}
      {validatorInfo && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>
          {[
            { label: 'Accuracy', value: `${(validatorInfo.accuracy_score * 100).toFixed(0)}%`, color: '#10b981' },
            { label: 'Queue Size', value: queue.length, color: '#6366f1' },
            { label: 'Tier', value: validatorInfo.tier?.toUpperCase(), color: '#f59e0b' },
            { label: 'Trust Score', value: (validatorInfo.trust_score || 0).toFixed(1), color: '#8b5cf6' },
          ].map((s, i) => (
            <div key={i} className={`hero-card fade-in-up stagger-${i+1}`} style={{ textAlign: 'center' }}>
              <div className="section-label">{s.label}</div>
              <div className="num-lg" style={{ color: s.color }}>{s.value}</div>
            </div>
          ))}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Queue */}
        <div className="card fade-in-up" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', fontWeight: 700, fontSize: '0.95rem' }}>
            Validation Queue ({queue.length})
          </div>
          <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
            {queue.length === 0 ? (
              <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>Queue empty</div>
            ) : queue.map(c => (
              <div key={c.id}
                style={{
                  padding: '14px 16px', borderBottom: '1px solid rgba(51,65,85,0.4)',
                  cursor: 'pointer',
                  background: selected?.id === c.id ? 'rgba(99,102,241,0.1)' : 'transparent',
                  transition: 'background 0.15s',
                }}
                onClick={() => setSelected(c)}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.875rem', marginBottom: '4px' }}>{c.title}</div>
                    <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.72rem', fontFamily: 'monospace', color: '#818cf8' }}>{c.type}</span>
                      <StatusPill status={c.status} />
                    </div>
                  </div>
                  <div className="mono" style={{ color: '#818cf8', fontSize: '0.82rem' }}>
                    {c.base_score || '—'}pts
                  </div>
                </div>
                {c.abuse_flags && c.abuse_flags.length > 0 && (
                  <div style={{ fontSize: '0.7rem', color: '#fb7185', marginTop: '4px' }}>
                    ⚠️ Flagged: {c.abuse_flags.join(', ')}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Action panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {selected ? (
            <div className="card fade-in-up">
              <div style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: '16px' }}>Review: {selected.title}</div>
              <div className="card-sm" style={{ marginBottom: '16px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '0.8rem' }}>
                  <div><span style={{ color: 'var(--text-muted)' }}>ID:</span> <span className="mono">{selected.id}</span></div>
                  <div><span style={{ color: 'var(--text-muted)' }}>Type:</span> <span style={{ color: '#818cf8' }}>{selected.type}</span></div>
                  <div><span style={{ color: 'var(--text-muted)' }}>Base:</span> <span className="mono">{selected.base_score || '—'}</span></div>
                  <div><span style={{ color: 'var(--text-muted)' }}>Status:</span> <StatusPill status={selected.status} /></div>
                </div>
              </div>

              <div style={{ marginBottom: '12px' }}>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>
                  Confidence: {(confidence * 100).toFixed(0)}%
                </label>
                <input type="range" min="0.5" max="1" step="0.05" value={confidence}
                  onChange={e => setConfidence(parseFloat(e.target.value))}
                  style={{ width: '100%', accentColor: '#6366f1' }} />
              </div>

              <div style={{ marginBottom: '12px' }}>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>Notes</label>
                <textarea className="input" rows={3} value={actionNote} onChange={e => setActionNote(e.target.value)}
                  placeholder="Optional review notes..." style={{ resize: 'vertical' }} />
              </div>

              {validatorInfo && ['expert','partner'].includes(validatorInfo.tier) && (
                <div style={{ marginBottom: '16px' }}>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>
                    Stake Credits (0–500) — Expert/Partner only
                  </label>
                  <input type="number" className="input" min="0" max="500" value={stakeAmount}
                    onChange={e => setStakeAmount(parseInt(e.target.value) || 0)} />
                  {stakeAmount > 0 && (
                    <div style={{ fontSize: '0.72rem', color: '#f59e0b', marginTop: '4px' }}>
                      Upheld → +50 bonus credits · Overturned → lose {stakeAmount} credits
                    </div>
                  )}
                </div>
              )}

              <div style={{ display: 'flex', gap: '8px' }}>
                <button className="btn btn-success" style={{ flex: 1 }} onClick={() => handleDecision('attest')}>
                  ✓ Attest
                </button>
                <button className="btn btn-danger" style={{ flex: 1 }} onClick={() => handleDecision('flag')}>
                  ⚑ Flag
                </button>
                <button className="btn btn-danger" onClick={() => handleDecision('reject')}>
                  ✕ Reject
                </button>
              </div>
            </div>
          ) : (
            <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '48px 24px' }}>
              Select a contribution from the queue to review
            </div>
          )}

          {/* Stakes */}
          {stakes.length > 0 && (
            <div className="card fade-in-up stagger-2" style={{ padding: 0, overflow: 'hidden' }}>
              <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border)', fontWeight: 700, fontSize: '0.875rem' }}>
                Active Stakes
              </div>
              <table className="data-table">
                <thead><tr><th>Contribution</th><th>Amount</th><th>Status</th></tr></thead>
                <tbody>
                  {stakes.map((s: any) => (
                    <tr key={s.id}>
                      <td className="mono" style={{ fontSize: '0.75rem' }}>{s.contribution_id}</td>
                      <td className="mono" style={{ color: '#f59e0b' }}>{s.amount}cr</td>
                      <td>
                        <span className={`status-pill ${s.status === 'upheld' ? 'status-complete' : s.status === 'overturned' ? 'status-rejected' : 'status-pending'}`}>
                          {s.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
