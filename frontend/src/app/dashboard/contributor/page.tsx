'use client'
import { useEffect, useState, useCallback } from 'react'
import Link from 'next/link'

const API = '/api'

interface Contributor {
  id: string; handle: string; tier: string; points: number;
  credits_balance: number; accuracy_score: number; trust_score: number;
  reputation_modifier: number; decay_status: string; domains: string[];
  contribution_types_used: string[];
  progression_tier?: string;
  acted_on_count?: number;
}
interface Contribution {
  id: string; type: string; title: string; status: string;
  base_score?: number; final_score?: number; helpfulness_multiplier?: number;
  tier_multiplier?: number; credit_equivalent?: number; submitted_at: string;
  abuse_flags?: string[]; domain?: string; submission_type?: string;
  verified_domain_expert?: boolean; acted_on?: boolean;
}
interface Transaction {
  id: string; type: string; amount: number; description: string; created_at: string;
}
interface SupplyStatus {
  total_hours_available: number; avg_capacity_pct: number; low_supply: boolean;
  model_access: { model: string; rate_tier: string; restrictions: string[]; available_hours: number; status: string }[];
}

const DEMO_ID = 'contrib_004'  // MariaFerments

const TIER_COLORS: Record<string, string> = {
  contributor: '#94a3b8', validator: '#818cf8', expert: '#fbbf24', partner: '#a78bfa'
}
const PROGRESSION_COLORS: Record<string, string> = {
  'contributor': '#94a3b8', 'Validator': '#818cf8', 'Field Expert': '#fbbf24', 'Founding Reviewer': '#a78bfa'
}

function TierBadge({ tier }: { tier: string }) {
  return <span className={`badge badge-${tier}`}>{tier}</span>
}
function StatusPill({ status }: { status: string }) {
  return <span className={`status-pill status-${status}`}>{status}</span>
}
function ProgressionBadge({ tier }: { tier: string }) {
  const color = PROGRESSION_COLORS[tier] || '#94a3b8'
  return (
    <span style={{
      fontSize: '0.65rem', fontWeight: 700, padding: '2px 8px', borderRadius: '12px',
      border: `1px solid ${color}40`, background: `${color}15`, color,
      letterSpacing: '0.04em', textTransform: 'uppercase' as const,
    }}>⬡ {tier}</span>
  )
}

