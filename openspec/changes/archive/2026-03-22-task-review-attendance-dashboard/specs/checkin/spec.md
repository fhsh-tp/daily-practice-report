## ADDED Requirements

### Requirement: Teacher accesses attendance management from points manage page

The points management page (`/pages/teacher/classes/{class_id}/points`) SHALL include a link or navigation entry to the attendance management page (`/pages/teacher/classes/{class_id}/attendance`). The existing generic point deduction form SHALL NOT be the sole mechanism for handling check-in exceptions.

#### Scenario: Points manage page links to attendance management

- **WHEN** a teacher views the points management page
- **THEN** the page SHALL display a clearly labeled link or card navigating to the attendance management page for the same class
