'use client'
import { useEffect, useState, useCallback } from 'react'

function TierBadge({ tier }: { tier: string }) {
  return <span className={`badge badge-${tier}`}>{tier}</span>
}

export default function LeaderboardPage() {
  const [leaders, setLeaders] = useState<any[]>([])
  const [filtered, setFiltered] = useState<any[]>([])
  const [tierFilter, setTierFilter] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [exchangeRate, setExchangeRate] = useState<any>(null)

  const load = async () => {
    setLoading(true)
    try {
      const [lb, er] = await Promise.all([
        fetch('/api/scoring/leaderboard?limit=50').then(r => r.json()),
        fetch('/api/scoring/exchange-rate').then(r => r.json()),
      ])
      setLeaders(lb)
      setFiltered(lb)
      setExchangeRate(er)
    } catch(e) {}
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  useEffect(() => {
    let result = [...leaders]
    if (tierFilter) result = result.filter(c => c.tier === tierFilter)
    if (search) result = result.filter(c => c.handle.toLowerCase().includes(search.toLowerCase()))
    setFiltered(result)
  }, [tierFilter, search, leaders])

  if (loading) return (
    <div style={{ padding: '48px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div className="skeleton" style={{ height: '80px' }} />
      <div className="skeleton" style={{ height: '400px' }} />
    </div>
  )

  const RANK_COLORS: Record<number, string> = { 1: '#fbbf24', 2: '#94a3b8', 3: '#cd7c3f' }

  return (
    <div style={{ padding: '32px 40px', maxWidth: '1100px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '4px' }}>Leaderboard</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Top contributors ranked by points · All-time</p>
      </div>

      {/* Exchange rate status */}
      {exchangeRate && (
        <div className="card fade-in-up" style={{
          marginBottom: '20px',
          borderColor: exchangeRate.inflation_guard ? 'rgba(245,158,11,0.4)' : 'rgba(16,185,129,0.2)',
          background: exchangeRate.inflation_guard ? 'rgba(245,158,11,0.05)' : 'rgba(16,185,129,0.04)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
            <div>
              <div className="section-label">Exchange Rate</div>
              <div className="num-md" style={{ color: '#34d399' }}>1pt = ${exchangeRate.dollar_per_point}</div>
            </div>
            <div>
              <div className="section-label">Helpfulness Ceiling</div>
              <div className="num-md" style={{ color: exchangeRate.inflation_guard ? '#fbbf24' : '#34d399' }}>
                {exchangeRate.helpfulness_multiplier_ceiling}×
              </div>
            </div>
            <div>
              <div className="section-label">Inflation Guard</div>
              <div style={{ fontWeight: 700, color: exchangeRate.inflation_guard ? '#fbbf24' : '#34d399' }}>
                {exchangeRate.inflation_guard ? '⚠ ACTIVE' : '✓ Inactive'}
              </div>
            </div>
            <div style={{ flex: 1, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              {exchangeRate.note}
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '20px', alignItems: 'center' }}>
        <input className="input" style={{ maxWidth: '240px' }} placeholder="Search handle..." value={search}
          onChange={e => setSearch(e.target.value)} />
        <select className="input" style={{ maxWidth: '160px' }} value={tierFilter} onChange={e => setTierFilter(e.target.value)}>
          <option value="">All Tiers</option>
          <option value="partner">Partner</option>
          <option value="expert">Expert</option>
          <option value="validator">Validator</option>
          <option value="contributor">Contributor</option>
        </select>
        <button className="btn btn-secondary" onClick={() => { setTierFilter(''); setSearch('') }}>
          Clear
        </button>
        <button className="btn btn-primary" onClick={load}>↻ Refresh</button>
        <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginLeft: 'auto' }}>
          {filtered.length} of {leaders.length} contributors
        </span>
      </div>

      {/* Top 3 podium */}
      {!tierFilter && !search && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', marginBottom: '24px' }}>
          {[1, 0, 2].map(idx => {
            const c = leaders[idx]
            if (!c) return null
            const rank = idx + 1
            const isFirst = idx === 0
            return (
              <div key={c.contributor_id} className={`hero-card fade-in-up stagger-${idx+1}`}
                style={{
                  textAlign: 'center', order: idx === 1 ? -1 : idx === 0 ? 0 : 1,
                  transform: isFirst ? 'scale(1.04)' : 'scale(1)',
                  borderColor: `${RANK_COLORS[rank]}40`,
                }}>
                <div style={{ fontSize: '2rem', marginBottom: '8px' }}>
                  {rank === 1 ? '🥇' : rank === 2 ? '🥈' : '🥉'}
                </div>
                <div style={{ fontWeight: 800, fontSize: '1rem', marginBottom: '6px' }}>{c.handle}</div>
                <TierBadge tier={c.tier} />
                <div className="num-lg" style={{ color: RANK_COLORS[rank], marginTop: '10px' }}>
                  {c.points?.toLocaleString()}
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>points</div>
                <div style={{ marginTop: '8px', fontSize: '0.78rem', color: '#34d399' }}>
                  ${c.credits_balance?.toFixed(2)} credits
                </div>
                <div style={{ marginTop: '4px' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    Trust: {c.trust_score?.toFixed(1)} · Accuracy: {(c.accuracy_score * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Full table */}
      <div className="card fade-in-up" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ width: '48px' }}>Rank</th>
              <th>Contributor</th>
              <th>Tier</th>
              <th>Points</th>
              <th>Credits</th>
              <th>Trust</th>
              <th>Accuracy</th>
              <th>Domains</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((c: any, i) => (
              <tr key={c.contributor_id} className="fade-in-up" style={{ animationDelay: `${i * 20}ms` }}>
                <td>
                  <span className="mono" style={{
                    fontWeight: 700,
                    color: RANK_COLORS[i + 1] || 'var(--text-muted)',
                    fontSize: i < 3 ? '1rem' : '0.875rem',
                  }}>
                    {i < 3 ? ['🥇','🥈','🥉'][i] : `#${i + 1}`}
                  </span>
                </td>
                <td>
                  <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{c.handle}</div>
                </td>
                <td><TierBadge tier={c.tier} /></td>
                <td className="mono" style={{ color: '#818cf8', fontWeight: 600 }}>{c.points?.toLocaleString()}</td>
                <td className="mono" style={{ color: '#fbbf24' }}>${c.credits_balance?.toFixed(2)}</td>
                <td>
                  <span className="mono" style={{
                    color: c.trust_score >= 70 ? '#34d399' : c.trust_score >= 40 ? '#818cf8' : '#fb7185'
                  }}>
                    {c.trust_score?.toFixed(1)}
                  </span>
                </td>
                <td className="mono" style={{ color: c.accuracy_score >= 0.9 ? '#34d399' : c.accuracy_score < 0.6 ? '#fb7185' : 'var(--text)' }}>
                  {(c.accuracy_score * 100).toFixed(0)}%
                </td>
                <td style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  {c.domains?.slice(0, 2).join(', ')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
