# ui-design-system Specification

## Purpose

Defines the shared visual design system for the application: CSS framework, typography, color tokens, dark mode strategy, responsive navigation structure, and template authoring conventions.

## Requirements

### Requirement: Tailwind CSS replaces Pico CSS as the styling foundation

All templates SHALL load Tailwind CSS via the Play CDN (`https://cdn.tailwindcss.com`) instead of Pico CSS. The `shared/base.html` template SHALL include an inline `<script>` block immediately after the Tailwind CDN tag that configures `tailwind.config` with the Academic Pro design tokens: `darkMode: 'class'`, a `brand` color scale (violet 50–950, centered on `#7c3aed`), and font family extensions for Poppins (headings) and Open Sans (body).

#### Scenario: Brand token available in all templates

- **WHEN** any template that extends `shared/base.html` uses a `brand-600` class
- **THEN** the browser SHALL apply `#7c3aed` as the resolved color value

#### Scenario: Pico CSS is absent

- **WHEN** any page is rendered
- **THEN** no `<link>` referencing `cdn.jsdelivr.net/npm/@picocss` SHALL be present in the HTML output

<!-- @trace
source: ui-redesign-academic-pro
updated: 2026-03-19
-->


<!-- @trace
source: ui-redesign-academic-pro
updated: 2026-03-19
code:
  - src/templates/community/leaderboard.html
  - src/templates/login.html
  - src/templates/setup.html
  - src/templates/teacher/template_form.html
  - src/templates/student/badges.html
  - src/templates/student/dashboard.html
  - src/templates/teacher/points_manage.html
  - src/templates/community/feed.html
  - src/templates/teacher/templates_list.html
  - src/templates/shared/base.html
  - src/templates/student/submit_task.html
-->

---
### Requirement: Light and Dark mode controlled by `<html>` class

The system SHALL implement dark mode using Tailwind's `class` strategy. The `<html>` element SHALL carry the `dark` class when dark mode is active. An inline `<script>` in `<head>` — placed before any stylesheets — SHALL read `localStorage.theme` and immediately apply or remove the `dark` class on `<html>` to prevent flash of unstyled content (FOUC). A theme toggle control SHALL write `localStorage.theme` to `'dark'` or `'light'` and update the `<html>` class accordingly.

#### Scenario: Dark mode applied before first paint

- **WHEN** a user has `localStorage.theme === 'dark'` and loads any page
- **THEN** the `<html>` element SHALL have class `dark` before any visible content renders

#### Scenario: Theme persisted across navigation

- **WHEN** a user toggles to dark mode on any page and then navigates to another page
- **THEN** the new page SHALL render in dark mode without a light-mode flash

<!-- @trace
source: ui-redesign-academic-pro
updated: 2026-03-19
-->


<!-- @trace
source: ui-redesign-academic-pro
updated: 2026-03-19
code:
  - src/templates/community/leaderboard.html
  - src/templates/login.html
  - src/templates/setup.html
  - src/templates/teacher/template_form.html
  - src/templates/student/badges.html
  - src/templates/student/dashboard.html
  - src/templates/teacher/points_manage.html
  - src/templates/community/feed.html
  - src/templates/teacher/templates_list.html
  - src/templates/shared/base.html
  - src/templates/student/submit_task.html
-->

---
### Requirement: Typography system uses Poppins and Open Sans

The `shared/base.html` SHALL load Poppins (weights 600, 700) and Open Sans (weights 400, 600) from Google Fonts. The `tailwind.config` SHALL map `fontFamily.heading` to `['Poppins', 'sans-serif']` and `fontFamily.sans` to `['Open Sans', 'sans-serif']`. All heading elements (`h1`–`h3`) in templates SHALL use `font-heading` to apply Poppins.

#### Scenario: Poppins applied to headings

- **WHEN** a page with an `<h1 class="font-heading">` is rendered
- **THEN** the browser SHALL resolve the font to Poppins

#### Scenario: Open Sans applied to body text

- **WHEN** a page is rendered with no explicit font class on body text
- **THEN** the browser SHALL apply Open Sans as the base body font via the `font-sans` default

<!-- @trace
source: ui-redesign-academic-pro
updated: 2026-03-19
-->


<!-- @trace
source: ui-redesign-academic-pro
updated: 2026-03-19
code:
  - src/templates/community/leaderboard.html
  - src/templates/login.html
  - src/templates/setup.html
  - src/templates/teacher/template_form.html
  - src/templates/student/badges.html
  - src/templates/student/dashboard.html
  - src/templates/teacher/points_manage.html
  - src/templates/community/feed.html
  - src/templates/teacher/templates_list.html
  - src/templates/shared/base.html
  - src/templates/student/submit_task.html
-->

---
### Requirement: RWD navigation adapts to three breakpoints

The `shared/base.html` SHALL render three distinct navigation structures based on viewport width:

