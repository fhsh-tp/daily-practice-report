## ADDED Requirements

### Requirement: Teacher can archive a task template

A teacher SHALL be able to archive a task template they manage. Archiving SHALL set `is_archived = True` on the template. An archived template SHALL remain visible in the teacher's template management list (styled differently to indicate archived status). An archived template SHALL NOT be used to fulfill `get_template_for_date()` queries — it behaves as if no template is assigned.

#### Scenario: Teacher archives a template

- **WHEN** a teacher clicks "封存" on a template in the templates list
- **THEN** `PATCH /templates/{template_id}/archive` is called
- **AND** the template's `is_archived` field is set to `True`
- **AND** the template remains visible to the teacher with an "已封存" label

#### Scenario: Archived template hidden from students

- **WHEN** a student visits the submission page on a date assigned to an archived template
- **THEN** the system behaves as if no template is assigned for that date
- **AND** the student cannot submit a task

### Requirement: Teacher can unarchive a task template

A teacher SHALL be able to restore an archived template to active status via an "取消封存" action. After unarchiving, the template SHALL once again fulfill `get_template_for_date()` queries normally.

#### Scenario: Teacher unarchives a template

- **WHEN** a teacher clicks "取消封存" on an archived template
- **THEN** `PATCH /templates/{template_id}/unarchive` is called
- **AND** the template's `is_archived` field is set to `False`
- **AND** the template is treated as active again
