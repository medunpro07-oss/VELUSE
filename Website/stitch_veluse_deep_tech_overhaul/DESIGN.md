---
name: Algorithmic Precision
colors:
  surface: '#131317'
  surface-dim: '#131317'
  surface-bright: '#39393d'
  surface-container-lowest: '#0e0e12'
  surface-container-low: '#1b1b1f'
  surface-container: '#1f1f23'
  surface-container-high: '#2a292e'
  surface-container-highest: '#353439'
  on-surface: '#e5e1e7'
  on-surface-variant: '#c7c4d8'
  inverse-surface: '#e5e1e7'
  inverse-on-surface: '#303034'
  outline: '#918fa1'
  outline-variant: '#464555'
  surface-tint: '#c3c0ff'
  primary: '#c3c0ff'
  on-primary: '#1d00a5'
  primary-container: '#4f46e5'
  on-primary-container: '#dad7ff'
  inverse-primary: '#4d44e3'
  secondary: '#c7c5d2'
  on-secondary: '#302f39'
  secondary-container: '#494852'
  on-secondary-container: '#b9b7c3'
  tertiary: '#c8c5d1'
  on-tertiary: '#302f38'
  tertiary-container: '#605f69'
  on-tertiary-container: '#dddae6'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e2dfff'
  primary-fixed-dim: '#c3c0ff'
  on-primary-fixed: '#0f0069'
  on-primary-fixed-variant: '#3323cc'
  secondary-fixed: '#e4e1ee'
  secondary-fixed-dim: '#c7c5d2'
  on-secondary-fixed: '#1b1b24'
  on-secondary-fixed-variant: '#464650'
  tertiary-fixed: '#e4e1ed'
  tertiary-fixed-dim: '#c8c5d1'
  on-tertiary-fixed: '#1b1b23'
  on-tertiary-fixed-variant: '#46464f'
  background: '#131317'
  on-background: '#e5e1e7'
  surface-variant: '#353439'
  graphite-border: '#16161F'
  cyber-indigo: '#4F46E5'
  void-black: '#050508'
  text-muted: '#8E8E93'
  glass-sheen: rgba(255, 255, 255, 0.05)
typography:
  display-hero:
    fontFamily: Inter
    fontSize: 72px
    fontWeight: '800'
    lineHeight: '1.1'
    letterSpacing: -0.04em
  headline-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '800'
    lineHeight: '1.1'
    letterSpacing: -0.03em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '800'
    lineHeight: '1.1'
    letterSpacing: -0.03em
  subheader:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: '1.6'
    letterSpacing: 0.05em
  body-main:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: '1.6'
    letterSpacing: 0em
  mono-numeric:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '700'
    lineHeight: '1.0'
    letterSpacing: 0.1em
  label-cta:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '700'
    lineHeight: '1.0'
    letterSpacing: 0.1em
spacing:
  grid-margin: 2rem
  gutter: 1.5rem
  section-gap: 8rem
  container-max: 1280px
---

## Brand & Style

This design system embodies the "Algorithmic Minimalism" of a high-performance deep tech laboratory. It positions the product not as a creative service, but as a "Precision-Engineered" infrastructure. The visual language evokes feelings of computational power, unforgeable security, and elite technical authority.

The core aesthetic combines **Minimalism** with **Glassmorphism** and **High-Contrast** elements. It utilizes a "Matte Void" foundation to allow high-fidelity data and interface elements to appear as if projected onto a dark lens. The mood is cold, calculated, and professional—prioritizing information density and systemic logic over decorative flair.

## Colors

The palette is anchored in **Matte Void Black (#050508)**, providing a zero-light background that allows for extreme contrast. **Graphite (#16161F)** is reserved for structural definition, used exclusively for thin, 1px borders and container backgrounds to create subtle layering.

**Cyber-Indigo (#4F46E5)** acts as the primary energetic accent, used for interactive triggers, status indicators, and glowing radial effects. For secondary information, a range of desaturated grays provides hierarchy without breaking the monolithic dark theme. All surfaces should utilize a very low-opacity white overlay (0.03 - 0.05) to simulate a glass-like texture.

## Typography

The typographic system relies on a sharp contrast between high-impact sans-serif display type and technical monospaced utilitarian type. 

**Inter Tight** (Heavyweight) is used for all primary headlines. It must always be set with tight tracking (-0.03em to -0.04em) and tight line height to create a dense, "block-like" visual impact.

**JetBrains Mono** handles all descriptive prose, metadata, and interface labels. This reinforces the "algorithmic" brand personality, suggesting that the content is output from a high-performance system. Numbers should always use double-digit formatting (e.g., 01, 02) to maintain the technical aesthetic.

## Layout & Spacing

The system uses a **Fixed Grid** model on desktop (12 columns) and a **Fluid Grid** on mobile. Layouts are strictly sequential, often utilizing a multi-column "step" architecture to visualize process flow.

- **Desktop:** 12 columns, 24px gutters, 80px side margins.
- **Tablet:** 8 columns, 16px gutters, 40px side margins.
- **Mobile:** 4 columns, 12px gutters, 20px side margins.

Vertical spacing is aggressive. Major sections are separated by large "void" gaps (128px+) to ensure each technical phase is perceived as a distinct architectural layer. Alignment should be rigid and geometric; center-alignment is reserved only for hero introductions and final CTAs.

## Elevation & Depth

Depth is achieved through **Tonal Layering** and **Glassmorphism** rather than traditional drop shadows. 

1.  **Base Layer:** Pure #050508.
2.  **Surface Layer:** Graphite (#16161F) with a 1px border.
3.  **Active State:** "Glowing Radial Illumination." When a grid item or card is hovered, a soft radial gradient of Cyber-Indigo (#4F46E5) should appear behind the border, creating a subtle "backlight" effect.
4.  **Glass Sheen:** Interactive buttons and modals use a backdrop-blur (12px) and a semi-transparent surface (5% white) to create the "unforgeable pane of glass" effect. 

Shadows, if used, should be ultra-diffused, sharp, and tinted with the accent indigo at 10% opacity.

## Shapes

The shape language is strictly **Sharp (0px radius)**. Every element—from buttons and input fields to cards and images—must have 90-degree corners. This reinforces the precision-engineering theme and avoids the "friendly" softness of consumer apps. 

Decorative shapes should be limited to thin 1px lines, geometric markers (crosshairs, dots), and the sequential numeric anchors.

## Components

### Buttons
Buttons are strictly rectangular (0px radius). Primary buttons feature a solid Cyber-Indigo fill with white text. Secondary buttons use a "Glass Sheen" effect: transparent background, 1px Graphite border, and backdrop-filter blur. Hover states trigger a subtle indigo outer glow.

### Cards
Cards are Graphite (#16161F) containers with a 1px border. On interaction, the border illuminates with a radial gradient. Content inside cards should follow the 13px JetBrains Mono body style.

### Input Fields
Fields are dark-recessed boxes with a 1px Graphite border. Labels are placed above the field in 11px uppercase JetBrains Mono. On focus, the border changes to solid Cyber-Indigo.

### Sequential Numbers
Large, low-opacity display numbers (e.g., 01, 02) should be used as background anchors or section prefixes. They should be set in Inter Bold at 20% opacity of the Graphite color.

### Icons
Use **Material Symbols** with a "Sharp" weight. Icons should be monochrome (white or light gray) and strictly functional. Avoid illustrative or playful iconography.