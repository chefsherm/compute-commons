# Compute Commons · Material Design 3 Design System

**Theme:** Material Design 3 — Tonal Palettes · Elevation · State Layers · M3 Type Scale  
**Context:** Expert AI talent network and evaluation platform  
**Aesthetic goal:** Aspirational for contributors, rigorously professional for enterprise AI buyers

> **Files:**
> - `tailwind.config.js` — tokens registered as Tailwind utilities
> - `src/app/globals.css` — CSS variables + `@layer components` primitives
> - This document — canonical reference for all future component work

---

## 1 · The M3 Color System

M3 uses **color roles** — not raw hex values. Every color has an **on-** counterpart for text rendered on top of it, and a **container** pair for softer usage.

### Primary Role (Indigo — Brand/Action)
| Role | CSS var | Hex | Use |
|---|---|---|---|
| Primary | `--md-primary` | `#4f46e5` | Filled buttons, active states, key highlights |
| On Primary | `--md-on-primary` | `#ffffff` | Text/icons inside Primary-colored elements |
| Primary Container | `--md-primary-container` | `#e0e7ff` | Chips, tinted card surfaces, selected state bg |
| On Primary Container | `--md-on-primary-container` | `#1e1b4b` | Text inside Primary Container |

### Secondary Role (Violet — Supporting)
| Role | CSS var | Hex | Use |
|---|---|---|---|
| Secondary | `--md-secondary` | `#7c3aed` | FABs, secondary emphasis |
| Secondary Container | `--md-secondary-container` | `#ede9fe` | Active nav items, tonal buttons |
| On Secondary Container | `--md-on-secondary-container` | `#2e1065` | Text inside Secondary Container |

### Tertiary Role (Sky — Accent)
| Role | CSS var | Hex | Use |
|---|---|---|---|
| Tertiary | `--md-tertiary` | `#0284c7` | Charts, progress, accent callouts |
| Tertiary Container | `--md-tertiary-container` | `#e0f2fe` | Soft highlight backgrounds |

### Semantic Roles
| Meaning | CSS var | Container var | Use |
|---|---|---|---|
| **Earned / Approved** | `--md-earned` `#059669` | `--md-earned-container` `#d1fae5` | Credits, complete status |
| **Staked / Pending** | `--md-staked` `#d97706` | `--md-staked-container` `#fef3c7` | Pending review, staked amounts |
| **Error / Flagged** | `--md-error` `#b91c1c` | `--md-error-container` `#fee2e2` | Rejected, abused, flagged |

### Surface Roles (Backgrounds)
M3 replaces plain `bg-white` + `bg-gray` with a **5-level container system**, all slightly tinted with the primary hue.

| Level | CSS var | Alpha tint | Use |
|---|---|---|---|
| `surface` | `--md-surface` | — | App shell / page bg (`#f8f7ff`) |
| `surface-container-lowest` | `--md-surface-container-lowest` | 0% | Cards at highest elevation |
| `surface-container-low` | `--md-surface-container-low` | 5% | Sidebars, navs, resting cards |
| `surface-container` | `--md-surface-container` | 8% | Standard card surface |
| `surface-container-high` | `--md-surface-container-high` | 11% | Filled inputs bg, elevated sections |
| `surface-container-highest` | `--md-surface-container-highest` | 14% | Overlapping panels, tooltips |

### On-Surface (Text)
| Role | CSS var | Hex | Use |
|---|---|---|---|
| On Surface | `--md-on-surface` | `#1c1b20` | All headings and primary body text |
| On Surface Variant | `--md-on-surface-variant` | `#47464f` | Secondary text, placeholder, hints |

### Outline
| Role | CSS var | Hex | Use |
|---|---|---|---|
| Outline | `--md-outline` | `#787680` | Input borders (unfocused), dividers |
| Outline Variant | `--md-outline-variant` | `#cac4d0` | Subtle dividers, inactive chip borders |

> **Rule:** NEVER use raw Tailwind colors like `text-gray-600` directly. Always reference the role. Compose using CSS variables or the semantic classes below.

