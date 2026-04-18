# Compute Commons · Design System

**Theme:** High-Trust Premium SaaS — Stripe × Linear × Vercel  
**Mode:** Light-first. Pure white cards on a slate-50 shell.  
**Goal:** Aspirational for expert contributors. Rigorously professional for enterprise AI buyers.

---

## 1 · Color Palette

### Backgrounds
| Token | Value | Tailwind | Use |
|---|---|---|---|
| App shell | `#f8fafc` | `bg-slate-50` | Page background, sidebars |
| Card surface | `#ffffff` | `bg-white` | Cards, modals, dropdowns |
| Subtle fill | `#f1f5f9` | `bg-slate-100` | Table rows, input bg, inner panels |

### Text
| Role | Tailwind | Use |
|---|---|---|
| Primary heading | `text-slate-900` | H1, H2, H3 — always `tracking-tight` |
| Body / secondary | `text-slate-600` | Paragraphs, descriptions |
| Muted | `text-slate-400` | Placeholders, hints, timestamps |
| Disabled | `text-slate-300` | Disabled states |

### Brand (Indigo)
| State | Tailwind | CSS var |
|---|---|---|
| Default | `bg-indigo-600` / `text-indigo-600` | `--cc-brand` |
| Hover | `bg-indigo-700` | `--cc-brand-hover` |
| Tinted bg | `bg-indigo-50` / `text-indigo-700` | `--cc-brand-light` |
| Focus ring | `ring-indigo-500` | `--cc-brand-ring` |

### Semantic Colors
| Meaning | Tailwind | CSS var | Use |
|---|---|---|---|
| **Earned / Approved** | `text-emerald-600` + `bg-emerald-50` | `--cc-earned` | Credits, complete status, trust score |
| **Staked / Pending** | `text-amber-600` + `bg-amber-50` | `--cc-staked` | Pending review, staked credits |
| **Flagged / Rejected** | `text-rose-600` + `bg-rose-50` | `--cc-flagged` | Error states, abuse flags, rejections |

> **Rule:** Never use raw colors on text. Always pair `text-{semantic}-600` with `bg-{semantic}-50` for badges. Use `text-{semantic}-700` on colored backgrounds.

---

## 2 · Typography

**Font stack:**
- Sans: `Inter` → `system-ui` → `-apple-system`
- Mono: `JetBrains Mono` → `Fira Code` → `ui-monospace`

### Scale
| Class | Size | Weight | Use |
|---|---|---|---|
| `text-4xl font-bold tracking-tightest` | 36px | 700 | Page heroes, stat callouts |
| `text-2xl font-semibold tracking-tight` | 24px | 600 | H2 section titles |
| `text-xl font-semibold tracking-tight` | 20px | 600 | Card titles, pane headers |
| `text-lg font-semibold` | 18px | 600 | H3 subsections |
| `text-sm` | 14px | 400 | Body copy, table cells |
| `text-xs font-semibold uppercase tracking-widest` | 12px | 600 | Section labels, column headers |
| `text-2xs` (custom) | 10.4px | — | Fine print, supplemental hints |

### Rules
- Apply `tracking-tight` (`-0.025em`) to **all** H1–H3 headings.
- Apply `tabular-nums` to all financial numbers and scores for alignment.
- Use `font-mono` for AI prompts, scores, IDs, and credit amounts.
- Use `text-balance` on marketing/hero headlines for clean line breaks.

---

## 3 · Spacing

**Philosophy:** Let data breathe. Dense where needed, relaxed in presentation.

| Context | Padding | Gap |
|---|---|---|
| Standard card | `p-6` | `gap-4` between content sections |
| Hero / stat card | `p-8` | `gap-6` |
| Dense list row | `px-4 py-3` | — |
| Form fields | `px-3 py-2` | `gap-3` between fields |
| Sidebar nav | `px-3 py-2` per item | `gap-1` between items |
| Page layout sections | — | `gap-6` |

---

## 4 · Component DNA

### Cards
```tsx
// Standard card
<div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">

// Or use the CSS class:
<div className="cc-card">

// Interactive — lifts on hover
<div className="cc-card cc-card-hover">

// Hero / stat card (has indigo top stripe)
<div className="cc-card-hero">
```

**Rules:**
- Border: `border-slate-200` — never darker unless active/focused
- Shadow: `shadow-sm` only — never heavier
- Radius: `rounded-xl` (14px) standard, `rounded-2xl` for hero sections

---

