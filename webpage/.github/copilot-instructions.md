<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Python Flask Web Application

This is a Python web application built with Flask framework. When working on this project:

## Code Style and Standards
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused on a single responsibility

## Flask Best Practices
- Use Flask blueprints for larger applications
- Implement proper error handling with try-catch blocks
- Use Flask's url_for() function for URL generation
- Follow RESTful routing conventions
- Validate user input and sanitize data

## Template Guidelines
- Use Jinja2 template inheritance with base.html
- Keep templates organized in the templates/ directory
- Use semantic HTML5 elements
- Ensure responsive design with Bootstrap classes
- Add proper meta tags and accessibility attributes

## Static Files
- Organize CSS files in static/css/
- Keep JavaScript files in static/js/
- Optimize images and place them in static/images/
- Use Flask's url_for() for static file references

## Security Considerations
- Implement CSRF protection for forms
- Validate and sanitize all user inputs
- Use environment variables for sensitive configuration
- Implement proper session management
- Add input validation and error handling

## Development Workflow
- Use virtual environments for dependency management
- Keep requirements.txt updated
- Add proper logging for debugging
- Implement unit tests for critical functionality
- Use environment-specific configuration files
