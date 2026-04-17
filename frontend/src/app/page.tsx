'use client'
import Link from 'next/link'
import { useEffect, useState } from 'react'

interface BrandData {
  platform_name: string
  tagline: string
  one_liner: string
  homepage_hero: string
  investor_description: string
  hospitality_vertical_pitch: string
}

interface PartnerStatus {
  active_partner_count: number
  total_compute_hours_available: number
  status: 'active' | 'limited' | 'offline'
  capacity_pct: number
}

export default function HomePage() {
  const [brand, setBrand] = useState<BrandData | null>(null)
  const [stats, setStats] = useState<{contributors: number, contributions: number, points: number} | null>(null)
  const [partners, setPartners] = useState<PartnerStatus | null>(null)

  useEffect(() => {
    fetch('/api/meta/brand').then(r => r.json()).then(setBrand).catch(() => {})
    fetch('/api/meta/partners').then(r => r.json()).then(setPartners).catch(() => {})
    fetch('/api/stats').then(r => r.json()).then(d => setStats({
      contributors: 25,
      contributions: d.total_contributions || 37,
      points: d.total_points_issued || 0,
    })).catch(() => {})
  }, [])

  const DASHBOARDS = [
    { href: '/dashboard/contributor', label: 'Contributor Dashboard', desc: 'Submit contributions, track your balance, monitor tier progression', icon: '◈', color: '#6366f1' },
    { href: '/dashboard/validator', label: 'Validator Dashboard', desc: 'Review submissions, attest quality, stake credits on high-conviction decisions', icon: '⧖', color: '#f59e0b' },
    { href: '/dashboard/governance', label: 'Governance', desc: 'Bicameral proposals, Expert Council ratification, dispute resolution', icon: '⚖', color: '#10b981' },
    { href: '/dashboard/trust', label: 'Trust Scores', desc: 'Full trust score breakdowns, fraud detection, network health', icon: '◎', color: '#8b5cf6' },
    { href: '/leaderboard', label: 'Leaderboard', desc: 'Top 50 contributors ranked by points, tier, and domain', icon: '⬙', color: '#f43f5e' },
  ]

  return (
    <div style={{ padding: '48px 48px', maxWidth: '1100px' }}>
      {/* Change 6 — Partner Status Bar (visible without login) */}
      {partners && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '10px',
          padding: '10px 16px', marginBottom: '20px',
          background: 'rgba(16,185,129,0.06)', border: '1px solid rgba(16,185,129,0.2)',
          borderRadius: '10px', fontSize: '0.82rem',
        }}>
          <span style={{
            width: '8px', height: '8px', borderRadius: '50%', flexShrink: 0,
            background: partners.status === 'active' ? '#10b981' : partners.status === 'limited' ? '#f59e0b' : '#ef4444',
            boxShadow: `0 0 6px ${partners.status === 'active' ? '#10b981' : '#f59e0b'}`,
          }} />
          <span style={{ color: partners.status === 'active' ? '#34d399' : '#fbbf24', fontWeight: 600 }}>
            {partners.active_partner_count} active compute partner{partners.active_partner_count !== 1 ? 's' : ''}
          </span>
          <span style={{ color: 'var(--text-muted)' }}>·</span>
          <span style={{ color: 'var(--text-muted)' }}>
            {partners.total_compute_hours_available.toLocaleString()} GPU-hrs available
          </span>
          <span style={{ color: 'var(--text-muted)' }}>·</span>
          <span style={{ color: partners.status === 'active' ? '#34d399' : '#fbbf24' }}>
            {partners.status === 'active' ? '● Live' : partners.status === 'limited' ? '⚠ Limited' : '○ Offline'}
          </span>
        </div>
      )}
      {/* Hero */}
      <div className="hero-card fade-in-up" style={{ marginBottom: '48px' }}>
        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ marginBottom: '12px' }}>
            <span className="badge badge-partner" style={{ marginBottom: '12px' }}>
              Credit Economy + Governance
            </span>
          </div>
          <h1 style={{
            fontSize: '2.8rem', fontWeight: 900, lineHeight: 1.1,
            background: 'linear-gradient(135deg, #f1f5f9 0%, #818cf8 60%, #a78bfa 100%)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            marginBottom: '16px',
          }}>
            {brand?.homepage_hero || 'The next AI divide isn\'t intelligence.\nIt\'s access.'}
          </h1>
          <p style={{ fontSize: '1.05rem', color: 'var(--text-muted)', maxWidth: '620px', lineHeight: 1.7, marginBottom: '28px' }}>
            {brand?.one_liner || 'A peer-governed network where verified contribution to AI earns redeemable compute access — not cash, access.'}
          </p>
          <div style={{ display: 'flex', gap: '12px' }}>
            <Link href="/dashboard/contributor" className="btn btn-primary">
              View Contributor Dashboard →
            </Link>
            <Link href="/dashboard/governance" className="btn btn-secondary">
              Governance →
            </Link>
          </div>
        </div>
      </div>

      {/* Stats row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '40px' }}>
        {[
          { label: 'Contributors', value: stats?.contributors ?? 25, color: '#6366f1', suffix: '' },
          { label: 'Contributions', value: stats?.contributions ?? 37, color: '#f59e0b', suffix: '' },
          { label: 'Points Issued', value: stats?.points ? Math.round(stats.points).toLocaleString() : '—', color: '#10b981', suffix: '' },
          { label: 'Compute Commons', value: 'v2.0', color: '#8b5cf6', suffix: '' },
        ].map((s, i) => (
          <div key={i} className={`card fade-in-up stagger-${i+1}`} style={{ textAlign: 'center' }}>
            <div className="num-lg" style={{ color: s.color }}>{s.value}{s.suffix}</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Dashboard cards */}
      <div className="section-label">Dashboards</div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '40px' }}>
        {DASHBOARDS.map((d, i) => (
          <Link key={d.href} href={d.href} style={{ textDecoration: 'none' }}>
            <div className={`card card-hover fade-in-up stagger-${i+1}`} style={{ height: '100%' }}>
              <div style={{ fontSize: '1.75rem', marginBottom: '12px' }}>{d.icon}</div>
              <div style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: '6px', color: d.color }}>{d.label}</div>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>{d.desc}</div>
            </div>
          </Link>
        ))}
      </div>

      {/* Investor pitch */}
      <div className="card fade-in-up" style={{ borderColor: 'rgba(99,102,241,0.25)', background: 'rgba(99,102,241,0.05)' }}>
        <div className="section-label">Platform Overview</div>
        <p style={{ fontSize: '0.9rem', lineHeight: 1.8, color: 'var(--text-muted)', maxWidth: '720px' }}>
          {brand?.investor_description || 'Compute Commons converts verified model improvements into AI compute credits via peer governance, trust-chain validation, and a fixed-floor credit economy.'}
        </p>
        <div style={{ marginTop: '16px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {['Non-transferable credits', 'Compute access only', 'Not securities', 'Not cash', 'Peer-governed'].map(tag => (
            <span key={tag} className="badge badge-contributor">{tag}</span>
          ))}
        </div>
      </div>
    </div>
  )
}
