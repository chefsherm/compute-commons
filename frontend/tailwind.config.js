/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],

  theme: {
    extend: {

      // ── Typography ────────────────────────────────────────────────────────
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'ui-monospace', 'monospace'],
      },

      // ── Brand color overrides ─────────────────────────────────────────────
      // Tailwind's full slate/indigo/emerald/amber/rose palettes are
      // already included; we only add the custom tokens below.
      colors: {
        // Slate-950 (not in Tailwind v3 by default)
        slate: {
          950: '#020617',
        },

        // Brand: Compute Commons Indigo
        brand: {
          50:  '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',   // PRIMARY ACTION
          700: '#4338ca',   // HOVER
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b',
        },

        // Semantic: Earned / Approved
        earned: {
          50:  '#ecfdf5',
          400: '#34d399',
          500: '#10b981',
          600: '#059669',   // PRIMARY EMERALD
          700: '#047857',
        },

        // Semantic: Staked / Pending
        staked: {
          50:  '#fffbeb',
          400: '#fbbf24',
          500: '#f59e0b',   // PRIMARY AMBER
          600: '#d97706',
        },

        // Semantic: Flagged / Rejected
        flagged: {
          50:  '#fff1f2',
          400: '#fb7185',
          500: '#f43f5e',   // PRIMARY ROSE
          600: '#e11d48',
        },
      },

      // ── Spacing & layout ──────────────────────────────────────────────────
      spacing: {
        18: '4.5rem',
        22: '5.5rem',
        112: '28rem',
        128: '32rem',
      },

      // ── Border radius ─────────────────────────────────────────────────────
      borderRadius: {
        '2xl': '1rem',      // 16px — hero cards
        '3xl': '1.5rem',    // 24px — feature highlights
      },

      // ── Box shadow ────────────────────────────────────────────────────────
      // Design rule: "Never use heavy drop shadows."
      boxShadow: {
        // Default card elevation
        card:    '0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px -1px rgb(0 0 0 / 0.06)',
        // Lifted on hover
        'card-md': '0 4px 12px -2px rgb(0 0 0 / 0.08), 0 2px 4px -2px rgb(0 0 0 / 0.06)',
        // Focus rings
        'focus-brand': '0 0 0 3px rgb(79 70 229 / 0.18)',
        // Inline highlight (used on score rings)
        'ring-earned': '0 0 0 3px rgb(16 185 129 / 0.18)',
        'ring-staked': '0 0 0 3px rgb(245 158 11 / 0.18)',
        'ring-flagged': '0 0 0 3px rgb(244 63 94 / 0.18)',
      },

      // ── Typography scale ──────────────────────────────────────────────────
      fontSize: {
        '2xs': ['0.65rem',  { lineHeight: '1rem' }],
        'xs':  ['0.75rem',  { lineHeight: '1.125rem' }],
        'sm':  ['0.875rem', { lineHeight: '1.375rem' }],
        'base': ['1rem',    { lineHeight: '1.625rem' }],
        'lg':  ['1.125rem', { lineHeight: '1.75rem' }],
        'xl':  ['1.25rem',  { lineHeight: '1.875rem' }],
        '2xl': ['1.5rem',   { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.375rem' }],
        '4xl': ['2.25rem',  { lineHeight: '2.75rem' }],
        '5xl': ['3rem',     { lineHeight: '3.5rem' }],
      },

      // ── Letter spacing ────────────────────────────────────────────────────
      letterSpacing: {
        tightest: '-0.05em',  // Large display headings
        tight:    '-0.025em', // All H1–H3
        normal:   '0em',
        wide:     '0.025em',
        widest:   '0.1em',    // ALL-CAPS section labels
      },

      // ── Transitions ───────────────────────────────────────────────────────
      transitionDuration: {
        DEFAULT: '150ms',
        fast:    '100ms',
        base:    '150ms',
        slow:    '300ms',
      },

      // ── Animations ───────────────────────────────────────────────────────
      keyframes: {
        fadeInUp: {
          from: { opacity: '0', transform: 'translateY(12px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        slideInRight: {
          from: { opacity: '0', transform: 'translateX(12px)' },
          to:   { opacity: '1', transform: 'translateX(0)' },
        },
        shimmer: {
          from: { backgroundPosition: '-200% 0' },
          to:   { backgroundPosition:  '200% 0' },
        },
        pulseRing: {
          '0%':   { boxShadow: '0 0 0 0 rgb(79 70 229 / 0.35)' },
          '70%':  { boxShadow: '0 0 0 8px rgb(79 70 229 / 0)' },
          '100%': { boxShadow: '0 0 0 0 rgb(79 70 229 / 0)' },
        },
        scaleIn: {
          from: { opacity: '0', transform: 'scale(0.96)' },
          to:   { opacity: '1', transform: 'scale(1)' },
        },
      },
      animation: {
        'fade-in-up':    'fadeInUp 0.35s ease both',
        'slide-in-right': 'slideInRight 0.3s ease both',
        'shimmer':       'shimmer 1.6s linear infinite',
        'pulse-ring':    'pulseRing 2.2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'scale-in':      'scaleIn 0.2s ease both',
      },
    },
  },

  plugins: [
    // Uncomment when @tailwindcss/forms is installed:
    // require('@tailwindcss/forms'),
  ],
}
