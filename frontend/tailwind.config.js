/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],

  theme: {
    extend: {

      // ══════════════════════════════════════════════════════════════════════
      // TYPOGRAPHY — M3 Type Scale
      // Roboto is the M3 reference, Inter is the acceptable system substitute.
      // ══════════════════════════════════════════════════════════════════════
      fontFamily: {
        sans: ['Inter', 'Roboto', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Roboto Mono', 'ui-monospace', 'monospace'],
      },

      // M3 Type Scale — sizes match the spec exactly (sp → rem at 16px root)
      fontSize: {
        // Display
        'display-lg': ['3.5625rem',  { lineHeight: '4rem',    letterSpacing: '-0.016em', fontWeight: '400' }],  // 57sp
        'display-md': ['2.8125rem',  { lineHeight: '3.25rem', letterSpacing: '0',        fontWeight: '400' }],  // 45sp
        'display-sm': ['2.25rem',    { lineHeight: '2.75rem', letterSpacing: '0',        fontWeight: '400' }],  // 36sp
        // Headline
        'headline-lg': ['2rem',      { lineHeight: '2.5rem',  letterSpacing: '0',        fontWeight: '400' }],  // 32sp
        'headline-md': ['1.75rem',   { lineHeight: '2.25rem', letterSpacing: '0',        fontWeight: '400' }],  // 28sp
        'headline-sm': ['1.5rem',    { lineHeight: '2rem',    letterSpacing: '0',        fontWeight: '400' }],  // 24sp
        // Title
        'title-lg':    ['1.375rem',  { lineHeight: '1.75rem', letterSpacing: '0',        fontWeight: '500' }],  // 22sp
        'title-md':    ['1rem',      { lineHeight: '1.5rem',  letterSpacing: '0.009em',  fontWeight: '500' }],  // 16sp
        'title-sm':    ['0.875rem',  { lineHeight: '1.25rem', letterSpacing: '0.006em',  fontWeight: '500' }],  // 14sp
        // Body
        'body-lg':     ['1rem',      { lineHeight: '1.5rem',  letterSpacing: '0.031em',  fontWeight: '400' }],  // 16sp
        'body-md':     ['0.875rem',  { lineHeight: '1.25rem', letterSpacing: '0.016em',  fontWeight: '400' }],  // 14sp
        'body-sm':     ['0.75rem',   { lineHeight: '1rem',    letterSpacing: '0.025em',  fontWeight: '400' }],  // 12sp
        // Label
        'label-lg':    ['0.875rem',  { lineHeight: '1.25rem', letterSpacing: '0.006em',  fontWeight: '500' }],  // 14sp
        'label-md':    ['0.75rem',   { lineHeight: '1rem',    letterSpacing: '0.031em',  fontWeight: '500' }],  // 12sp
        'label-sm':    ['0.6875rem', { lineHeight: '1rem',    letterSpacing: '0.031em',  fontWeight: '500' }],  // 11sp
      },

      letterSpacing: {
        tight:    '-0.016em', // Display Large only
        normal:   '0em',
        wide:     '0.009em',  // Title Medium
        wider:    '0.016em',  // Body Large
        widest:   '0.031em',  // Body Medium, Label Medium/Small
        label:    '0.006em',  // Title Small, Label Large
      },

      // ══════════════════════════════════════════════════════════════════════
      // COLORS — M3 Tonal Palette System
      // Primary, Secondary, Tertiary, Error, Neutral, Neutral Variant
      // Each role has a container + on-container pair.
      // ══════════════════════════════════════════════════════════════════════
      colors: {
        // ── Primary (Indigo / Blue-Violet) ──────────────────────────────────
        primary: {
          DEFAULT:   '#4f46e5', // indigo-600 — Primary
          on:        '#ffffff', // On Primary
          container: '#e0e7ff', // indigo-100 — Primary Container
          'on-container': '#1e1b4b', // indigo-950 — On Primary Container
          hover:     '#4338ca', // indigo-700
          pressed:   '#3730a3', // indigo-800
          focus:     '#4f46e5',
        },

        // ── Secondary (Violet) ───────────────────────────────────────────────
        secondary: {
          DEFAULT:   '#7c3aed', // violet-600
          on:        '#ffffff',
          container: '#ede9fe', // violet-100
          'on-container': '#2e1065', // violet-950
          hover:     '#6d28d9',
        },

        // ── Tertiary (Sky/Teal) ──────────────────────────────────────────────
        tertiary: {
          DEFAULT:   '#0284c7', // sky-600
          on:        '#ffffff',
          container: '#e0f2fe', // sky-100
          'on-container': '#0c4a6e', // sky-900
          hover:     '#0369a1',
        },

        // ── Semantic: Earned / Approved ────────────────────────────────────
        earned: {
          DEFAULT:   '#059669', // emerald-600
          on:        '#ffffff',
          container: '#d1fae5', // emerald-100
          'on-container': '#064e3b', // emerald-900
        },

        // ── Semantic: Staked / Pending ─────────────────────────────────────
        staked: {
          DEFAULT:   '#d97706', // amber-600
          on:        '#ffffff',
          container: '#fef3c7', // amber-100
          'on-container': '#78350f', // amber-900
        },

        // ── Error / Flagged / Rejected ─────────────────────────────────────
        error: {
          DEFAULT:   '#b91c1c', // red-700
          on:        '#ffffff',
          container: '#fee2e2', // red-100
          'on-container': '#7f1d1d', // red-900
        },

        // ── Neutral (Surfaces) ─────────────────────────────────────────────
        // M3 neutral = slightly tinted grays derived from the primary hue
        surface: {
          DEFAULT:      '#f8f7ff', // App shell — slightly warm/violet-tinted white
          dim:          '#dcd8f8', // Dimmed surface (modal backdrop)
          bright:       '#ffffff', // Fully bright surface
          container: {
            lowest:     '#ffffff', // Highest elevation cards
            low:        '#f3f2fb', // Nav, sidebars
            DEFAULT:    '#eeedf5', // Standard card surface
            high:       '#e8e7ef', // Slightly elevated sections
            highest:    '#e2e1ea', // Most elevated within page
          },
        },

        // On-surface (text on surface backgrounds)
        'on-surface': {
          DEFAULT:  '#1c1b20', // slate-900 equivalent — primary heading text
          variant:  '#47464f', // slate-600 equivalent — secondary text
        },

        // ── Outline ────────────────────────────────────────────────────────
        outline: {
          DEFAULT: '#787680', // M3 outline — neutral dividers, input borders
          variant: '#cac4d0', // Softer dividers
        },
      },

      // ══════════════════════════════════════════════════════════════════════
      // SHAPES — M3 Shape Scale
      // None 0px | Extra Small 4px | Small 8px | Medium 12px |
      // Large 16px | Extra Large 28px | Full 9999px
      // ══════════════════════════════════════════════════════════════════════
      borderRadius: {
        'none':  '0px',
        'xs':    '4px',    // Extra Small — menus, tooltips
        'sm':    '8px',    // Small — chips, text fields (outlined top)
        'md':    '12px',   // Medium — cards, dialogs
        'lg':    '16px',   // Large — navigation drawers, side sheets
        'xl':    '28px',   // Extra Large — floating action buttons, large cards
        '2xl':   '28px',   // mapped — use xl or 2xl interchangeably
        '3xl':   '28px',   // same
        'full':  '9999px', // Full — FAB, pill buttons, chips
      },

      // ══════════════════════════════════════════════════════════════════════
      // ELEVATION — M3 Shadow tokens + Tonal Surface Overlay
      // Shadows should be subtle. The real M3 elevation cue is surface tint.
      // ══════════════════════════════════════════════════════════════════════
      boxShadow: {
        // M3 Elevation Level 0 — Flat, no shadow
        'elev-0': 'none',
        // M3 Elevation Level 1 — Cards at rest
        'elev-1': '0 1px 2px 0 rgb(0 0 0 / 0.08), 0 1px 3px 1px rgb(0 0 0 / 0.06)',
        // M3 Elevation Level 2 — Navigation, floating elements
        'elev-2': '0 1px 2px 0 rgb(0 0 0 / 0.1),  0 2px 6px 2px rgb(0 0 0 / 0.08)',
        // M3 Elevation Level 3 — FABs, dialogs
        'elev-3': '0 4px 8px 3px rgb(0 0 0 / 0.1), 0 1px 3px 0 rgb(0 0 0 / 0.1)',
        // M3 Elevation Level 4 — Navigation bar
        'elev-4': '0 6px 10px 4px rgb(0 0 0 / 0.1), 0 2px 3px 0 rgb(0 0 0 / 0.1)',
        // M3 Elevation Level 5 — Top app bar (scrolled)
        'elev-5': '0 8px 12px 6px rgb(0 0 0 / 0.1), 0 4px 4px 0 rgb(0 0 0 / 0.1)',

        // Focus ring (accessible, matches primary)
        'focus-ring': '0 0 0 3px rgb(79 70 229 / 0.4)',

        // Backward compat with Tailwind utilities
        sm:  '0 1px 2px 0 rgb(0 0 0 / 0.08), 0 1px 3px 1px rgb(0 0 0 / 0.06)',
        md:  '0 1px 2px 0 rgb(0 0 0 / 0.1),  0 2px 6px 2px rgb(0 0 0 / 0.08)',
        lg:  '0 4px 8px 3px rgb(0 0 0 / 0.1), 0 1px 3px 0 rgb(0 0 0 / 0.1)',
      },

      // ══════════════════════════════════════════════════════════════════════
      // MOTION — M3 uses Emphasized and Standard easing
      // ══════════════════════════════════════════════════════════════════════
      transitionTimingFunction: {
        // M3 Standard — default for most transitions
        'm3-standard':    'cubic-bezier(0.2, 0, 0, 1)',
        // M3 Standard Decelerate — elements entering
        'm3-decelerate':  'cubic-bezier(0, 0, 0, 1)',
        // M3 Standard Accelerate — elements exiting
        'm3-accelerate':  'cubic-bezier(0.3, 0, 1, 1)',
        // M3 Emphasized — expressive entrances
        'm3-emphasized':  'cubic-bezier(0.2, 0, 0, 1)',
      },

      transitionDuration: {
        'short-1':  '50ms',   // Fade in/out, icon appearance
        'short-2':  '100ms',
        'short-3':  '150ms',  // Color changes, state layers
        'short-4':  '200ms',  // Default — buttons, chips, toggles
        'medium-1': '250ms',
        'medium-2': '300ms',  // Cards, menus
        'medium-3': '350ms',
        'medium-4': '400ms',  // FAB, nav bar
        'long-1':   '450ms',
        'long-2':   '500ms',  // Complex transitions
      },

      // ══════════════════════════════════════════════════════════════════════
      // ANIMATIONS
      // ══════════════════════════════════════════════════════════════════════
      keyframes: {
        // Fade in + slide up (entering content)
        fadeInUp: {
          from: { opacity: '0', transform: 'translateY(16px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        // Scale in (dialogs, FABs)
        scaleIn: {
          from: { opacity: '0', transform: 'scale(0.92)' },
          to:   { opacity: '1', transform: 'scale(1)' },
        },
        // Slide in from right (navigation drawers)
        slideInRight: {
          from: { opacity: '0', transform: 'translateX(20px)' },
          to:   { opacity: '1', transform: 'translateX(0)' },
        },
        // Skeleton shimmer
        shimmer: {
          from: { backgroundPosition: '-200% 0' },
          to:   { backgroundPosition:  '200% 0' },
        },
        // M3 ripple (state layer)
        ripple: {
          from: { transform: 'scale(0)', opacity: '0.24' },
          to:   { transform: 'scale(2)', opacity: '0' },
        },
        // Progress bar indeterminate
        progressIndeterminate: {
          '0%':   { left: '-35%',  right: '100%' },
          '60%':  { left: '100%',  right: '-90%' },
          '100%': { left: '100%',  right: '-90%' },
        },
      },
      animation: {
        'fade-in-up':    'fadeInUp 300ms cubic-bezier(0.2, 0, 0, 1) both',
        'scale-in':      'scaleIn 200ms cubic-bezier(0.2, 0, 0, 1) both',
        'slide-in-right':'slideInRight 300ms cubic-bezier(0, 0, 0, 1) both',
        'shimmer':       'shimmer 1.6s linear infinite',
        'ripple':        'ripple 600ms linear',
        'progress-ind':  'progressIndeterminate 2.1s cubic-bezier(0.65, 0.815, 0.735, 0.395) infinite',
      },

      // Spacing
      spacing: {
        18: '4.5rem',
        22: '5.5rem',
        112: '28rem',
        128: '32rem',
      },
    },
  },

  plugins: [],
}
