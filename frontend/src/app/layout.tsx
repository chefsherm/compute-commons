import type { Metadata } from 'next'
import './globals.css'
import Link from 'next/link'
import {
  LayoutDashboard,
  ShieldCheck,
  Scale,
  Award,
  Trophy,
  Terminal,
  ChevronRight,
  Briefcase,
} from 'lucide-react'

export const metadata: Metadata = {
  title: 'Compute Commons — Earn your seat at the frontier.',
  description: 'A peer-governed network where verified contribution to AI earns redeemable compute access — not cash, access.',
}

const NAV_LINKS = [
  { href: '/',                        label: 'Home',                icon: LayoutDashboard },
  { href: '/dashboard/contributor',   label: 'Contributor',         icon: Award           },
  { href: '/dashboard/validator',     label: 'Validator',           icon: ShieldCheck     },
  { href: '/dashboard/governance',    label: 'Governance',          icon: Scale           },
  { href: '/dashboard/trust',         label: 'Trust',               icon: ShieldCheck     },
  { href: '/leaderboard',             label: 'Leaderboard',         icon: Trophy          },
  { href: '/partner/workspace',       label: 'Partner Workspace',   icon: Briefcase       },
]

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="flex min-h-screen bg-slate-50">

          {/* ── Sidebar ──────────────────────────────────────────────────── */}
          <aside className="cc-sidebar">

            {/* Logo */}
            <div className="cc-sidebar-logo">
              <div className="cc-sidebar-logo-icon">
                <Terminal className="w-4 h-4 text-white" />
              </div>
              <div>
                <div className="font-bold text-sm text-slate-900 leading-tight tracking-tight">
                  Compute
                </div>
                <div className="font-bold text-sm text-indigo-600 leading-tight tracking-tight">
                  Commons
                </div>
              </div>
              <span className="ml-auto text-[9px] font-semibold text-slate-300 uppercase tracking-widest border border-slate-200 rounded px-1.5 py-0.5">
                v2
              </span>
            </div>

            {/* Navigation */}
            <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-0.5">
              <div className="cc-nav-section-label px-3 py-2">Navigation</div>
              {NAV_LINKS.map(({ href, label, icon: Icon }) => (
                <Link key={href} href={href} className="cc-nav-link">
                  <Icon className="nav-icon" />
                  <span>{label}</span>
                </Link>
              ))}
            </nav>

            {/* Legal footer */}
            <div className="px-5 py-4 border-t border-slate-100">
              <p className="text-[10px] text-slate-400 leading-relaxed">
                Credits have no cash value.<br />
                Compute access only. Non-transferable.
              </p>
            </div>
          </aside>

          {/* ── Main content ─────────────────────────────────────────────── */}
          <main
            className="flex-1 min-h-screen overflow-y-auto"
            style={{ marginLeft: 'var(--sidebar-w)' }}
          >
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
