# Workflow Status

This document tracks the CI/CD workflow configuration and common issues.

## Current Workflow Configuration

The TCU CEAA CI/CD Pipeline includes:
- **Backend Tests**: Django application tests with PostgreSQL
- **Frontend Tests**: React/TypeScript tests with Jest
- **Security Scan**: Dependency vulnerability scanning
- **Build and Deploy**: Production build artifacts

## Workflow Triggers

The workflow runs on:
- Push to `main`, `develop`, or `AI_Integration` branches
- Pull requests to `main` branch

## Common Issues

### Draft PRs
Draft pull requests may require manual approval before workflows run. Convert the PR to "Ready for review" to trigger the workflow.

### First-time Contributors
Pull requests from first-time contributors or bots may require repository maintainer approval before workflows execute.

## Running the Workflow

1. Ensure all required files are present:
   - `backend/requirements-ci.txt`
   - `frontend/package.json`
   - `frontend/package-lock.json`
   - `tests/backend/integration_tests/test_ci_dependency_resolution.py`

2. The workflow will automatically run on pushes and pull requests that meet the trigger conditions.

3. Check the Actions tab for workflow run status and logs.
