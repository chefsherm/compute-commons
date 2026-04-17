'use client'
import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'

const API = '/api'

interface PublicProfile {
  handle: string
  progression_tier: string
  progression_tier_label: string
  badge_color: string
  tier_description: string
  platform_tier: string
  domains: string[]
  accuracy_rate: number
  validated_submissions: number
  acted_on_count: number
  contribution_type_breakdown: Record<string, number>
  member_since: string
  trust_score: number
  public_url: string
}

export default function PublicProfilePage() {
  const params = useParams()
  const handle = params?.handle as string
  const [profile, setProfile] = useState<PublicProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    if (!handle) return
    fetch(`${API}/progression/profile/${handle}`)
      .then(r => { if (!r.ok) throw new Error(); return r.json() })
      .then(setProfile)
      .catch(() => setError(true))
      .finally(() => setLoading(false))
  }, [handle])

  if (loading) return (
    <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
      Loading profile...
    </div>
  )

  if (error || !profile) return (
    <div style={{ padding: '60px', textAlign: 'center' }}>
      <div style={{ fontSize: '2rem', marginBottom: '12px' }}>¬</div>
      <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No contributor found with handle "{handle}"</div>
      <Link href="/" className="btn btn-secondary" style={{ marginTop: '20px', display: 'inline-block' }}>← Home</Link>
    </div>
  )

  const typeEntries = Object.entries(profile.contribution_type_breakdown).sort((a, b) => b[1] - a[1])

  return (
    <div style={{ padding: '48px', maxWidth: '800px' }}>
      {/* Public notice */}
      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '20px', padding: '6px 12px', background: 'rgba(99,102,241,0.06)', borderRadius: '6px', display: 'inline-block' }}>
        Public profile · No login required · {`computecommons.ai/profile/${handle}`}
      </div>

      {/* Hero */}
      <div className="hero-card fade-in-up" style={{ marginBottom: '28px' }}>
        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '20px' }}>
            <div style={{
              width: '56px', height: '56px', borderRadius: '50%', flexShrink: 0,
              background: `linear-gradient(135deg, ${profile.badge_color}40, ${profile.badge_color}20)`,
              border: `2px solid ${profile.badge_color}60`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '1.4rem',
            }}>⬡</div>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px', flexWrap: 'wrap' }}>
                <h1 style={{ fontSize: '1.8rem', fontWeight: 900, margin: 0 }}>{profile.handle}</h1>
                <span style={{
                  fontSize: '0.7rem', fontWeight: 700, padding: '3px 10px', borderRadius: '12px',
                  border: `1px solid ${profile.badge_color}40`,
                  background: `${profile.badge_color}15`, color: profile.badge_color,
                  letterSpacing: '0.06em', textTransform: 'uppercase' as const,
                }}>⬡ {profile.progression_tier_label}</span>
                <span className={`badge badge-${profile.platform_tier}`}>{profile.platform_tier}</span>
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
                {profile.tier_description}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Member since {profile.member_since}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '24px' }}>
        {[
          { label: 'Validated Submissions', value: profile.validated_submissions, color: '#818cf8' },
          { label: 'Accuracy Rate', value: `${(profile.accuracy_rate * 100).toFixed(0)}%`, color: '#10b981' },
          { label: 'Acted On by Lab', value: profile.acted_on_count, color: '#34d399' },
          { label: 'Trust Score', value: profile.trust_score.toFixed(1), color: '#f59e0b' },
        ].map((s, i) => (
          <div key={i} className="card" style={{ textAlign: 'center', padding: '16px' }}>
            <div className="num-lg" style={{ color: s.color }}>{s.value}</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '4px' }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Domains */}
      {profile.domains.length > 0 && (
        <div className="card fade-in-up" style={{ marginBottom: '16px' }}>
          <div style={{ fontWeight: 700, fontSize: '0.9rem', marginBottom: '10px' }}>Domains Flagged</div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {profile.domains.map(d => (
              <span key={d} className="badge badge-contributor" style={{ fontSize: '0.72rem' }}>{d.replace(/_/g, ' ')}</span>
            ))}
          </div>
        </div>
      )}

      {/* Contribution type breakdown */}
      {typeEntries.length > 0 && (
        <div className="card fade-in-up" style={{ marginBottom: '16px' }}>
          <div style={{ fontWeight: 700, fontSize: '0.9rem', marginBottom: '12px' }}>Contribution Breakdown</div>
          {typeEntries.map(([type, count]) => {
            const maxCount = typeEntries[0][1]
            return (
              <div key={type} style={{ marginBottom: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
                  <span style={{ fontSize: '0.75rem', fontFamily: 'monospace', color: '#818cf8' }}>{type.replace(/_/g, '_')}</span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{count}</span>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '4px', height: '4px' }}>
                  <div style={{
                    height: '100%', borderRadius: '4px',
                    background: 'linear-gradient(90deg, #6366f1, #8b5cf6)',
                    width: `${(count / maxCount) * 100}%`,
                  }} />
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Acted-on note */}
      {profile.acted_on_count > 0 && (
        <div className="card fade-in-up" style={{ borderColor: 'rgba(16,185,129,0.2)', background: 'rgba(16,185,129,0.04)', marginBottom: '16px' }}>
          <div style={{ fontWeight: 700, fontSize: '0.85rem', color: '#34d399', marginBottom: '6px' }}>
            ⚡ {profile.acted_on_count} submission{profile.acted_on_count !== 1 ? 's' : ''} acted on by a lab partner
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Lab partners flagged these contributions as directly used in model development, evaluation, or safety work.
          </div>
        </div>
      )}

      {/* Legal rail */}
      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border)', paddingTop: '16px', lineHeight: 1.6 }}>
        Compute Commons credits have no cash value, are non-transferable, and redeem for compute access only.
        This profile is public. No personally identifiable information is displayed.
      </div>

      <div style={{ marginTop: '16px' }}>
        <Link href="/dashboard/contributor" className="btn btn-secondary" style={{ fontSize: '0.8rem' }}>← Contributor Dashboard</Link>
      </div>
    </div>
  )
}
