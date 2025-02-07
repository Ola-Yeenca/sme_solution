# Project Integration Guide

### Objective  
Connect a Python/Flask backend API to a React/Vite (TypeScript) frontend, ensuring full integration and functionality.

---

## Instructions for Cursor IDE Agent

1. **Project Analysis**  
   - Thoroughly review all project files in both `/backend` (Flask) and `/frontend` (React/Vite) directories.
   - Identify key files:
     - Backend: `app.py`, route handlers, models, and configuration files
     - Frontend: `package.json`, API service files, React components, and TypeScript interfaces
     - Environment configurations (`.env`, `config.py`, `vite.config.ts`)

2. **Architecture Understanding**  
   - Explain the current project structure and how data flows between components.
   - Clarify:
     - RESTful API endpoints in Flask
     - React components consuming API data
     - TypeScript interfaces matching API response schemas
     - Authentication/authorization mechanisms (if any)

3. **Connection Requirements**  
   - Ensure the following technical links:
     - **CORS Configuration**: Verify `flask-cors` is properly initialized
     - **API Proxy**: Set up Vite proxy to avoid CORS issues during development
     - **Request Handling**: Create TypeScript fetch/Axios utility functions
     - **Environment Variables**: Connect frontend `.env` variables to backend URL

4. **Implementation Steps**  
   Provide explicit code-level guidance for:
   - **Backend**:
     ```python
     # Example: Add CORS support if missing
     from flask_cors import CORS
     CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
     ```
   - **Frontend**:
     ```typescript
     // Example: API service module
     export const fetchData = async (): Promise<ApiResponseType> => {
       const response = await fetch('/api/data-endpoint');
       return await response.json();
     }
     ```

5. **Testing Protocol**  
   - Create a test plan covering:
     - Backend API verification using Postman/curl
     - Frontend integration tests with mock data
     - End-to-end user flow validation
   - Include error handling patterns for:
     - Network failures
     - API authentication errors
     - Data type mismatches

6. **Documentation**  
   - Generate integration documentation covering:
     - API endpoint list with parameters/response types
     - Frontend data fetching patterns
     - Common troubleshooting scenarios (CORS, type errors, connection refused)

---

## Special Requests

- **Ask Before Proceeding** if any of these are unclear:
  - Authentication flow between frontend/backend
  - Complex data type mappings
  - State management synchronization
- **Provide Code Snippets** for both Python and TypeScript simultaneously
- **Highlight Potential Conflicts** between current implementation and suggested solutions

---

**Response Format**  
Present explanations in this structure:

1. Concept Overview
2. Current Implementation Analysis
3. Required Modifications (with code examples)
4. Testing Recommendations
5. Additional Optimization Suggestions