---

## 2 · M3 Elevation

M3 elevation has **two mechanisms** — shadow + primary-tinted surface overlay. Both must be applied together.

| Level | Shadow token | Tint level | Component examples |
|---|---|---|---|
| 0 | `shadow-elev-0` / none | 0% | Flat surfaces, text buttons |
| 1 | `shadow-elev-1` / `shadow-sm` | 5% | Cards at rest, search bars |
| 2 | `shadow-elev-2` / `shadow-md` | 8% | Nav drawers, floating elements |
| 3 | `shadow-elev-3` / `shadow-lg` | 11% | FABs, dialogs, modals |
| 4 | `shadow-elev-4` | 12% | Navigation bar (scrolled) |
| 5 | `shadow-elev-5` | 14% | Top app bar (scrolled) |

**Applying tint + shadow in Tailwind:**
```tsx
// Level 1 card (rest state)
<div className="shadow-elev-1 bg-surface-container-low rounded-md">

// Level 2 (on hover or navigation)
<div className="shadow-elev-2 bg-surface-container rounded-md">
```

**Using the CSS component class (recommended):**
```tsx
// Handles both shadow AND correct surface tint
<div className="md-card">...</div>
<div className="md-card-xl">...</div>   // Extra Large shape, Level 2
```

---

## 3 · M3 Shape Scale

M3 uses named shape tokens — not arbitrary `rounded-*` values.

| M3 Token | Radius | Tailwind | Use |
|---|---|---|---|
| Extra Small | 4px | `rounded-xs` | Menus, tooltips, snackbars |
| Small | 8px | `rounded-sm` | Chips, text field corners |
| Medium | 12px | `rounded-md` | Cards, dialogs |
| Large | 16px | `rounded-lg` | Navigation drawers, side sheets |
| Extra Large | 28px | `rounded-xl` | Large FABs, prominent cards |
| Full | 9999px | `rounded-full` | **All buttons**, pills, FABs, chips |

> **Rule:** Buttons ALWAYS use `rounded-full`. Cards use `rounded-md` (12px) or `rounded-xl` (28px) for hero/xl cards. NEVER use `rounded-xl` on buttons.

---

## 4 · M3 Typography Scale

Inter (or Roboto) is the platform font. All sizes mapped to M3 spec in `tailwind.config.js`.

| Role | Class | Size | Weight | Use |
|---|---|---|---|---|
| Display Large | `text-display-lg` | 57sp / 3.56rem | 400 | Marketing heroes (rare) |
| Display Medium | `text-display-md` | 45sp / 2.81rem | 400 | Page-level stat callouts |
| Display Small | `text-display-sm` | 36sp / 2.25rem | 400 | Section hero numbers |
| Headline Large | `text-headline-lg` | 32sp / 2rem | 400 | Page titles (H2) |
| Headline Medium | `text-headline-md` | 28sp / 1.75rem | 400 | Section headings |
| Headline Small | `text-headline-sm` | 24sp / 1.5rem | 400 | Card titles (H3) |
| Title Large | `text-title-lg` | 22sp / 1.375rem | 500 | Pane headers, dialog titles |
| Title Medium | `text-title-md` | 16sp / 1rem | 500 | Prominent labels |
| Title Small | `text-title-sm` | 14sp / 0.875rem | 500 | Column headers |
| Body Large | `text-body-lg` | 16sp / 1rem | 400 | Default body text |
| Body Medium | `text-body-md` | 14sp / 0.875rem | 400 | Table cells, secondary body |
| Body Small | `text-body-sm` | 12sp / 0.75rem | 400 | Captions, fine print |
| Label Large | `text-label-lg` | 14sp / 0.875rem | 500 | **Button text**, prominent labels |
| Label Medium | `text-label-md` | 12sp / 0.75rem | 500 | **Chip text**, overlines, nav labels |
| Label Small | `text-label-sm` | 11sp / 0.6875rem | 500 | Badge text, annotation |

