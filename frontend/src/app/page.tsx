'use client'
import Link from 'next/link'
import { useEffect, useState } from 'react'
import {
  Award, ShieldCheck, Scale, Trophy, Briefcase,
  Zap, Activity, Users, BarChart3,
  ArrowRight, CheckCircle2,
} from 'lucide-react'

// ── Types ──────────────────────────────────────────────────────────────────

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

// ── Dashboard card data ────────────────────────────────────────────────────

const DASHBOARDS = [
  {
    href:  '/dashboard/contributor',
    label: 'Contributor Dashboard',
    desc:  'Submit contributions, track your credit balance, and monitor tier progression.',
    icon:  Award,
    color: 'text-indigo-600',
    bg:    'bg-indigo-50',
  },
  {
    href:  '/dashboard/validator',
    label: 'Validator Queue',
    desc:  'Review submissions, attest quality, and stake credits on high-conviction decisions.',
    icon:  ShieldCheck,
    color: 'text-amber-600',
    bg:    'bg-amber-50',
  },
  {
    href:  '/dashboard/governance',
    label: 'Governance',
    desc:  'Bicameral proposals, Expert Council ratification, and dispute resolution.',
    icon:  Scale,
    color: 'text-emerald-600',
    bg:    'bg-emerald-50',
  },
  {
    href:  '/dashboard/trust',
    label: 'Trust Scores',
    desc:  'Full trust score breakdowns, fraud detection signals, and network health.',
    icon:  Activity,
    color: 'text-violet-600',
    bg:    'bg-violet-50',
  },
  {
    href:  '/leaderboard',
    label: 'Leaderboard',
    desc:  'Top 50 contributors ranked by points, tier, and domain expertise.',
    icon:  Trophy,
    color: 'text-rose-600',
    bg:    'bg-rose-50',
  },
  {
    href:  '/partner/workspace',
    label: 'Partner Workspace',
    desc:  'Enterprise expert discovery — inspect verified work samples and request secure intros.',
    icon:  Briefcase,
    color: 'text-sky-600',
    bg:    'bg-sky-50',
  },
]

// ── Component ──────────────────────────────────────────────────────────────

