# modal-system Specification

## Purpose

Defines the shared non-blocking modal component that replaces native browser dialogs (`alert`, `confirm`) across all application pages.

## Requirements

### Requirement: Global non-blocking modal replaces browser dialogs

The application SHALL provide a shared, non-blocking Modal component available to all pages via `window.Modal`. All pages that previously called `alert()` or `confirm()` SHALL use `Modal.alert()` or `Modal.confirm()` instead. The modal component SHALL be defined in `shared/base.html` and SHALL be available without any additional import.

#### Scenario: Confirm modal shown with callback

- **WHEN** a page calls `Modal.confirm("Are you sure?", onConfirm, onCancel)`
- **THEN** a modal overlay appears with the message text, a "確認" button, and a "取消" button
- **AND** clicking "確認" calls `onConfirm` and closes the modal
- **AND** clicking "取消" or the backdrop calls `onCancel` (if provided) and closes the modal
- **AND** the page remains responsive while the modal is open (non-blocking)

#### Scenario: Alert modal shown with callback

- **WHEN** a page calls `Modal.alert("Operation failed.")`
- **THEN** a modal overlay appears with the message text and a "確認" button
- **AND** clicking "確認" closes the modal
- **AND** no `onCancel` handler is required

<!-- @trace
source: ui-polish-and-fixes
updated: 2026-03-19
-->

---
### Requirement: All existing browser dialog calls replaced

Every call to `window.confirm()` or `window.alert()` in HTML templates SHALL be replaced with the corresponding `Modal.confirm()` or `Modal.alert()` call. After this change, no template SHALL contain a direct call to the native browser dialog functions.

#### Scenario: Delete confirmation uses modal

- **WHEN** a user clicks a "刪除" or "移除" button
- **THEN** `Modal.confirm()` is called (not `window.confirm()`)
- **AND** the deletion proceeds only if the user clicks "確認" in the modal

<!-- @trace
source: ui-polish-and-fixes
updated: 2026-03-19
-->