> **Rules:**
> - Button text → always `text-label-lg font-medium`
> - Table column headers → `text-label-md font-medium uppercase`
> - Section labels → `cc-section-label` class (Label Small, uppercase, On Surface Variant)
> - Monospace numbers → `font-mono tabular-nums` on top of scale class

---

## 5 · State Layers

M3 interaction states are an **overlay of the "on-" color** at a defined opacity — NOT background-color changes of the component itself. This is enforced via `::before` pseudo-elements in all interactive components.

| State | Opacity | Elements |
|---|---|---|
| Hover | 8% (`0.08`) | All interactive surfaces |
| Focus | 12% (`0.12`) | All interactive surfaces |
| Pressed | 12% (`0.12`) | Buttons, chips, rows |
| Dragged | 16% (`0.16`) | Draggable list items |
| Disabled (content) | 38% (`0.38`) | Text, icons in disabled els |
| Disabled (container) | 12% (`0.12`) | Background of disabled el |

**All interactive components must use M3 state layers.** The CSS classes below implement this automatically via `::before`.

---

## 6 · Component Primitives

### Surfaces / Cards
```tsx
// Elevation 1 — standard card at rest (shadow + tinted surface)
<div className="md-card p-6">...</div>

// Interactive card — adds state layer on hover/press + elevates
<div className="md-card-interactive p-6">...</div>

// Extra Large shape — hero/feature cards
<div className="md-card-xl p-8">...</div>

// Tonal card — primary-tinted for stat highlights
<div className="md-card-tonal p-6">...</div>
```

### Buttons (all use `rounded-full`)
```tsx
// Filled — highest emphasis, primary action
<button className="md-btn-filled">Request Secure Intro</button>

// Filled Tonal — secondary emphasis (secondary-container bg)
<button className="md-btn-tonal">Save Draft</button>

// Elevated — above-surface, shadow at rest
<button className="md-btn-elevated">Export</button>

// Outlined — medium emphasis, border only
<button className="md-btn-outlined">Cancel</button>

// Text — lowest emphasis, no bg or border
<button className="md-btn-text">Learn More</button>

// Error / Destructive
<button className="md-btn-error">Remove Expert</button>

// Icon button
<button className="md-btn-icon"><Trash2 className="w-5 h-5" /></button>
```

### Badges / Chips
```tsx
// Tier badges
<span className="cc-badge cc-badge-contributor">Contributor</span>
<span className="cc-badge cc-badge-validator">Validator</span>
<span className="cc-badge cc-badge-expert">Expert</span>
<span className="cc-badge cc-badge-partner">Partner</span>

// Status chips
<span className="cc-status cc-status-pending">Pending</span>
<span className="cc-status cc-status-complete">Complete</span>
<span className="cc-status cc-status-validating">Validating</span>
<span className="cc-status cc-status-flagged">Flagged</span>

// Interactive M3 chip (with state layer)
<button className="md-chip">law_legal</button>
<button className="md-chip selected">biomedical</button>

// Domain tag (static)
<span className="cc-tag">clinical_eval</span>
```

### Text Fields
```tsx
// Filled (M3 standard — flat bottom border, colored bg)
<input className="md-input-filled" placeholder="Search experts…" />

// Outlined (M3 standard — full border, transparent bg)
<input className="md-input-outlined" placeholder="Search experts…" />

// Compute Commons shorthand (outlined + 8px radius)
<input className="cc-input" placeholder="Search ID or domain…" />
<select className="cc-select">…</select>
```

### Tables
```tsx
<table className="md-table w-full">
  <thead>
    <tr>
      <th>Candidate ID</th>
      <th>Domain</th>
      <th>Score</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Expert_042</td>
      <td className="text-body-md">Law & Legal</td>
      <td className="font-mono tabular-nums">94%</td>
    </tr>
  </tbody>
</table>
```
State layer on rows handled automatically via `::after` pseudo.

