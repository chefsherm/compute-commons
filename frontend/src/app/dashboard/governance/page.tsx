'use client'
import { useEffect, useState } from 'react'

function StatusPill({ status }: { status: string }) {
  const map: Record<string, string> = {
    active: 'status-validating', ratified: 'status-complete', vetoed: 'status-rejected',
    community_failed: 'status-rejected', rejected_by_council: 'status-rejected',
    pending_ratification: 'status-pending', submitted: 'status-pending',
    panel_assigned: 'status-validating', decided: 'status-complete',
  }
  return <span className={`status-pill ${map[status] || 'status-pending'}`}>{status.replace(/_/g, ' ')}</span>
}

export default function GovernanceDashboard() {
  const [proposals, setProposals] = useState<any[]>([])
  const [results, setResults] = useState<any>({ passed: [], failed: [], pending: [] })
  const [disputes, setDisputes] = useState<any[]>([])
  const [charter, setCharter] = useState<any>(null)
  const [queue, setQueue] = useState<any[]>([])
  const [auditSample, setAuditSample] = useState<any[]>([])
  const [tab, setTab] = useState<'proposals' | 'results' | 'disputes' | 'charter' | 'queue' | 'audit'>('proposals')
  const [loading, setLoading] = useState(true)
  const [voteMsg, setVoteMsg] = useState('')

  // New proposal form
  const [newProp, setNewProp] = useState({ proposer_id: 'contrib_010', type: 'taxonomy_change', title: '', description: '', affected_parameter: '', proposed_change: '' })

  const load = async () => {
    setLoading(true)
    try {
      const [p, r, d, c, q, a] = await Promise.all([
        fetch('/api/governance/proposals').then(x => x.json()),
        fetch('/api/governance/results').then(x => x.json()),
        fetch('/api/governance/disputes').then(x => x.json()),
        fetch('/api/governance/charter').then(x => x.json()),
        fetch('/api/governance/queue').then(x => x.json()),
        fetch('/api/governance/audit?limit=8').then(x => x.json()),
      ])
      setProposals(p)
      setResults(r)
      setDisputes(d)
      setCharter(c)
      setQueue(q)
      setAuditSample(a)
    } catch(e) {}
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  const castVote = async (proposalId: string, vote: string, chamber: string = 'community') => {
    try {
      const res = await fetch('/api/governance/vote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voter_id: 'contrib_010', proposal_id: proposalId, chamber, vote }),
      })
      const data = await res.json()
      if (data.detail) setVoteMsg(`Error: ${data.detail}`)
      else setVoteMsg(`Vote cast — weight: ${data.weight_cast}, proposal status: ${data.proposal_status}`)
      load()
    } catch(e) { setVoteMsg('Error casting vote') }
  }

  const submitProposal = async () => {
    try {
      const res = await fetch('/api/governance/proposals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newProp),
      })
      const data = await res.json()
      setVoteMsg(`Proposal submitted: ${data.id}`)
      setNewProp(prev => ({ ...prev, title: '', description: '', affected_parameter: '', proposed_change: '' }))
      load()
    } catch(e) { setVoteMsg('Error submitting proposal') }
  }

  const TABS = [
    { key: 'proposals', label: 'Proposals', count: proposals.length },
    { key: 'results', label: 'Results', count: results.passed?.length + results.failed?.length },
    { key: 'disputes', label: 'Disputes', count: disputes.length },
    { key: 'queue', label: 'Escalations', count: queue.length },
    { key: 'audit', label: 'Audit', count: null },
    { key: 'charter', label: 'Charter', count: null },
  ] as const

  return (
    <div style={{ padding: '32px 40px', maxWidth: '1200px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '4px' }}>Governance</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Bicameral governance · Community Voice + Expert Council · Dispute Resolution</p>
      </div>

      {voteMsg && (
        <div className="card fade-in-up" style={{ marginBottom: '16px', borderColor: voteMsg.startsWith('Error') ? 'rgba(244,63,94,0.4)' : 'rgba(16,185,129,0.4)' }}>
          {voteMsg}
        </div>
      )}

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '14px', marginBottom: '24px' }}>
        {[
          { label: 'Active Proposals', value: results.pending?.length || 0, color: '#6366f1' },
          { label: 'Ratified', value: results.passed?.length || 0, color: '#10b981' },
          { label: 'Failed/Vetoed', value: results.failed?.length || 0, color: '#f43f5e' },
          { label: 'Disputes', value: disputes.length, color: '#f59e0b' },
        ].map((s, i) => (
          <div key={i} className={`hero-card fade-in-up stagger-${i+1}`} style={{ textAlign: 'center' }}>
            <div className="section-label">{s.label}</div>
            <div className="num-lg" style={{ color: s.color }}>{s.value}</div>
          </div>
        ))}
      </div>

      {/* Tab bar */}
      <div style={{ display: 'flex', gap: '4px', marginBottom: '20px', borderBottom: '1px solid var(--border)', paddingBottom: '0' }}>
        {TABS.map(t => (
          <button key={t.key}
            onClick={() => setTab(t.key as any)}
            style={{
              padding: '8px 16px', border: 'none', cursor: 'pointer', borderRadius: '6px 6px 0 0',
              background: tab === t.key ? 'var(--surface)' : 'transparent',
              color: tab === t.key ? '#818cf8' : 'var(--text-muted)',
              fontWeight: tab === t.key ? 700 : 400,
              fontSize: '0.875rem',
              borderBottom: tab === t.key ? '2px solid #6366f1' : '2px solid transparent',
            }}>
            {t.label}{t.count !== null ? ` (${t.count})` : ''}
          </button>
        ))}
      </div>

      {/* Proposals Tab */}
      {tab === 'proposals' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '20px' }}>
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border)', fontWeight: 700, fontSize: '0.9rem' }}>Active Proposals</div>
            <div>
              {proposals.map(p => (
                <div key={p.id} style={{ padding: '16px', borderBottom: '1px solid rgba(51,65,85,0.4)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                    <div style={{ fontWeight: 600, fontSize: '0.875rem', flex: 1, marginRight: '12px' }}>{p.title}</div>
                    <StatusPill status={p.status} />
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '10px', lineHeight: 1.5 }}>{p.description}</div>
                  <div style={{ display: 'flex', gap: '16px', fontSize: '0.75rem', marginBottom: '10px' }}>
                    <span>Community: <strong style={{ color: '#34d399' }}>{p.community_votes_for}</strong> / <strong style={{ color: '#fb7185' }}>{p.community_votes_against}</strong></span>
                    <span>Council: <strong style={{ color: '#34d399' }}>{p.council_votes_for}</strong>pts / <strong style={{ color: '#fb7185' }}>{p.council_votes_against}</strong>pts</span>
                  </div>
                  {p.status === 'active' && (
                    <div style={{ display: 'flex', gap: '6px' }}>
                      <button className="btn btn-success" style={{ fontSize: '0.75rem', padding: '4px 10px' }} onClick={() => castVote(p.id, 'for')}>
                        ↑ For (Community)
                      </button>
                      <button className="btn btn-danger" style={{ fontSize: '0.75rem', padding: '4px 10px' }} onClick={() => castVote(p.id, 'against')}>
                        ↓ Against
                      </button>
                      <button className="btn btn-primary" style={{ fontSize: '0.75rem', padding: '4px 10px' }} onClick={() => castVote(p.id, 'for', 'council')}>
                        ⊞ Council Ratify
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Submit proposal form */}
          <div className="card fade-in-up">
            <div style={{ fontWeight: 700, fontSize: '0.9rem', marginBottom: '16px' }}>Submit Proposal</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Type</label>
                <select className="input" value={newProp.type} onChange={e => setNewProp(p => ({ ...p, type: e.target.value }))}>
                  {['taxonomy_change','point_value_adjustment','new_contribution_type','validator_accuracy_threshold','leaderboard_display'].map(t => (
                    <option key={t} value={t}>{t.replace(/_/g,' ')}</option>
                  ))}
                </select>
              </div>
              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Title</label>
                <input className="input" value={newProp.title} onChange={e => setNewProp(p => ({ ...p, title: e.target.value }))} placeholder="Proposal title..." />
              </div>
              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Description</label>
                <textarea className="input" rows={3} value={newProp.description} onChange={e => setNewProp(p => ({ ...p, description: e.target.value }))} placeholder="Detailed rationale..." style={{ resize: 'vertical' }} />
              </div>
              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Affected Parameter</label>
                <input className="input" value={newProp.affected_parameter} onChange={e => setNewProp(p => ({ ...p, affected_parameter: e.target.value }))} placeholder="e.g. scoring.red_team_report.base_score" />
              </div>
              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Proposed Change</label>
                <input className="input" value={newProp.proposed_change} onChange={e => setNewProp(p => ({ ...p, proposed_change: e.target.value }))} placeholder="e.g. +20%" />
              </div>
              <button className="btn btn-primary" onClick={submitProposal} style={{ marginTop: '4px' }}>
                Submit Proposal →
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Results Tab */}
      {tab === 'results' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border)', fontWeight: 700, color: '#34d399' }}>✓ Ratified ({results.passed?.length})</div>
            {results.passed?.map((p: any) => (
              <div key={p.id} style={{ padding: '14px 16px', borderBottom: '1px solid rgba(51,65,85,0.4)' }}>
                <div style={{ fontWeight: 600, fontSize: '0.875rem', marginBottom: '4px' }}>{p.title}</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{p.resolved_at?.slice(0, 10)}</div>
              </div>
            ))}
          </div>
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border)', fontWeight: 700, color: '#fb7185' }}>✕ Failed/Vetoed ({results.failed?.length})</div>
            {results.failed?.map((p: any) => (
              <div key={p.id} style={{ padding: '14px 16px', borderBottom: '1px solid rgba(51,65,85,0.4)' }}>
                <div style={{ fontWeight: 600, fontSize: '0.875rem', marginBottom: '4px' }}>{p.title}</div>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <StatusPill status={p.status} />
                  {p.veto_reason && <span style={{ fontSize: '0.72rem', color: '#fb7185' }}>Veto: {p.veto_reason}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Disputes Tab */}
      {tab === 'disputes' && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border)', fontWeight: 700, fontSize: '0.9rem' }}>Disputes & Appeals</div>
          <table className="data-table">
            <thead><tr><th>ID</th><th>Contribution</th><th>Reason</th><th>Status</th><th>Panel</th><th>Decision</th></tr></thead>
            <tbody>
              {disputes.map((d: any) => (
                <tr key={d.id}>
                  <td className="mono" style={{ fontSize: '0.75rem' }}>{d.id}</td>
                  <td className="mono" style={{ fontSize: '0.75rem' }}>{d.contribution_id}</td>
                  <td style={{ fontSize: '0.78rem', maxWidth: '200px', color: 'var(--text-muted)' }}>{d.reason?.slice(0, 80)}...</td>
                  <td><StatusPill status={d.status} /></td>
                  <td style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{d.panel_ids?.length || 0} experts</td>
                  <td style={{ fontSize: '0.78rem' }}>{d.decision || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Queue Tab */}
      {tab === 'queue' && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border)', fontWeight: 700, fontSize: '0.9rem' }}>Escalation Queue ({queue.length})</div>
          {queue.length === 0 ? (
            <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>No escalations — queue clear</div>
          ) : (
            <table className="data-table">
              <thead><tr><th>ID</th><th>Type</th><th>Title</th><th>Status</th><th>Abuse Flags</th></tr></thead>
              <tbody>
                {queue.map((c: any) => (
                  <tr key={c.id}>
                    <td className="mono" style={{ fontSize: '0.75rem' }}>{c.id}</td>
                    <td><span style={{ fontSize: '0.72rem', fontFamily: 'monospace', color: '#818cf8' }}>{c.type}</span></td>
                    <td style={{ fontSize: '0.82rem' }}>{c.title}</td>
                    <td><StatusPill status={c.status} /></td>
                    <td style={{ fontSize: '0.72rem', color: '#fb7185' }}>{c.abuse_flags?.join(', ') || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Audit Tab */}
      {tab === 'audit' && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border)', fontWeight: 700, fontSize: '0.9rem' }}>Audit Sample (Random)</div>
          <table className="data-table">
            <thead><tr><th>Validation ID</th><th>Contribution</th><th>Validator</th><th>Decision</th><th>Confidence</th><th>Notes</th></tr></thead>
            <tbody>
              {auditSample.map((v: any) => (
                <tr key={v.id}>
                  <td className="mono" style={{ fontSize: '0.72rem' }}>{v.id}</td>
                  <td className="mono" style={{ fontSize: '0.72rem' }}>{v.contribution_id}</td>
                  <td className="mono" style={{ fontSize: '0.72rem' }}>{v.validator_id}</td>
                  <td><span className={`status-pill ${v.decision === 'attest' ? 'status-complete' : 'status-rejected'}`}>{v.decision}</span></td>
                  <td className="mono">{(v.confidence * 100).toFixed(0)}%</td>
                  <td style={{ fontSize: '0.75rem', color: 'var(--text-muted)', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{v.notes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Charter Tab */}
      {tab === 'charter' && charter && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div className="hero-card fade-in-up">
            <div style={{ fontSize: '0.72rem', color: '#818cf8', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '8px' }}>Governance Charter — Compute Commons</div>
            <p style={{ fontSize: '0.95rem', lineHeight: 1.8, color: 'var(--text-muted)' }}>{charter.mission}</p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            {[
              { key: 'community_voice', title: '⊞ Community Voice', color: '#6366f1', data: charter.chambers?.community_voice },
              { key: 'expert_council', title: '◈ Expert Council', color: '#f59e0b', data: charter.chambers?.expert_council },
            ].map(ch => (
              <div key={ch.key} className="card fade-in-up">
                <div style={{ fontWeight: 700, color: ch.color, marginBottom: '12px' }}>{ch.title}</div>
                <div style={{ fontSize: '0.82rem', lineHeight: 1.8, color: 'var(--text-muted)' }}>
                  {Object.entries(ch.data || {}).map(([k, v]) => (
                    <div key={k}><strong style={{ color: 'var(--text)' }}>{k.replace(/_/g, ' ')}:</strong> {String(v)}</div>
                  ))}
                </div>
              </div>
            ))}
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="card">
              <div style={{ fontWeight: 700, color: '#34d399', marginBottom: '12px' }}>✓ Can Be Governed</div>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {charter.what_can_be_governed?.map((item: string) => (
                  <li key={item} style={{ fontSize: '0.82rem', color: 'var(--text-muted)', display: 'flex', gap: '8px' }}>
                    <span style={{ color: '#34d399' }}>✓</span> {item.replace(/_/g, ' ')}
                  </li>
                ))}
              </ul>
            </div>
            <div className="card">
              <div style={{ fontWeight: 700, color: '#fb7185', marginBottom: '12px' }}>✕ Cannot Be Governed</div>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {charter.what_cannot_be_governed?.map((item: string) => (
                  <li key={item} style={{ fontSize: '0.82rem', color: 'var(--text-muted)', display: 'flex', gap: '8px' }}>
                    <span style={{ color: '#fb7185' }}>✕</span> {item.replace(/_/g, ' ')}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
