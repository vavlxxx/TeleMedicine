# Stitch Migration Plan

## Priority screens

These Stitch exports were the first screens that needed native JSX because they participate in the real runtime flow:

| Stitch screen | Priority | Current state |
|---|---|---|
| `login-desktop-ru` | P0 | native React |
| `registration-desktop-ru` | P0 | native React |
| `doctor-directory-with-filters-ru` | P0 | native React |
| `doctor-public-profile-ru` | P0 | native React |
| `public-questions-feed-ru` | P0 | native React |

## Per-screen migration notes

| Screen | Visuals kept intact | Adapted for real data flow | `iframe` status | Responsive note |
|---|---|---|---|---|
| `login-desktop-ru` | glass card, ambient gradients, auth shell hierarchy | controlled fields, real `/auth/login`, success/error banners, disabled submit, redirect logic | removed from runtime | works inside the shared auth shell on desktop and mobile widths |
| `registration-desktop-ru` | same auth shell, wide split layout, explanatory side panel | patient-only contract, confirm password, `409/422` handling, redirect to login | removed from runtime | split grid collapses to one column on mobile |
| `doctor-directory-with-filters-ru` | discovery-focused catalog cards, summary hero, chip filters | `/doctors/`, `/specializations/`, empty/error/load-more states, profile links | removed from runtime | grids collapse at `959px` and below |
| `doctor-public-profile-ru` | public hero + two-column profile composition | `doctor_id` loading, `404`/missing-doctor state, only public DTO fields | removed from runtime | profile grid becomes single-column on tablet/mobile |
| `public-questions-feed-ru` | public information architecture, feed cards, inline actions | `/questions/`, patient question form, verified-doctor reply flow, deep-linking by `question_id` | removed from runtime | question feed and CTA blocks remain single-column on small screens |

## Isolation policy for remaining Stitch assets

- Runtime no longer depends on `iframe` wrappers for the interactive screens above.
- Files in `public/stitch/` and `stitch/raw/` remain as visual reference assets only.
- Native pages are the only source of truth for interaction, routing, loading/error states, and role checks.

## Visual integrity checks

- The migrated pages keep the same blue/emerald palette, glassy surfaces, rounded cards, and ambient background treatment used across the first frontend MVP.
- Auth screens share one shell; public directory/profile/Q&A/admin pages share one public-page design system.
- Responsive behavior is covered by existing breakpoints in `auth-shell.css` and `public-pages.css` and passes the production build without layout-specific errors.