### Navigation
```tsx
<nav>
  <a href="/dashboard" className="md-nav-item active">
    <LayoutDashboard className="w-5 h-5" />
    Dashboard
  </a>
  <a href="/workspace" className="md-nav-item">
    <Terminal className="w-5 h-5" />
    Partner Workspace
  </a>
</nav>
```

### Numerics
```tsx
// Large stat — credit balance
<span className="cc-num-xl cc-num-earned tabular-nums">1,420</span>

// Medium stat — trust score
<span className="cc-num-lg cc-num-primary">88.4</span>

// Inline — card metric
<span className="cc-num-md tabular-nums">627 pts</span>
```

### Progress
```tsx
// Determinate
<div className="md-progress-track">
  <div className="md-progress-fill" style={{ width: '74%' }} />
</div>

// Earned variant
<div className="md-progress-track">
  <div className="md-progress-fill earned" style={{ width: '91%' }} />
</div>
```

### Skeleton Loaders
```tsx
<div className="md-skeleton h-4 w-32 rounded-xs mb-2" />
<div className="md-skeleton h-4 w-24 rounded-xs" />
```

### Score Ring
```tsx
<div className="cc-score-ring">88.4</div>
<div className="cc-score-ring earned">91%</div>
```

### Dividers
```tsx
<hr className="md-divider" />          // Full bleed
<hr className="md-divider-inset" />    // Inset (icon-list style)
```

### Code Blocks (Partner Workspace)
```tsx
<pre className="cc-code-block max-h-72">
  {JSON.stringify(payload, null, 2)}
</pre>
```

---

## 7 · Surface Contexts

Apply `data-surface` to `<main>` or a containing `<div>` to shift the color role tokens for that section:

| Value | Where | Effect |
|---|---|---|
| `contributor` | Contributor Dashboard | Rebases `--md-primary` to emerald (earned-forward). FABs, progress, score ring all go green. |
| `partner` | Partner Workspace | Darker surface shell (`#f3f2fb`), smaller default font for density. |
| `profile` | Public Profile | Pure white surface, slightly larger font, relaxed leading. |

```tsx
<main data-surface="contributor">
  {/* Score ring, FABs, progress bars all use emerald now */}
</main>

<main data-surface="partner">
  {/* Dense type, darker background */}
</main>
```

---

## 8 · Motion

M3 uses **Standard** (most transitions) and **Emphasized** (expressive entrances) easing.

| M3 Curve | CSS var | Tailwind class | Use |
|---|---|---|---|
| Standard | `cubic-bezier(0.2, 0, 0, 1)` | `ease-m3-standard` | State changes, color transitions |
| Decelerate | `cubic-bezier(0, 0, 0, 1)` | `ease-m3-decelerate` | Entering elements |
| Accelerate | `cubic-bezier(0.3, 0, 1, 1)` | `ease-m3-accelerate` | Exiting elements |

```tsx
// Standard entrance
<div className="animate-fade-in-up">...</div>

// Dialog / modal
<div className="animate-scale-in">...</div>

// Drawer / panel
<div className="animate-slide-in-right">...</div>

// Skeleton
<div className="md-skeleton h-5 w-40 rounded-xs" />

// Stagger list
<div className="animate-fade-in-up stagger-1">...</div>
<div className="animate-fade-in-up stagger-2">...</div>
<div className="animate-fade-in-up stagger-3">...</div>
```

**All interactive elements must use:**
```tsx
className="transition-all duration-short-4 ease-m3-standard"
// or the shorthand already built into md-btn, md-card-interactive, etc.
```

---

## 9 · M3 vs Previous System — Migration Notes