- **Mobile (< 768px)**: A bottom tab bar fixed to the viewport bottom with 4 primary navigation items (Dashboard, Submit, Community, Profile/More). No sidebar or top navbar.
- **Tablet (768px–1023px)**: A horizontal top navbar with navigation links. No sidebar, no bottom tab bar.
- **Desktop (≥ 1024px)**: A collapsible left sidebar (default expanded, icon + label) plus a top bar containing search, notifications, and user controls. The sidebar SHALL have an active-state style of `bg-brand-50 dark:bg-brand-900/20 text-brand-700 font-semibold`.

Each navigation structure SHALL be conditionally rendered using Tailwind responsive prefixes (`md:`, `lg:`), not JavaScript.

#### Scenario: Mobile shows bottom tab bar only

- **WHEN** viewport width is below 768px
- **THEN** the bottom tab bar SHALL be visible and the sidebar and top navbar SHALL be hidden

#### Scenario: Desktop shows sidebar and top bar

- **WHEN** viewport width is 1024px or above
- **THEN** the collapsible sidebar and top bar SHALL be visible and the bottom tab bar SHALL be hidden

#### Scenario: Active sidebar item is highlighted

- **WHEN** the current page path matches a sidebar navigation item
- **THEN** that item SHALL have the brand active-state background and text color applied

<!-- @trace
source: ui-redesign-academic-pro
updated: 2026-03-19
-->


<!-- @trace
source: ui-redesign-academic-pro
updated: 2026-03-19
code:
  - src/templates/community/leaderboard.html
  - src/templates/login.html
  - src/templates/setup.html
  - src/templates/teacher/template_form.html
  - src/templates/student/badges.html
  - src/templates/student/dashboard.html
  - src/templates/teacher/points_manage.html
  - src/templates/community/feed.html
  - src/templates/teacher/templates_list.html
  - src/templates/shared/base.html
  - src/templates/student/submit_task.html
-->

---
### Requirement: setup.html inherits shared/base.html

The `setup.html` template SHALL extend `shared/base.html` and remove its standalone inline CSS. All visual styling SHALL be provided by the inherited Tailwind-based design system.

#### Scenario: Setup page uses design system styles

- **WHEN** the setup page is rendered
- **THEN** it SHALL use the same Tailwind brand colors, typography, and dark mode behavior as all other templates

<!-- @trace
source: ui-redesign-academic-pro
updated: 2026-03-19
-->


<!-- @trace
source: ui-redesign-academic-pro
updated: 2026-03-19
code:
  - src/templates/community/leaderboard.html
  - src/templates/login.html
  - src/templates/setup.html
  - src/templates/teacher/template_form.html
  - src/templates/student/badges.html
  - src/templates/student/dashboard.html
  - src/templates/teacher/points_manage.html
  - src/templates/community/feed.html
  - src/templates/teacher/templates_list.html
  - src/templates/shared/base.html
  - src/templates/student/submit_task.html
-->

---
### Requirement: All class attribute strings are written in full

All Tailwind utility class names in templates SHALL be written as complete strings. No class name SHALL be constructed via string concatenation or JavaScript template literals, because the Tailwind Play CDN scans static DOM text to generate styles and will not detect dynamically assembled class names.

#### Scenario: Dynamic class avoided

- **WHEN** a template conditionally applies a brand color class
- **THEN** both the truthy and falsy class names SHALL appear as complete literal strings in the template source

<!-- @trace
source: ui-redesign-academic-pro
updated: 2026-03-19
-->

<!-- @trace
source: ui-redesign-academic-pro
updated: 2026-03-19
code:
  - src/templates/community/leaderboard.html
  - src/templates/login.html
  - src/templates/setup.html
  - src/templates/teacher/template_form.html
  - src/templates/student/badges.html
  - src/templates/student/dashboard.html
  - src/templates/teacher/points_manage.html
  - src/templates/community/feed.html
  - src/templates/teacher/templates_list.html
  - src/templates/shared/base.html
  - src/templates/student/submit_task.html
-->

---
### Requirement: Shared modal component in base template

The `shared/base.html` template SHALL include a modal overlay element and a `window.Modal` JavaScript API before the closing `</body>` tag. All other templates SHALL use this API instead of native browser dialogs.

#### Scenario: Modal component available in all pages

- **WHEN** any page extending `shared/base.html` is loaded
- **THEN** `window.Modal.confirm` and `window.Modal.alert` SHALL be callable
- **AND** the modal HTML overlay SHALL be present in the DOM

<!-- @trace
source: ui-polish-and-fixes
updated: 2026-03-19
-->

---
### Requirement: Navigation links SHALL be correct and consistent

All navigation links in `shared/base.html` SHALL resolve to existing page routes. Sidebar links, mobile tab bar links, and in-page links SHALL all point to the same canonical URL for each destination.

#### Scenario: My Badges navigation link resolves correctly

- **WHEN** a student clicks "我的徽章" in any navigation element
- **THEN** the browser navigates to `/pages/students/me/badges`
- **AND** the page loads successfully with HTTP 200

<!-- @trace
source: ui-polish-and-fixes
updated: 2026-03-19
-->