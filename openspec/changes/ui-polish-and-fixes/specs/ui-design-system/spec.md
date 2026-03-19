## ADDED Requirements

### Requirement: Shared modal component in base template

The `shared/base.html` template SHALL include a modal overlay element and a `window.Modal` JavaScript API before the closing `</body>` tag. All other templates SHALL use this API instead of native browser dialogs.

#### Scenario: Modal component available in all pages

- **WHEN** any page extending `shared/base.html` is loaded
- **THEN** `window.Modal.confirm` and `window.Modal.alert` SHALL be callable
- **AND** the modal HTML overlay SHALL be present in the DOM

### Requirement: Navigation links SHALL be correct and consistent

All navigation links in `shared/base.html` SHALL resolve to existing page routes. Sidebar links, mobile tab bar links, and in-page links SHALL all point to the same canonical URL for each destination.

#### Scenario: My Badges navigation link resolves correctly

- **WHEN** a student clicks "我的徽章" in any navigation element
- **THEN** the browser navigates to `/pages/students/me/badges`
- **AND** the page loads successfully with HTTP 200
