# Requirements Document - Phase 2: Web GUI Mode

## Introduction

Phase 2 of SQLTrans adds a web-based graphical user interface (GUI) as an alternative to the existing terminal UI. Users can choose between GUI and TUI modes at launch, providing flexibility for different use cases and preferences.

## Alignment with Product Vision

This feature extends the product goals outlined in product.md:
- **Accessibility**: Web GUI lowers the barrier for users less comfortable with terminal interfaces
- **Visual Appeal**: Modern web UI with better visual feedback and styling
- **Local-First**: Runs on localhost, no external dependencies or cloud services
- **Dual Mode**: Preserves TUI for power users while adding GUI for wider adoption

## Requirements

### Requirement 1: Web Application Framework

**User Story:** As a developer, I want a lightweight web framework that can serve the GUI locally, so that users get a responsive interface without external dependencies.

#### Acceptance Criteria

1. WHEN the application starts in GUI mode THEN the system SHALL launch a local web server on an available port
2. WHEN the web server starts THEN the system SHALL automatically open the default browser to the application URL
3. WHEN the user closes the browser THEN the system SHALL continue running until explicitly stopped (Ctrl+C)
4. WHEN the server binds to a port THEN the system SHALL display the URL in the console
5. WHEN the port is in use THEN the system SHALL try alternative ports automatically
6. WHEN the server shuts down THEN the system SHALL clean up resources gracefully

### Requirement 2: REST API Backend

**User Story:** As a frontend developer, I want REST API endpoints for query operations, so that the web UI can interact with the business logic.

#### Acceptance Criteria

1. WHEN the frontend requests GET /api/query THEN the system SHALL return the current QueryState as JSON
2. WHEN the frontend sends POST /api/query/table THEN the system SHALL validate and set the table name
3. WHEN the frontend sends POST /api/query/columns THEN the system SHALL add/remove columns
4. WHEN the frontend sends POST /api/query/filters THEN the system SHALL add filters with validation
5. WHEN the frontend sends DELETE /api/query/filters/:index THEN the system SHALL remove the specified filter
6. WHEN the frontend sends POST /api/query/dialect THEN the system SHALL change the dialect and regenerate SQL
7. WHEN the frontend sends POST /api/query/clear THEN the system SHALL reset the query state
8. WHEN the frontend requests GET /api/query/sql THEN the system SHALL return formatted SQL with syntax highlighting
9. WHEN validation fails THEN the system SHALL return 400 status with error details
10. WHEN an internal error occurs THEN the system SHALL return 500 status with error message

### Requirement 3: Interactive Web UI

**User Story:** As a support engineer, I want a visual web interface for building queries, so that I can work in a familiar browser environment.

#### Acceptance Criteria

1. WHEN the user opens the application THEN the system SHALL display a clean, organized layout with distinct sections
2. WHEN the user selects a dialect THEN the system SHALL update immediately and regenerate SQL
3. WHEN the user enters a table name THEN the system SHALL validate in real-time with visual feedback
4. WHEN the user adds columns THEN the system SHALL display them in a list with remove buttons
5. WHEN the user adds a filter THEN the system SHALL show a form with column, operator, and value inputs
6. WHEN the user selects an operator THEN the system SHALL adjust the value input (hide for NULL, show list for IN)
7. WHEN the SQL updates THEN the system SHALL display it with syntax highlighting
8. WHEN the user clicks "Copy SQL" THEN the system SHALL copy to clipboard with success feedback
9. WHEN the user clicks "Download SQL" THEN the system SHALL trigger file download
10. WHEN validation errors occur THEN the system SHALL display clear error messages near the relevant input

### Requirement 4: Dual Mode Launcher

**User Story:** As a user, I want to choose between GUI and TUI modes at launch, so that I can use the interface that best suits my workflow.

#### Acceptance Criteria

1. WHEN the user runs `sqltrans --gui` THEN the system SHALL launch in web GUI mode
2. WHEN the user runs `sqltrans --tui` THEN the system SHALL launch in terminal TUI mode
3. WHEN the user runs `sqltrans` without flags THEN the system SHALL use the mode from config (default: TUI)
4. WHEN the config file specifies default_mode THEN the system SHALL respect that preference
5. WHEN the user runs `sqltrans --help` THEN the system SHALL document both --gui and --tui options
6. WHEN GUI mode cannot start (port issues, etc.) THEN the system SHALL show clear error and suggest TUI mode

### Requirement 5: Real-time Query Synchronization

**User Story:** As a user, I want the SQL preview to update instantly as I build the query, so that I can see the result of my changes immediately.

#### Acceptance Criteria

1. WHEN any query element changes THEN the SQL preview SHALL update within 100ms
2. WHEN the dialect changes THEN the SQL SHALL regenerate with new syntax immediately
3. WHEN validation fails THEN the SQL preview SHALL show the last valid query
4. WHEN the query is cleared THEN the SQL preview SHALL show "No query built"
5. WHEN multiple rapid changes occur THEN the system SHALL debounce updates to avoid flicker

### Requirement 6: Modern Responsive UI

**User Story:** As a user, I want a modern, responsive interface that works on different screen sizes, so that I can use the tool on various devices.

#### Acceptance Criteria

1. WHEN the user opens the application THEN the system SHALL display a modern, professional design
2. WHEN the screen size changes THEN the layout SHALL adapt responsively
3. WHEN the user interacts with elements THEN the system SHALL provide visual feedback (hover, focus, active states)
4. WHEN operations succeed THEN the system SHALL show success notifications
5. WHEN operations fail THEN the system SHALL show error notifications
6. WHEN the application is loading THEN the system SHALL display loading indicators
7. WHEN buttons are clicked THEN the system SHALL show temporary disabled state to prevent double-clicks

## Non-Functional Requirements

### Architecture and Code Reuse
- **Leverage Existing Logic**: Reuse 100% of models, SQL generation, validation, and business logic
- **Clean Separation**: Web layer should only handle HTTP, not business logic
- **API Design**: RESTful endpoints following standard conventions
- **Frontend Framework**: Vanilla JavaScript or lightweight framework (Alpine.js, HTMX)

### Performance
- Server startup time: < 2 seconds
- API response time: < 50ms for all endpoints
- Frontend rendering: < 100ms for UI updates
- Browser compatibility: Modern browsers (Chrome, Firefox, Edge, Safari)

### Security
- Server binds to localhost only (127.0.0.1) - no external access
- Input validation on both frontend and backend
- CORS disabled (local-only application)
- No authentication needed (local single-user app)

### Usability
- Clear visual hierarchy and spacing
- Consistent color scheme and styling
- Helpful error messages with recovery suggestions
- Keyboard shortcuts for common actions
- Tab navigation support for accessibility

### Maintainability
- Separate frontend and backend concerns
- Reusable UI components
- Clear API documentation
- Type hints for all Python code
- JSDoc comments for JavaScript functions
