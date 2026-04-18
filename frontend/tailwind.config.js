/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],

  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },

      colors: {
        // Brand — Indigo
        brand: {
          50:  '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          500: '#6366f1',
          600: '#4f46e5',   // PRIMARY ACTION
          700: '#4338ca',   // HOVER
          800: '#3730a3',
          900: '#312e81',
        },
        // Semantic — Earned/Active
        earned: {
          50:  '#ecfdf5',
          100: '#d1fae5',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
        },
        // Semantic — Staked/Pending
        staked: {
          50:  '#fffbeb',
          500: '#f59e0b',
          600: '#d97706',
        },
        // Semantic — Error/Flagged
        flagged: {
          50:  '#fff1f2',
          500: '#f43f5e',
          600: '#e11d48',
        },
        // Neutral (slate-950 not in Tailwind v3 by default)
        slate: { 950: '#020617' },
      },

      borderRadius: {
        'xl':  '0.75rem',   // 12px — cards
        '2xl': '1rem',      // 16px — hero cards
        '3xl': '1.5rem',    // 24px — modal
        'full': '9999px',   // buttons, pills
      },

      boxShadow: {
        card:    '0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px -1px rgb(0 0 0 / 0.04)',
        'card-hover': '0 4px 12px -2px rgb(0 0 0 / 0.08), 0 2px 4px -2px rgb(0 0 0 / 0.05)',
        'focus-brand': '0 0 0 3px rgb(79 70 229 / 0.2)',
        sm: '0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px -1px rgb(0 0 0 / 0.04)',
        md: '0 4px 12px -2px rgb(0 0 0 / 0.08), 0 2px 4px -2px rgb(0 0 0 / 0.05)',
      },

      letterSpacing: {
        tightest: '-0.04em',
        tight:    '-0.025em',
        normal:   '0',
        widest:   '0.1em',
      },

      keyframes: {
        fadeInUp: {
          from: { opacity: '0', transform: 'translateY(12px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          from: { opacity: '0', transform: 'scale(0.96)' },
          to:   { opacity: '1', transform: 'scale(1)' },
        },
        shimmer: {
          from: { backgroundPosition: '-200% 0' },
          to:   { backgroundPosition:  '200% 0' },
        },
        pulseGlow: {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '0.6' },
        },
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.35s cubic-bezier(0.2, 0, 0, 1) both',
        'scale-in':   'scaleIn 0.2s cubic-bezier(0.2, 0, 0, 1) both',
        'shimmer':    'shimmer 1.6s linear infinite',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
      },

      spacing: {
        18: '4.5rem',
        22: '5.5rem',
      },
    },
  },

  plugins: [],
}
