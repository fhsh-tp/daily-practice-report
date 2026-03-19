## MODIFIED Requirements

### Requirement: Student task submission HTML page

The system SHALL serve a task submission form page at `GET /pages/student/classes/{class_id}/submit`. The page SHALL require authentication. It SHALL display the current day's task template fields and allow the student to submit. If an `error` query parameter is present, the page SHALL display it.

The form layout SHALL render each template field in a mixed-field format:

- **text** fields: a single-line `<input type="text">` with label
- **markdown** fields: a Toast UI Editor (`toastui.Editor`) instance mounted on a `<div>` with a corresponding hidden `<input type="hidden">` that receives the Markdown source value before form submission. The editor SHALL be initialized with `initialEditType: 'markdown'` and `previewStyle: 'vertical'`. The editor SHALL carry a commented `toolbarItems` extension block in source code showing how to add `['link', 'image']` and `['table']` toolbar groups.
- **number** fields: an `<input type="number">` with label
- **checkbox** fields: an `<input type="checkbox">` with label

The Toast UI Editor SHALL be loaded from `https://uicdn.toast.com/editor/latest/` CDN and SHALL NOT use EasyMDE.

#### Scenario: Submit page shows today's template

- **WHEN** an authenticated student navigates to `GET /pages/student/classes/{class_id}/submit`
- **THEN** the system SHALL display an HTML form with all fields from today's assigned template for that class, each rendered in the appropriate mixed-field widget

#### Scenario: Markdown field uses Toast UI Editor

- **WHEN** the submit page includes a field of type `markdown`
- **THEN** the page SHALL render a Toast UI Editor instance in Markdown source mode with a vertical live preview panel

#### Scenario: Submit page shown with error

- **WHEN** `GET /pages/student/classes/{class_id}/submit?error=<message>` is requested
- **THEN** the page SHALL display the error message

---

## REMOVED Requirements

### Requirement: EasyMDE used for markdown fields

**Reason**: Replaced by Toast UI Editor, which provides native dark mode support, built-in WYSIWYG/Markdown dual-mode, and a complete CDN bundle. EasyMDE required excessive CSS overrides for dark mode compatibility.

**Migration**: Remove EasyMDE CDN links from all templates. Replace EasyMDE initialization scripts in `submit_task.html` with Toast UI Editor initialization using `initialEditType: 'markdown'` and `previewStyle: 'vertical'`. Map the TUI Editor `change` event to sync content into the hidden `<input>` before form submission.

#### Scenario: EasyMDE no longer present in rendered pages

- **WHEN** any page in the application is rendered
- **THEN** no `<link>` or `<script>` referencing EasyMDE SHALL be present in the HTML output
