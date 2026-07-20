# Component patterns: premium vs. generic

A checklist for auditing or designing specific components common to financial/data products. Use this after reading SKILL.md's core principles — this file is the applied checklist, not the theory.

## Data cards (stat tiles, KPI cards)

| Generic | Premium |
|---|---|
| Border + shadow on every card | Flat surface differentiated by subtle background shift; border only on hover/focus |
| Label and value same weight/size | Small uppercase secondary-color label, large tabular-nums value, small colored delta |
| Static | Value flashes/highlights briefly on update, fades back over ~600ms–1s |
| Icon as decoration | Icon reinforces the metric's meaning (trend arrow, category glyph) or omitted entirely |

## Tables (market data, calendars, holdings)

| Generic | Premium |
|---|---|
| Heavy grid lines on every cell | Row separators only (1px, low-contrast), column alignment does the organizing |
| Center-aligned numbers | Right-aligned, tabular-nums, decimal-aligned |
| Static row | Row hover highlights the full row (background shift), not just the cell |
| Red/green text only | Red/green + directional glyph (▲/▼) for colorblind accessibility |
| All columns equal visual weight | Primary column (name/ticker) bolder; secondary columns (volume, etc.) in secondary color |
| Pagination only | Sticky header row on scroll for long tables |

## Charts / sparklines

| Generic | Premium |
|---|---|
| Default charting-library styling (heavy gridlines, legend boxes) | Gridlines removed or near-invisible; axis labels minimal |
| Every data point labeled | Only key points labeled (latest value, min/max); rest revealed on hover/tooltip |
| Static render | Line draws in on load (stroke-dashoffset animation) or area fades in |
| Generic tooltip (browser default or boxy) | Custom tooltip matching type system, tabular-nums, appears with a 100–150ms fade |
| One color for all series | Accent color reserved for the primary/featured series; others muted |

## Navigation

| Generic | Premium |
|---|---|
| Dropdown appears instantly | Dropdown fades/translates in over ~150–200ms with a slight delay on close (forgiving hover) |
| Flat list of links | Grouped with small category labels, optional icon + description for key items |
| Active state = color change only | Active state = color + a persistent indicator (underline, dot, background) |
| Search buried in a menu | Global search/command palette (⌘K) for product surfaces with lots of content (calendar, reports, tickers) |

## Buttons & CTAs

| Generic | Premium |
|---|---|
| One button style everywhere | Clear primary/secondary/tertiary hierarchy, used consistently |
| Instant hover color swap | Hover transitions background/border over 120–200ms; pressed state slightly scales down (~0.98) |
| Loading = disabled + spinner replaces label | Label stays, small inline spinner appended, button width doesn't jump |
| Generic corner radius mismatched to rest of UI | Radius token consistent with cards/inputs elsewhere in the system |

## Real-time / "live" indicators

| Generic | Premium |
|---|---|
| Static "LIVE" text badge | Small dot with a slow pulse animation (`opacity` keyframe, ~1.5–2s loop), paired with a timestamp |
| No indication of staleness | "as of HH:MM" or relative time ("updated 2 min ago"), updates without a full page refresh feel |
| Ticker jumps/cuts at loop point | Ticker track duplicated and translated seamlessly (no visible reset) |
| Error state = blank/broken UI | Explicit error/stale-data state styled consistently with the rest of the status system |

## Forms & inputs (signup, alerts, preferences)

| Generic | Premium |
|---|---|
| Label appears only as placeholder (disappears on focus/input) | Persistent label (floating or static above field) |
| Validation only on submit | Inline validation on blur, specific error copy (not just "invalid") |
| Generic browser-default select/checkbox | Custom-styled to match design tokens, but still fully keyboard-accessible |
| Flat "Submit" | Button reflects the actual value ("Get my report", "Start free") |

## Empty / loading / error states

| Generic | Premium |
|---|---|
| Spinner only | Skeleton shapes matching the eventual content's layout |
| Blank white/dark space when no data | Designed empty state with a clear next action ("No alerts yet — set one up") |
| Generic "Something went wrong" | Specific, on-brand error copy with a retry action, styled consistently with the status/badge system elsewhere |