### Buttons
```tsx
// Primary — brand action
<button className="cc-btn-primary">Request Intro</button>

// Tailwind compose (equivalent):
<button className="bg-indigo-600 text-white font-medium text-sm rounded-lg
                   px-4 py-2 shadow-sm border border-indigo-600
                   hover:bg-indigo-700 transition-colors">

// Secondary
<button className="cc-btn-secondary">Cancel</button>

// Tailwind compose:
<button className="bg-white text-slate-700 border border-slate-300 font-medium
                   text-sm rounded-lg px-4 py-2 hover:bg-slate-50
                   transition-colors shadow-sm">

// Destructive
<button className="cc-btn-danger">Remove</button>

// Confirmed state (after "Request Intro")
<button className="bg-emerald-50 text-emerald-700 border border-emerald-200
                   rounded-lg px-4 py-2 font-medium text-sm cursor-default
                   inline-flex items-center gap-2">
  <CheckCircle2 className="w-4 h-4" /> Intro Requested
</button>
```

---

### Badges & Status Pills
```tsx
// Tier badges
<span className="cc-badge-contributor">Contributor</span>
<span className="cc-badge-validator">Validator</span>
<span className="cc-badge-expert">Expert</span>
<span className="cc-badge-partner">Partner</span>

// Status pills
<span className="cc-status-pending">Pending</span>
<span className="cc-status-complete">Complete</span>
<span className="cc-status-validating">Validating</span>
<span className="cc-status-flagged">Flagged</span>
<span className="cc-status-rejected">Rejected</span>

// Domain / taxonomy tags
<span className="cc-tag">law_legal</span>
```

**Pill anatomy:**
`bg-{color}-50 text-{color}-700 border border-{color}-200 rounded-full px-2.5 py-0.5 text-xs font-semibold`

---

### Data Tables
```tsx
<table className="cc-table">
  <thead>
    <tr>
      <th>Candidate</th>
      <th>Score</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Expert_042</td>
      <td>94%</td>
    </tr>
  </tbody>
</table>
```
**Rules:**
- No vertical dividers — horizontal `border-b border-slate-100` only
- `hover:bg-slate-50` on tbody rows for interactivity
- Column headers: `text-[11px] font-semibold text-slate-400 uppercase tracking-widest`

---

### Form Inputs
```tsx
<label className="cc-label">Search</label>
<input className="cc-input" placeholder="Search ID or domain…" />
<select className="cc-select">…</select>
```

Focus state: `border-indigo-500` + `box-shadow: 0 0 0 3px rgb(79 70 229 / 0.18)`

---

### Numeric Displays
```tsx
// Credit balance (large, emerald)
<span className="cc-num-xl cc-num-earned tabular-nums">1,420</span>

// Trust score (brand)
<span className="cc-num-lg cc-num-brand">88.4</span>

// Inline stat
<span className="cc-num-md tabular-nums">627 pts</span>
```

---

### Progress Bars
```tsx
<div className="cc-progress-track">
  <div className="cc-progress-fill bg-indigo-500" style={{ width: '74%' }} />
</div>

// Gradient brand fill
<div className="cc-progress-track">
  <div className="cc-progress-fill cc-progress-fill-brand" style={{ width: '68%' }} />
</div>
```

---

## 5 · Surface Contexts

Apply `data-surface="..."` to `<main>` or a wrapper `<div>`:

| Value | Where | Override |
|---|---|---|
| `contributor` | Contributor Dashboard | Accent → emerald, progress fill → emerald |
| `partner` | Partner Workspace | bg-slate-50 shell, brand accent, dense type |
| `profile` | Public Profile pages | bg-white, 17px base font, relaxed leading |

```tsx
<main data-surface="partner">
  {/* Dense monospace evidence data, indigo accent */}
</main>
```

---

## 6 · Surface-Specific Vibes

### Contributor Dashboard
> **Vibe:** Reward & Progression. Make contributions feel valuable.

- Credit balance: `cc-num-xl cc-num-earned` — large, emerald, always visible
- Trust score: `cc-score-ring` or circular SVG with indigo ring
- Tier badge: `cc-badge-{tier}` in header, always present
- Progress bars: `cc-progress-fill-brand`, animated on mount
- Acted-on: `cc-status-complete` pill + `Zap` icon
- Stats: `cc-card-hero` for highlights, `cc-card` for activity lists

### Partner Workspace
> **Vibe:** Data & Rigor. VPs need density without decoration.

