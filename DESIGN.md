---
name: WarmBalance
colors:
  surface: '#121413'
  surface-dim: '#121413'
  surface-bright: '#383938'
  surface-container-lowest: '#0d0e0e'
  surface-container-low: '#1b1c1b'
  surface-container: '#1f201f'
  surface-container-high: '#292a29'
  surface-container-highest: '#343534'
  on-surface: '#e3e2e0'
  on-surface-variant: '#c2c8c3'
  inverse-surface: '#e3e2e0'
  inverse-on-surface: '#30312f'
  outline: '#8c928e'
  outline-variant: '#424845'
  surface-tint: '#b3ccbf'
  primary: '#b3ccbf'
  on-primary: '#1f352c'
  primary-container: '#8fa79b'
  on-primary-container: '#273c33'
  inverse-primary: '#4d6359'
  secondary: '#e8bcbc'
  on-secondary: '#452929'
  secondary-container: '#614141'
  on-secondary-container: '#d9aeae'
  tertiary: '#e5bdba'
  on-tertiary: '#432a28'
  tertiary-container: '#be9996'
  on-tertiary-container: '#4c3130'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#cfe8db'
  primary-fixed-dim: '#b3ccbf'
  on-primary-fixed: '#091f17'
  on-primary-fixed-variant: '#354b42'
  secondary-fixed: '#ffdad9'
  secondary-fixed-dim: '#e8bcbc'
  on-secondary-fixed: '#2d1415'
  on-secondary-fixed-variant: '#5e3f3f'
  tertiary-fixed: '#ffdad7'
  tertiary-fixed-dim: '#e5bdba'
  on-tertiary-fixed: '#2c1514'
  on-tertiary-fixed-variant: '#5c403d'
  background: '#121413'
  on-background: '#e3e2e0'
  surface-variant: '#343534'
typography:
  display-xl:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '800'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: '1.3'
  title-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: '1.5'
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.6'
  label-caps:
    fontFamily: Inter
    fontSize: 10px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: 0.1em
  stats-lg:
    fontFamily: Inter
    fontSize: 30px
    fontWeight: '700'
    lineHeight: '1'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  container-padding: 2.5rem
  element-gap: 1.5rem
  section-margin: 2rem
  sidebar-width: 16rem
  grid-gutter: 1.5rem
---

## Brand & Style
WarmBalance is a financial auditing interface designed for "Eye-Comfort." The brand personality is professional yet empathetic, shifting away from the clinical, cold blues of traditional finance toward a warm, "coffee-and-sage" palette. 

The design style is **Corporate / Modern** with a focus on **Tonal Minimalism**. It prioritizes legibility and reduced eye strain through the use of off-white "cream" tones instead of pure whites, and warm charcoals instead of pure blacks. The emotional response is one of calm control and reliability, suitable for long-form auditing sessions.

## Colors
The palette is centered on an "Eye-Comfort" dark mode. The primary accent is a **Muted Sage Green** (#8fa79b), used for growth indicators and primary actions. A **Dusty Rose** (#b58d8d) serves as the secondary accent for liabilities and downward trends. 

The background uses a **Warm Charcoal-Coffee** (#1c1b1a) to avoid the harshness of true black. Surfaces and cards use a slightly lighter **Warm Neutral** (#2a2826). Text is rendered in **Cream** (#e8e4df) to soften the contrast and reduce glare.

## Typography
The system utilizes **Inter** exclusively to maintain a systematic, utilitarian, and highly readable feel. 

- **Headlines:** Use heavy weights (700-800) with tight tracking for a grounded, authoritative presence.
- **Numbers:** Financial data uses `tabular-nums` to ensure vertical alignment in lists and grids.
- **Labels:** Small caps with wide letter-spacing are used for section headers to provide clear hierarchy without excessive size.
- **Body:** Standard body text is kept at 14px for density without sacrificing legibility on high-resolution displays.

## Layout & Spacing
The layout follows a **Hybrid Fluid Grid**. The main structure consists of a fixed-width sidebar (256px/16rem) and a flexible content area with a maximum width of 1400px. 

Spacing is based on an 8px (0.5rem) scale. 
- **Margins:** Large page-level padding of 40px (2.5rem) provides significant whitespace.
- **Grids:** A 3-column responsive grid is used for top-level metrics, collapsing to 1-column on mobile.
- **Lists:** Content within cards uses consistent 20px (1.25rem) horizontal padding.

## Elevation & Depth
Depth is achieved primarily through **Tonal Layering** and **Soft Ghost Borders** rather than aggressive shadows.

- **Level 0 (Background):** #1c1b1a (Warm Charcoal).
- **Level 1 (Sidebar/Secondary):** Transparent overlays or 50% opacity of the background.
- **Level 2 (Cards):** #2a2826 (Lighter Warm Neutral) with a 1px border.
- **Accents:** Borders use a subtle primary-tinted stroke (e.g., `primary/5` or `primary/10`) to create a soft "inner glow" effect on dark surfaces.
- **Hover States:** Elements use a slight scale-up (1.01) and background tint shift rather than increased shadow.

## Shapes
The shape language is **Soft and Precise**. 
- **Standard Corners:** Most containers and buttons use a 0.4rem (6.4px) radius.
- **Large Cards:** Metrics cards and main content wrappers use a 0.75rem to 1rem radius for a more approachable, modern feel.
- **Interactive Elements:** Small interactive chips and status indicators use a `full` (pill) radius for distinct visual categorization.

## Components
- **Buttons:** Primary buttons are solid Sage (#8fa79b) with dark text. Secondary buttons are outlined or use the `surface-dark` background with a subtle border.
- **Cards:** White or surface-dark backgrounds with a 1px border. Financial cards feature an icon in the top right and growth indicators in the bottom left.
- **Sidebar Nav:** Active states use a low-opacity primary tint (`primary/15`) with a high-contrast label. Icons are 24px Material Symbols.
- **Input Fields:** Search bars are integrated into the header with a `surface-dark` background, removing borders until focused.
- **Status Pills:** Used for percentages and "Eye-Comfort" status. They consist of a 10% opacity background of the signal color (Sage or Rose) with a 100% opacity bold label inside.
- **Data Lists:** Feature hover-highlighting and consistent 10px spacing between the icon/avatar and primary text label.