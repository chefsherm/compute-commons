import type { Metadata } from 'next'
import './globals.css'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Compute Commons — Earn your seat at the frontier.',
  description: 'A peer-governed network where verified contribution to AI earns redeemable compute access — not cash, access.',
}

const NAV_LINKS = [
  { href: '/', label: 'Home', icon: '⬡' },
  { href: '/dashboard/contributor', label: 'Contributor', icon: '◈' },
  { href: '/dashboard/validator', label: 'Validator', icon: '⧖' },
  { href: '/dashboard/governance', label: 'Governance', icon: '⚖' },
  { href: '/dashboard/trust', label: 'Trust', icon: '◎' },
  { href: '/leaderboard', label: 'Leaderboard', icon: '⬙' },
]

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div style={{ display: 'flex', minHeight: '100vh' }}>
          {/* Sidebar */}
          <aside style={{
            width: '220px',
            background: 'var(--surface)',
            borderRight: '1px solid var(--border)',
            display: 'flex',
            flexDirection: 'column',
            padding: '0',
            position: 'fixed',
            top: 0,
            left: 0,
            height: '100vh',
            zIndex: 100,
          }}>
            {/* Logo */}
            <div style={{ padding: '20px 20px 16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{
                  width: '32px', height: '32px', borderRadius: '8px',
                  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '16px', boxShadow: '0 4px 12px rgba(99,102,241,0.4)',
                }}>⬡</div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.9rem', lineHeight: '1.1' }}>Compute</div>
                  <div style={{ fontWeight: 700, fontSize: '0.9rem', color: '#818cf8', lineHeight: '1.1' }}>Commons</div>
                </div>
              </div>
              <div style={{ marginTop: '6px', fontSize: '0.62rem', color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
                Phase 2
              </div>
            </div>

            <div style={{ width: 'calc(100% - 32px)', margin: '0 16px', borderTop: '1px solid var(--border)' }} />

            {/* Nav links */}
            <nav style={{ padding: '12px 12px', flex: 1, display: 'flex', flexDirection: 'column', gap: '2px' }}>
              <div className="section-label" style={{ paddingLeft: '8px', marginBottom: '8px' }}>Navigation</div>
              {NAV_LINKS.map(link => (
                <Link key={link.href} href={link.href} className="nav-link">
                  <span style={{ fontSize: '1rem', lineHeight: 1 }}>{link.icon}</span>
                  {link.label}
                </Link>
              ))}
            </nav>

            {/* Bottom legal notice */}
            <div style={{ padding: '12px 16px', borderTop: '1px solid var(--border)' }}>
              <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                Credits have no cash value. Compute access only.<br />
                Non-transferable. Not investments.
              </div>
            </div>
          </aside>

          {/* Main content */}
          <main style={{ marginLeft: '220px', flex: 1, minHeight: '100vh' }}>
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