| Old class | M3 replacement | Notes |
|---|---|---|
| `bg-white` (cards) | `md-card` or `bg-surface-container-low` | Adds elevation + tint |
| `border border-slate-200` | ❌ Remove — use elevation instead | M3 doesn't use borders for separation |
| `rounded-xl` (buttons) | `rounded-full` | M3 buttons ALWAYS pill |
| `rounded-xl` (cards) | `rounded-md` (12px) or `rounded-xl` (28px) | Kept — maps to Large/Extra Large |
| `shadow-sm` | `shadow-elev-1` | Same shadow, but now has a name |
| `text-slate-900` | `text-on-surface` or `color: var(--md-on-surface)` | Use role not raw color |
| `text-slate-600` | `text-on-surface-variant` or `color: var(--md-on-surface-variant)` | |
| `bg-indigo-50` (chips) | `bg-primary-container text-on-primary-container` | Tonal container pair |
| `hover:bg-slate-50` | (built into state layer via `::before`) | Use `md-card-interactive` |
| `.cc-btn-primary` | `.md-btn-filled` | New M3 button family |
| `.cc-btn-secondary` | `.md-btn-elevated` or `.md-btn-outlined` | Choose by emphasis |

---

## 10 · Quick Reference

```
─── COLOR ROLES ─────────────────────────────────────────────────────────────────
Primary            --md-primary             #4f46e5   filled buttons, active states
On Primary         --md-on-primary          #ffffff   text ON primary
Primary Container  --md-primary-container   #e0e7ff   chips, tonal card bg
Earned             --md-earned              #059669   credits, completions
Staked             --md-staked              #d97706   pending, staked
Error              --md-error               #b91c1c   rejected, flagged

─── SURFACE ROLES ───────────────────────────────────────────────────────────────
Surface                     --md-surface                #f8f7ff  app shell
Surface Container Low       --md-surface-container-low  #f3f2fb  sidebar, nav
Surface Container           --md-surface-container      #eeedf5  standard card
Surface Container High      --md-surface-container-high #e8e7ef  filled inputs
Surface Container Highest   --md-surface-container-highest       tooltip, overlay

─── SHAPE ───────────────────────────────────────────────────────────────────────
Buttons         rounded-full  (ALWAYS)
Chips / Tags    rounded-sm    (8px)
Cards           rounded-md    (12px Medium)
Hero Cards      rounded-xl    (28px Extra Large)
Inputs          rounded-xs    (4px) filled top only, or rounded-sm for outlined

─── ELEVATION ───────────────────────────────────────────────────────────────────
Level 0  shadow-elev-0  flat             body text, dividers
Level 1  shadow-elev-1  shadow-sm        cards at rest, search bars
Level 2  shadow-elev-2  shadow-md        nav, hover cards
Level 3  shadow-elev-3  shadow-lg        dialogs, FABs

─── BUTTONS ─────────────────────────────────────────────────────────────────────
md-btn-filled    primary action, indigo bg, white text, rounded-full
md-btn-tonal     secondary, violet-container bg, semi-emphasis
md-btn-elevated  surface bg, primary text, has shadow
md-btn-outlined  transparent bg, outline border, primary text
md-btn-text      no bg, no border, primary text, minimum emphasis
md-btn-error     error bg, white text, destructive
md-btn-icon      circle, icon only, no bg

─── TYPE SCALE ──────────────────────────────────────────────────────────────────
text-display-lg/md/sm    Large expressive numbers and heroes
text-headline-lg/md/sm   Page and section titles
text-title-lg/md/sm      Card titles, dialog headers, pane labels
text-body-lg/md/sm       Body copy (body-lg is default)
text-label-lg/md/sm      Button text, chip text, table labels

─── STATE LAYERS (auto in md-* classes) ─────────────────────────────────────────
Hover    8%  of on-color
Focus   12%  of on-color
Pressed 12%  of on-color

─── NEVER ───────────────────────────────────────────────────────────────────────
- NO border-alone for separation — use elevation
- NO rounded-xl or rounded-lg on buttons — always rounded-full
- NO raw text-slate-* colors — use on-surface / on-surface-variant
- NO heavy shadows (shadow-xl, shadow-2xl) — max is shadow-elev-3
- NO background-color changes on hover — use ::before state layer
```

---

> **Spec reference:** https://m3.material.io/  
> **Files:** `tailwind.config.js` · `src/app/globals.css` · `design-system.md`  
> **Last updated:** April 2026