export default function ContributorDashboard() {
  const [contrib, setContrib] = useState<Contributor | null>(null)
  const [contributions, setContributions] = useState<Contribution[]>([])
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [leaderboard, setLeaderboard] = useState<any[]>([])
  const [selectedId, setSelectedId] = useState(DEMO_ID)
  const [allContribs, setAllContribs] = useState<Contributor[]>([])
  const [loading, setLoading] = useState(true)
  const [supply, setSupply] = useState<SupplyStatus | null>(null)

  // Change 2 — pre-submit classifier state
  const [showSubmitForm, setShowSubmitForm] = useState(false)
  const [submitForm, setSubmitForm] = useState({
    type: 'domain_labeling', domain: '', submission_type: '', title: '',
    description: '', what_went_wrong: '', correct_answer: '', domain_qualification: '', credential_reference: '',
  })
  const [classifyResult, setClassifyResult] = useState<any>(null)
  const [classifyLoading, setClassifyLoading] = useState(false)
  const [submitResult, setSubmitResult] = useState<any>(null)
  const [receiptVisible, setReceiptVisible] = useState(false)

  const DOMAINS: Record<string, string> = {
    biomedical: 'Biomedical & Life Sciences', chemistry: 'Chemistry & Materials Science',
    climate_environment: 'Climate & Environmental Science', code_software: 'Software Engineering & Code',
    culinary_food: 'Culinary & Food Science', economics_finance: 'Economics & Finance',
    healthcare_clinical: 'Healthcare & Clinical Medicine', law_legal: 'Law & Legal Systems',
    linguistics_language: 'Linguistics & Low-Resource Languages', math_formal: 'Mathematics & Formal Reasoning',
    philosophy_ethics: 'Philosophy & Ethics', psychology_cognition: 'Psychology & Cognitive Science',
    security_safety: 'Security, Safety & Red-Teaming',
  }

  const loadData = async (id: string) => {
    setLoading(true)
    try {
      const [b, cs, ts, lb, all, sup] = await Promise.all([
        fetch(`${API}/ledger/balance/${id}`).then(r => r.json()),
        fetch(`${API}/intake/contributions/contributor/${id}`).then(r => r.json()),
        fetch(`${API}/ledger/transactions/${id}`).then(r => r.json()),
        fetch(`${API}/scoring/leaderboard?limit=10`).then(r => r.json()),
        fetch(`${API}/scoring/leaderboard?limit=25`).then(r => r.json()),
        fetch(`${API}/meta/supply-status`).then(r => r.json()),
      ])
      setContrib(b)
      setContributions(cs)
      setTransactions(ts)
      setLeaderboard(lb)
      setAllContribs(all)
      setSupply(sup)
    } catch(e) {}
    setLoading(false)
  }

  // Debounced pre-classify call (Change 2)
  const runPreClassify = useCallback(async () => {
    if (!submitForm.description && !submitForm.what_went_wrong) return
    setClassifyLoading(true)
    try {
      const res = await fetch(`${API}/scoring/pre-classify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contributor_id: selectedId,
          title: submitForm.title,
          description: submitForm.description,
          what_went_wrong: submitForm.what_went_wrong,
        }),
      })
      setClassifyResult(await res.json())
    } catch(e) {}
    setClassifyLoading(false)
  }, [submitForm.description, submitForm.what_went_wrong, submitForm.title, selectedId])

  const handleSubmit = async () => {
    try {
      const res = await fetch(`${API}/intake/contributions/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contributor_id: selectedId, ...submitForm }),
      })
      const data = await res.json()
      setSubmitResult(data)
      setReceiptVisible(true)
      setShowSubmitForm(false)
      loadData(selectedId)
    } catch(e) {}
  }

  useEffect(() => { loadData(selectedId) }, [selectedId])

  if (loading) return (
    <div style={{ padding: '48px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div className="skeleton" style={{ height: '180px', borderRadius: '16px' }} />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: '12px' }}>
        {[1,2,3,4].map(i => <div key={i} className="skeleton" style={{ height: '100px' }} />)}
      </div>
    </div>
  )

  const tierPct: Record<string, number> = {contributor: 25, validator: 50, expert: 75, partner: 100}
  const pct = tierPct[contrib?.tier || 'contributor'] || 25

  // Change 1 — find lowest-capacity model for inline display
  const primaryModel = supply?.model_access.find(m => m.status === 'available') || supply?.model_access[0]
  const creditValue = contrib?.credits_balance ? (contrib.credits_balance / 0.01 / 100).toFixed(0) : '0'

  return (
    <div style={{ padding: '32px 40px', maxWidth: '1200px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '4px' }}>Contributor Dashboard</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Points earned, credits balance, contribution history</p>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <select className="input" style={{ width: 'auto' }} value={selectedId} onChange={e => setSelectedId(e.target.value)}>
            {allContribs.map((c: any) => (
              <option key={c.contributor_id} value={c.contributor_id}>{c.handle}</option>
            ))}
          </select>
          <button className="btn btn-primary" onClick={() => loadData(selectedId)}>↻ Refresh</button>
        </div>
      </div>

      {/* Change 1 — Low supply banner: shown BEFORE contributor submits, not after */}
      {supply?.low_supply && (
        <div style={{
          padding: '12px 16px', marginBottom: '16px', borderRadius: '10px',
          background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.3)',
          display: 'flex', alignItems: 'flex-start', gap: '10px',
        }}>
          <span style={{ fontSize: '1.1rem', lineHeight: 1 }}>⚠️</span>
          <div>
            <div style={{ fontWeight: 700, fontSize: '0.85rem', color: '#fbbf24', marginBottom: '2px' }}>
              Supply Notice — One or more compute partners are running low
            </div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
              {supply.model_access.filter(m => m.status === 'low').map(m =>
                `${m.model}: ${m.available_hours.toLocaleString()} GPU-hrs remaining`
              ).join(' · ')}.
              {' '}High-quality submissions are prioritized for redemption when capacity is limited.
            </div>
          </div>
        </div>
      )}

      {/* Contributor hero */}
      {contrib && (
        <div className="hero-card fade-in-up" style={{ marginBottom: '24px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '24px', position: 'relative', zIndex: 1 }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px', flexWrap: 'wrap' }}>
                <h2 style={{ fontSize: '1.75rem', fontWeight: 800 }}>{contrib.handle}</h2>
                <TierBadge tier={contrib.tier} />
                {contrib.progression_tier && contrib.progression_tier !== 'contributor' && (
                  <ProgressionBadge tier={contrib.progression_tier} />
                )}
                {contrib.reputation_modifier > 1 && (
                  <span className="badge" style={{ background: 'rgba(16,185,129,0.15)', color: '#34d399', border: '1px solid rgba(16,185,129,0.3)' }}>
                    +{Math.round((contrib.reputation_modifier - 1) * 100)}% Rep Bonus
                  </span>
                )}
                {contrib.reputation_modifier < 1 && (
                  <span className="badge" style={{ background: 'rgba(244,63,94,0.15)', color: '#fb7185', border: '1px solid rgba(244,63,94,0.3)' }}>
                    {Math.round((contrib.reputation_modifier - 1) * 100)}% Rep Penalty
                  </span>
                )}
              </div>
              <div style={{ display: 'flex', gap: '24px', marginBottom: '16px', flexWrap: 'wrap' }}>
                <div>
                  <div className="section-label">Points</div>
                  <div className="num-xl" style={{ color: '#818cf8' }}>{contrib.points?.toLocaleString()}</div>
                </div>
                <div>
                  {/* Change 1 — credit display with model + rate tier + restrictions inline */}
                  <div className="section-label">Credits</div>
                  <div className="num-xl" style={{ color: '#fbbf24' }}>${contrib.credits_balance?.toFixed(2)}</div>
                  {primaryModel && (
                    <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '3px', lineHeight: 1.4 }}>
                      ≈ {Math.floor(contrib.credits_balance / 0.01)} GPU-min ·{' '}
                      <span style={{ color: '#818cf8' }}>{primaryModel.model}</span>{' '}
                      · {primaryModel.rate_tier}{' '}
                      · {primaryModel.restrictions[0]}
                    </div>
                  )}
                </div>
                <div>
                  <div className="section-label">Trust Score</div>
                  <div className="num-xl" style={{ color: '#10b981' }}>{contrib.trust_score?.toFixed(1)}</div>
                </div>
                <div>
                  <div className="section-label">Accuracy</div>
                  <div className="num-xl" style={{ color: '#f59e0b' }}>{(contrib.accuracy_score * 100).toFixed(0)}%</div>
                </div>
                {(contrib.acted_on_count || 0) > 0 && (
                  <div>
                    <div className="section-label">Acted On</div>
                    <div className="num-xl" style={{ color: '#34d399' }}>⚡ {contrib.acted_on_count}</div>
                  </div>
                )}
              </div>
              {/* Tier progress */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Tier Progress</span>
                  <span style={{ fontSize: '0.75rem', color: TIER_COLORS[contrib.tier] }}>{contrib.tier.toUpperCase()}</span>
                </div>
                <div className="progress-track">
                  <div className="progress-fill" style={{ width: `${pct}%` }} />
                </div>
              </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', minWidth: '140px' }}>
              <div className="card-sm" style={{ background: 'rgba(0,0,0,0.3)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase' as const }}>Decay Status</div>
                <StatusPill status={contrib.decay_status || 'active'} />
              </div>
              <div className="card-sm" style={{ background: 'rgba(0,0,0,0.3)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase' as const }}>Types Used</div>
                <div className="num-md" style={{ color: '#818cf8' }}>{contrib.contribution_types_used?.length || 0}</div>
              </div>
              <Link href={`/profile/${contrib.handle}`} style={{ textDecoration: 'none' }}>
                <div className="card-sm" style={{ background: 'rgba(99,102,241,0.1)', textAlign: 'center', cursor: 'pointer', border: '1px solid rgba(99,102,241,0.3)' }}>
                  <div style={{ fontSize: '0.7rem', color: '#818cf8', fontWeight: 600 }}>Public Profile ↗</div>
                </div>
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Supply model details (Change 1 — inline, not tooltip) */}
      {supply && (
        <div className="card fade-in-up" style={{ marginBottom: '20px', padding: '14px 18px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <div style={{ fontWeight: 700, fontSize: '0.85rem' }}>Compute Access — What Your Credits Buy</div>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{supply.total_hours_available.toLocaleString()} GPU-hrs total available</span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
            {supply.model_access.map((m, i) => (
              <div key={i} style={{
                padding: '10px 12px', borderRadius: '8px', background: 'rgba(0,0,0,0.2)',
                border: `1px solid ${m.status === 'low' ? 'rgba(245,158,11,0.3)' : 'rgba(51,65,85,0.5)'}`,
              }}>
                <div style={{ fontWeight: 600, fontSize: '0.8rem', color: '#f1f5f9', marginBottom: '4px' }}>{m.model}</div>
                <div style={{ fontSize: '0.7rem', color: '#818cf8', marginBottom: '6px' }}>{m.rate_tier}</div>
                {m.restrictions.map((r, j) => (
                  <div key={j} style={{ fontSize: '0.68rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>· {r}</div>
                ))}
                <div style={{ marginTop: '6px', fontSize: '0.68rem', color: m.status === 'low' ? '#fbbf24' : '#34d399' }}>
                  {m.status === 'low' ? '⚠ Low supply' : '● Available'} · {m.available_hours.toLocaleString()} hrs
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Submit button (Change 4) */}
      <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'flex-end' }}>
        <button className="btn btn-primary" onClick={() => setShowSubmitForm(!showSubmitForm)}>
          {showSubmitForm ? '✕ Close Form' : '+ Submit Contribution'}
        </button>
      </div>

      {/* Change 4 — Structured submission form */}
      {showSubmitForm && (
        <div className="card fade-in-up" style={{ marginBottom: '20px', borderColor: 'rgba(99,102,241,0.3)', background: 'rgba(99,102,241,0.03)' }}>
          <div style={{ fontWeight: 700, fontSize: '1rem', marginBottom: '16px', color: '#818cf8' }}>Submit a Contribution</div>

          {/* Change 2 — Pre-classify warning */}
          {classifyResult && classifyResult.quality_signal !== 'high' && (
            <div style={{
              padding: '12px 14px', marginBottom: '14px', borderRadius: '8px',
              background: classifyResult.quality_signal === 'generic' ? 'rgba(244,63,94,0.08)' : 'rgba(245,158,11,0.08)',
              border: `1px solid ${classifyResult.quality_signal === 'generic' ? 'rgba(244,63,94,0.3)' : 'rgba(245,158,11,0.3)'}`,
            }}>
              <div style={{ fontWeight: 700, fontSize: '0.8rem', color: classifyResult.quality_signal === 'generic' ? '#fb7185' : '#fbbf24', marginBottom: '4px' }}>
                {classifyResult.quality_signal === 'generic' ? '⚠ Generic submission detected' : '↓ Signal quality: ' + classifyResult.quality_signal}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{classifyResult.suggestion}</div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                Current signal modifier: <span style={{ color: '#818cf8' }}>{classifyResult.signal_quality_modifier_current?.toFixed(2)}×</span>
              </div>
            </div>
          )}
          {classifyResult && classifyResult.quality_signal === 'high' && (
            <div style={{ padding: '8px 14px', marginBottom: '14px', borderRadius: '8px', background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)', fontSize: '0.78rem', color: '#34d399' }}>
              ✓ {classifyResult.suggestion}
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Contribution Type</label>
              <select className="input" value={submitForm.type} onChange={e => setSubmitForm(f => ({...f, type: e.target.value}))}>
                {['domain_labeling','bug_report','edge_case','safety_testing','red_team_report','training_dataset','evaluation_framework','human_feedback_session'].map(t => (
                  <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>
                ))}
              </select>
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Domain *</label>
              <select className="input" value={submitForm.domain} onChange={e => setSubmitForm(f => ({...f, domain: e.target.value}))}>
                <option value="">Select domain...</option>
                {Object.entries(DOMAINS).map(([k,v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Submission Type *</label>
              <select className="input" value={submitForm.submission_type} onChange={e => setSubmitForm(f => ({...f, submission_type: e.target.value}))}>
                <option value="">Select type...</option>
                {['edge_case','error_report','blind_spot','domain_correction'].map(t => <option key={t} value={t}>{t.replace(/_/g,' ')}</option>)}
              </select>
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Title *</label>
              <input className="input" placeholder="Short title..." value={submitForm.title} onChange={e => setSubmitForm(f => ({...f, title: e.target.value}))} />
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '12px' }}>
            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>What did the model get wrong? * (min 20 chars)</label>
              <textarea className="input" rows={2} placeholder="Describe the specific failure..." value={submitForm.what_went_wrong}
                onChange={e => setSubmitForm(f => ({...f, what_went_wrong: e.target.value}))}
                onBlur={runPreClassify}
                style={{ resize: 'vertical' as const, width: '100%' }} />
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>What is the correct answer? * (min 10 chars)</label>
              <textarea className="input" rows={2} placeholder="The correct information is..." value={submitForm.correct_answer}
                onChange={e => setSubmitForm(f => ({...f, correct_answer: e.target.value}))}
                style={{ resize: 'vertical' as const, width: '100%' }} />
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Why does your domain qualify you to make this call? *</label>
              <input className="input" placeholder="e.g. I have a PhD in fermentation biology and 12 years industry experience..."
                value={submitForm.domain_qualification} onChange={e => setSubmitForm(f => ({...f, domain_qualification: e.target.value}))} />
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                Credential or published work reference <span style={{ color: '#34d399' }}>(optional — earns ✓ Verified Domain Expert flag)</span>
              </label>
              <input className="input" placeholder="DOI, URL, credential ID..."
                value={submitForm.credential_reference} onChange={e => setSubmitForm(f => ({...f, credential_reference: e.target.value}))} />
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Description (additional context)</label>
              <textarea className="input" rows={2} placeholder="Any additional context..."
                value={submitForm.description} onChange={e => setSubmitForm(f => ({...f, description: e.target.value}))}
                onBlur={runPreClassify} style={{ resize: 'vertical' as const, width: '100%' }} />
            </div>
          </div>

          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <button className="btn btn-primary" onClick={handleSubmit}>Submit Contribution</button>
            <button className="btn btn-secondary" onClick={runPreClassify} disabled={classifyLoading}>
              {classifyLoading ? 'Checking...' : 'Check Quality'}
            </button>
            {submitForm.credential_reference && (
              <span style={{ fontSize: '0.75rem', color: '#34d399' }}>✓ Verified Domain Expert flag will be applied</span>
            )}
          </div>
        </div>
      )}

      {/* Submit receipt modal (Change 4) */}
      {receiptVisible && submitResult && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', zIndex: 999,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }} onClick={() => setReceiptVisible(false)}>
          <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '16px', padding: '28px', maxWidth: '480px', width: '90%' }}
            onClick={e => e.stopPropagation()}>
            <div style={{ fontWeight: 800, fontSize: '1.1rem', marginBottom: '12px', color: '#34d399' }}>✓ Submission Receipt</div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.7 }}>
              <div><span style={{ color: 'var(--text)' }}>ID:</span> {submitResult.contribution_id}</div>
              <div><span style={{ color: 'var(--text)' }}>Status:</span> {submitResult.status}</div>
              <div><span style={{ color: 'var(--text)' }}>Domain:</span> {submitResult.domain || '—'}</div>
              <div><span style={{ color: 'var(--text)' }}>Type:</span> {submitResult.submission_type || '—'}</div>
              {submitResult.verified_domain_expert && (
                <div style={{ color: '#34d399', marginTop: '4px' }}>✓ Verified Domain Expert flag applied — visible to lab partners in review queue</div>
              )}
              <div style={{ marginTop: '8px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Credit receipt will be available at <span style={{ color: '#818cf8' }}>GET /intake/receipt/{submitResult.contribution_id}</span> once validation is complete.
              </div>
            </div>
            <button className="btn btn-secondary" style={{ marginTop: '16px' }} onClick={() => setReceiptVisible(false)}>Close</button>
          </div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
        {/* Contributions table */}
        <div>
          <div className="card fade-in-up stagger-2" style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>Contributions</div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{contributions.length} total</span>
              </div>
            </div>
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Type</th>
                    <th>Title</th>
                    <th>Status</th>
                    <th>Points</th>
                    <th>Credits</th>
                  </tr>
                </thead>
                <tbody>
                  {contributions.slice(0, 12).map(c => (
                    <tr key={c.id}>
                      <td>
                        <span style={{ fontSize: '0.72rem', fontFamily: 'monospace', color: '#818cf8' }}>
                          {c.type?.replace(/_/g, '_')}
                        </span>
                        {/* Change 3 + 5 — show verified + acted_on badges per row */}
                        <div style={{ display: 'flex', gap: '4px', marginTop: '2px', flexWrap: 'wrap' as const }}>
                          {c.verified_domain_expert && (
                            <span style={{ fontSize: '0.6rem', color: '#34d399', background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)', padding: '1px 5px', borderRadius: '4px' }}>✓ Verified</span>
                          )}
                          {c.acted_on && (
                            <span style={{ fontSize: '0.6rem', color: '#818cf8', background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)', padding: '1px 5px', borderRadius: '4px' }}>⚡ Acted on</span>
                          )}
                        </div>
                      </td>
                      <td>
                        <div style={{ maxWidth: '220px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontSize: '0.82rem' }}>
                          {c.title}
                        </div>
                        {c.domain && (
                          <div style={{ fontSize: '0.68rem', color: '#818cf8', marginTop: '1px' }}>{c.domain}</div>
                        )}
                        {c.abuse_flags && c.abuse_flags.length > 0 && (
                          <div style={{ fontSize: '0.68rem', color: '#fb7185', marginTop: '2px' }}>
                            ⚠️ {c.abuse_flags.join(', ')}
                          </div>
                        )}
                      </td>
                      <td><StatusPill status={c.status} /></td>
                      <td className="mono" style={{ color: '#818cf8' }}>{c.final_score ? Math.round(c.final_score) : '—'}</td>
                      <td className="mono" style={{ color: '#fbbf24' }}>{c.credit_equivalent ? `$${c.credit_equivalent.toFixed(2)}` : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Transaction ledger */}
          <div className="card fade-in-up stagger-3" style={{ marginTop: '16px', padding: 0, overflow: 'hidden' }}>
            <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', fontWeight: 700, fontSize: '0.95rem' }}>
              Credit Ledger
            </div>
            <table className="data-table">
              <thead><tr><th>Type</th><th>Amount</th><th>Description</th><th>Date</th></tr></thead>
              <tbody>
                {transactions.slice(0, 8).map(t => (
                  <tr key={t.id}>
                    <td><span className="badge badge-contributor">{t.type}</span></td>
                    <td className="mono" style={{ color: t.amount > 0 ? '#34d399' : '#fb7185' }}>
                      {t.amount > 0 ? '+' : ''}{t.amount?.toFixed(2)}
                    </td>
                    <td style={{ fontSize: '0.78rem', color: 'var(--text-muted)', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{t.description}</td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t.created_at?.slice(0, 10)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Maria test fixture callout */}
          {selectedId === 'contrib_004' && (
            <div className="card fade-in-up" style={{ borderColor: 'rgba(245,158,11,0.4)', background: 'rgba(245,158,11,0.05)' }}>
              <div style={{ fontWeight: 700, fontSize: '0.85rem', color: '#fbbf24', marginBottom: '10px' }}>📋 Maria's Test Fixture</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
                <strong style={{ color: 'var(--text)' }}>Fermentation Chemistry Labels</strong><br />
                Base: 250 × 1.7 × 1.5 × 1.10<br />
                <span className="mono" style={{ color: '#fbbf24' }}>=701 pts = $7.01</span><br /><br />
                Staked 200 credits → upheld → +50 bonus<br />
                Final: <span className="mono" style={{ color: '#34d399' }}>751 pts credited</span>
              </div>
            </div>
          )}

          {/* Leaderboard widget */}
          <div className="card fade-in-up stagger-2" style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border)', fontWeight: 700, fontSize: '0.9rem' }}>
              Top 10 Leaderboard
            </div>
            <div>
              {leaderboard.slice(0, 8).map((c: any) => (
                <div key={c.contributor_id} style={{
                  display: 'flex', alignItems: 'center', gap: '10px',
                  padding: '10px 14px', borderBottom: '1px solid rgba(51,65,85,0.4)',
                  cursor: 'pointer',
                  background: c.contributor_id === selectedId ? 'rgba(99,102,241,0.08)' : 'transparent',
                }} onClick={() => setSelectedId(c.contributor_id)}>
                  <span className="mono" style={{ color: 'var(--text-muted)', fontSize: '0.85rem', width: '24px' }}>#{c.rank}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{c.handle}</div>
                    <TierBadge tier={c.tier} />
                  </div>
                  <span className="mono" style={{ color: '#818cf8', fontSize: '0.82rem' }}>{c.points?.toLocaleString()}</span>
                </div>
              ))}
            </div>
            <div style={{ padding: '10px 14px' }}>
              <Link href="/leaderboard" className="btn btn-secondary" style={{ fontSize: '0.8rem', padding: '6px 12px' }}>
                Full Leaderboard →
              </Link>
            </div>
          </div>

          {/* Legal rails card */}
          <div className="card fade-in-up stagger-3" style={{ borderColor: 'rgba(244,63,94,0.2)', background: 'rgba(244,63,94,0.04)' }}>
            <div style={{ fontWeight: 700, fontSize: '0.85rem', color: '#fb7185', marginBottom: '8px' }}>⚖ Legal Rails</div>
            <ul style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.9, paddingLeft: '16px' }}>
              <li>Credits have no cash value</li>
              <li>Compute access redemption only</li>
              <li>Non-transferable between accounts</li>
              <li>Not investments — no guaranteed appreciation</li>
              <li>Exchange rate may adjust (30 days notice)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