export default function HomePage() {
  const [brand,   setBrand]   = useState<BrandData | null>(null)
  const [stats,   setStats]   = useState<{ contributors: number; contributions: number; points: number } | null>(null)
  const [partners, setPartners] = useState<PartnerStatus | null>(null)

  useEffect(() => {
    fetch('/api/meta/brand').then(r => r.json()).then(setBrand).catch(() => {})
    fetch('/api/meta/partners').then(r => r.json()).then(setPartners).catch(() => {})
    fetch('/api/scoring/stats').then(r => r.json()).then(d => setStats({
      contributors:  25,
      contributions: d.total_contributions || 37,
      points:        d.total_points_issued  || 0,
    })).catch(() => {})
  }, [])

  const statusColor = partners?.status === 'active'
    ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
    : partners?.status === 'limited'
      ? 'bg-amber-50 text-amber-700 border-amber-200'
      : 'bg-slate-100 text-slate-600 border-slate-200'

  const dotColor = partners?.status === 'active' ? 'bg-emerald-500' :
                   partners?.status === 'limited' ? 'bg-amber-400'  : 'bg-slate-300'

  return (
    <div className="cc-page max-w-6xl mx-auto">

      {/* ── Partner Status Badge ──────────────────────────────────────────── */}
      {partners && (
        <div className="animate-fade-in-up mb-6">
          <div className={`inline-flex items-center gap-2.5 border rounded-full px-4 py-2 text-sm font-medium ${statusColor}`}>
            <span className={`w-2 h-2 rounded-full flex-shrink-0 ${dotColor} ${partners.status === 'active' ? 'animate-pulse' : ''}`} />
            <span>
              {partners.active_partner_count} active compute partner{partners.active_partner_count !== 1 ? 's' : ''}
            </span>
            <span className="opacity-40">·</span>
            <span className="font-normal opacity-80">
              {partners.total_compute_hours_available.toLocaleString()} GPU-hrs available
            </span>
            <span className="opacity-40">·</span>
            <span>
              {partners.status === 'active' ? '● Live' : partners.status === 'limited' ? '⚠ Limited' : '○ Offline'}
            </span>
          </div>
        </div>
      )}

      {/* ── Hero Card ─────────────────────────────────────────────────────── */}
      <div className="cc-card-hero animate-fade-in-up mb-8">
        {/* Decorative gradient blob */}
        <div
          className="absolute top-0 right-0 w-72 h-72 rounded-full opacity-[0.06] pointer-events-none"
          style={{ background: 'radial-gradient(circle, #4f46e5 0%, transparent 70%)', transform: 'translate(30%, -30%)' }}
        />

        <div className="relative">
          <span className="cc-badge-brand mb-4 inline-flex">
            Credit Economy + Governance
          </span>

          <h1 className="text-4xl font-bold tracking-tightest text-slate-900 leading-tight mb-4 max-w-2xl text-balance">
            {brand?.homepage_hero || "The next AI divide isn't intelligence.\nIt's access."}
          </h1>

          <p className="text-base text-slate-500 max-w-xl leading-relaxed mb-8">
            {brand?.one_liner ||
              'A peer-governed network where verified contribution to AI earns redeemable compute access — not cash, access.'}
          </p>

          <div className="flex items-center gap-3 flex-wrap">
            <Link href="/dashboard/contributor" className="cc-btn-primary">
              Contributor Dashboard
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link href="/dashboard/governance" className="cc-btn-secondary">
              Governance
            </Link>
          </div>
        </div>
      </div>

      {/* ── Stats Row ─────────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        {[
          { label: 'Contributors',     value: stats?.contributors  ?? 25,                         icon: Users,    color: 'text-indigo-600', bg: 'bg-indigo-50'  },
          { label: 'Contributions',    value: stats?.contributions ?? 37,                         icon: Zap,      color: 'text-amber-600',  bg: 'bg-amber-50'   },
          { label: 'Points Issued',    value: stats?.points ? Math.round(stats.points).toLocaleString() : '—', icon: BarChart3, color: 'text-emerald-600', bg: 'bg-emerald-50' },
          { label: 'Platform Version', value: 'v2.0',                                              icon: CheckCircle2, color: 'text-violet-600', bg: 'bg-violet-50' },
        ].map((s, i) => {
          const Icon = s.icon
          return (
            <div key={i} className={`cc-card animate-fade-in-up stagger-${i + 1} text-center`}>
              <div className={`w-10 h-10 ${s.bg} rounded-xl flex items-center justify-center mx-auto mb-3`}>
                <Icon className={`w-5 h-5 ${s.color}`} />
              </div>
              <div className={`cc-num-md font-bold tabular-nums ${s.color}`}>
                {s.value}
              </div>
              <div className="text-xs text-slate-400 mt-1 font-medium">
                {s.label}
              </div>
            </div>
          )
        })}
      </div>

      {/* ── Dashboard Cards ───────────────────────────────────────────────── */}
      <div className="mb-10">
        <div className="cc-section-label mb-4">Dashboards &amp; Tools</div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {DASHBOARDS.map((d, i) => {
            const Icon = d.icon
            return (
              <Link key={d.href} href={d.href} className="block group">
                <div className={`cc-card cc-card-hover animate-fade-in-up stagger-${i + 1} h-full`}>
                  <div className={`w-11 h-11 ${d.bg} rounded-xl flex items-center justify-center mb-4`}>
                    <Icon className={`w-5 h-5 ${d.color}`} />
                  </div>
                  <h3 className={`text-sm font-semibold tracking-tight mb-2 ${d.color}`}>
                    {d.label}
                  </h3>
                  <p className="text-xs text-slate-500 leading-relaxed mb-4">
                    {d.desc}
                  </p>
                  <div className="flex items-center gap-1 text-xs font-medium text-slate-400 group-hover:text-indigo-600 transition-colors">
                    Open
                    <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
                  </div>
                </div>
              </Link>
            )
          })}
        </div>
      </div>

      {/* ── Platform Overview ─────────────────────────────────────────────── */}
      <div className="cc-card animate-fade-in-up border-indigo-100" style={{ background: 'linear-gradient(135deg, #eef2ff 0%, #ffffff 60%)' }}>
        <div className="cc-section-label mb-3">Platform Overview</div>
        <p className="text-sm text-slate-600 leading-relaxed max-w-2xl mb-5">
          {brand?.investor_description ||
            'Compute Commons converts verified model improvements into AI compute credits via peer governance, trust-chain validation, and a fixed-floor credit economy.'}
        </p>
        <div className="flex flex-wrap gap-2">
          {['Non-transferable credits', 'Compute access only', 'Not securities', 'Not cash', 'Peer-governed'].map(tag => (
            <span key={tag} className="cc-tag">{tag}</span>
          ))}
        </div>
      </div>
    </div>
  )
}
