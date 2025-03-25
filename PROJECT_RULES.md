# Project Rules and Guidelines

## Feature Implementation Rules
1. Each feature must be implemented in its own branch
2. Features must be marked as complete only after user confirmation
3. All features must include:
   - Unit tests with >80% coverage
   - Documentation updates
   - Code review approval
   - User acceptance testing

## Code Quality Rules
1. Follow PEP 8 style guide
2. Maximum line length: 88 characters (Black formatter standard)
3. All functions must have docstrings
4. Type hints are required for all function parameters and return values
5. No hardcoded values in production code
6. All secrets and API keys must be stored in environment variables

## Testing Requirements
1. Unit tests must be written before implementing features (TDD approach)
2. Integration tests required for all API endpoints
3. End-to-end tests for critical user flows
4. Test coverage must not decrease
5. All tests must pass before merging

## Documentation Requirements
1. README.md must be updated with new features
2. API documentation must be current
3. Code comments must explain complex logic
4. User guide must be updated for new features
5. Changelog must be maintained

## Git Workflow
1. Branch naming: feature/feature-name or bugfix/bug-name
2. Commit messages must follow conventional commits format
3. Pull requests must include:
   - Description of changes
   - Test results
   - Screenshots (if UI changes)
   - Related issue numbers

## Security Rules
1. No sensitive data in code or logs
2. Input validation required for all user inputs
3. Rate limiting on API endpoints
4. Regular security audits
5. Dependencies must be regularly updated

## Performance Requirements
1. Screenshot capture < 5 seconds
2. PowerPoint generation < 10 seconds
3. API response time < 2 seconds
4. Memory usage < 500MB
5. Regular performance testing

## Feature Completion Checklist
Before marking a feature as complete, verify:
1. [ ] All tests pass
2. [ ] Code review completed
3. [ ] Documentation updated
4. [ ] User acceptance testing completed
5. [ ] Performance requirements met
6. [ ] Security review completed
7. [ ] User confirmed feature works as expected

## Emergency Procedures
1. Critical bugs must be fixed within 24 hours
2. Security vulnerabilities must be addressed immediately
3. Data loss incidents require immediate notification
4. Service outages must be communicated to users
5. Regular backups must be maintained

## Maintenance Rules
1. Weekly dependency updates
2. Monthly security audits
3. Quarterly performance reviews
4. Regular code cleanup
5. Documentation reviews 