- Fixed split pane: `bg-slate-50` left, `bg-white` right
- Evidence prose: `text-sm text-slate-700 leading-relaxed`
- AI payload evidence: `cc-code-block` (monospace, slate-50 bg)
- JSON toggle: `bg-slate-50` pre-block, muted syntax (no terminal neon)
- Work sample cards: `cc-card cc-card-hover`
- Vulnerability block: `bg-red-50 border border-red-100 rounded-lg p-4`
- Ground truth block: `bg-emerald-50 border border-emerald-100 rounded-lg p-4`

### Public Profiles
> **Vibe:** Authority. This is an expert's portfolio.

- `data-surface="profile"` gives bg-white and 17px base font
- Hero: full-width header, `cc-card-hero`, handle + tier badge + trust score ring
- Work samples: `cc-card cc-card-hover p-8`
- Section labels: `text-2xl font-semibold tracking-tight`
- Peer consensus: `cc-num-lg cc-num-brand` for the verified count

---

## 7 · Animation

```tsx
// Entrances
<div className="animate-fade-in-up">...</div>
<div className="animate-slide-in-right">...</div>
<div className="animate-scale-in">...</div>

// Stagger list children
<div className="animate-fade-in-up stagger-1">First item</div>
<div className="animate-fade-in-up stagger-2">Second item</div>
<div className="animate-fade-in-up stagger-3">Third item</div>

// Skeleton loaders
<div className="cc-skeleton h-4 w-32 rounded mb-2" />
<div className="cc-skeleton h-4 w-24 rounded" />

// Pulse ring on primary CTA
<button className="cc-btn-primary animate-pulse-ring">
  Request Secure Intro
</button>
```

---

## 8 · Quick Reference

```
─── BACKGROUNDS ──────────────────────────────────────────────────
bg-white         Cards, modals, main content
bg-slate-50      App shell, sidebars, pane backgrounds
bg-slate-100     Table rows, input fills, nested panels

─── BORDERS ──────────────────────────────────────────────────────
border-slate-200   Default — never darker unless active
border-slate-300   Strong — inputs on focus-adjacent

─── TEXT ─────────────────────────────────────────────────────────
text-slate-900   Primary headings
text-slate-600   Body copy, secondary
text-slate-400   Muted / placeholder

─── BRAND ────────────────────────────────────────────────────────
indigo-600       Primary action
indigo-700       Hover
indigo-50        Tinted background (active rows, tags)

─── SEMANTIC ─────────────────────────────────────────────────────
emerald-600 / emerald-50    Earned / approved
amber-600   / amber-50      Staked / pending
rose-600    / rose-50       Flagged / rejected

─── COMPONENT SHORTCUTS ──────────────────────────────────────────
cc-card              bg-white rounded-xl border-slate-200 shadow-sm p-6
cc-card-hover        lifts shadow + darkens border on :hover
cc-card-hero         + accent top stripe
cc-btn-primary       bg-indigo-600 text-white rounded-lg px-4 py-2
cc-btn-secondary     bg-white text-slate-700 border-slate-300
cc-badge-{tier}      pastel pill for contributor/validator/expert/partner
cc-status-{state}    pastel pill for pending/complete/validating/flagged
cc-tag               slate-100 neutral domain tag
cc-input / cc-select form inputs with indigo focus ring
cc-table             clean rows, no vertical lines, hover:bg-slate-50
cc-num-xl/lg/md      mono numeric displays
cc-score-ring        circular trust score display
cc-progress-track    full-width 6px track
cc-code-block        slate-50 mono evidence block
cc-section-label     11px uppercase tracking-widest text-slate-400
cc-nav-link          sidebar nav, .active = indigo-50 bg
cc-skeleton          shimmer loading placeholder

─── TYPOGRAPHY ───────────────────────────────────────────────────
All H1–H3: tracking-tight (-0.025em)
Scores/IDs: font-mono tabular-nums
Section labels: uppercase tracking-widest text-[11px]
Hero counts: font-mono font-bold text-4xl

─── SHADOWS ──────────────────────────────────────────────────────
shadow-sm    Card default — never heavier
shadow-md    Card hover only

─── NEVER ────────────────────────────────────────────────────────
- No shadow-lg or shadow-xl on cards
- No bg-slate-900 / bg-slate-950 (dark styles only in code blocks)
- No raw color text without semantic pairing (e.g. no bare text-red-500)
- No border-slate-800 or darker borders on light surfaces
```

---

> **Files:** `tailwind.config.js` · `src/app/globals.css` · this doc (`design-system.md`)
> **Last updated:** April 2026
