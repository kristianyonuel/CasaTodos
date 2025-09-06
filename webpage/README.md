# Python Flask Web Application

A modern, responsive web application built with Python Flask framework featuring a clean design and Bootstrap styling.

## 🚀 Features

- **Modern Design**: Clean and responsive UI with Bootstrap 5
- **Flask Framework**: Lightweight and powerful Python web framework
- **Template Inheritance**: Organized templates using Jinja2
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile devices
- **Easy to Customize**: Well-structured code that's easy to modify and extend

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## 🛠️ Installation

1. **Clone or download this project**
   ```bash
   # If using git
   git clone <repository-url>
   cd webpage
   ```

2. **Create and activate virtual environment** (recommended)
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS/Linux
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Running the Application

1. **Start the development server**
   ```bash
   python app.py
   ```

2. **Open your browser and visit**
   ```
   http://localhost:5000
   ```

## 📁 Project Structure

```
webpage/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── .github/
│   └── copilot-instructions.md  # Copilot customization
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   ├── about.html       # About page
│   └── contact.html     # Contact page
└── static/              # Static files
    └── css/
        └── style.css    # Custom CSS styles
```

## 🎨 Customization

### Adding New Pages

1. **Create a new route in app.py**
   ```python
   @app.route('/new-page')
   def new_page():
       return render_template('new-page.html')
   ```

2. **Create the template file**
   - Add `new-page.html` in the `templates/` directory
   - Extend the base template: `{% extends "base.html" %}`

3. **Update navigation**
   - Add the new link to the navbar in `base.html`

### Styling

- **Custom styles**: Edit `static/css/style.css`
- **Bootstrap classes**: Use Bootstrap 5 utility classes in templates
- **Colors**: Update CSS variables for consistent theming

## 🔧 Development

### Running in Debug Mode

The application runs in debug mode by default, which enables:
- Auto-reload on code changes
- Detailed error pages
- Interactive debugger

### Adding Dependencies

1. Install new packages: `pip install package-name`
2. Update requirements: `pip freeze > requirements.txt`

## 📱 Pages

- **Home** (`/`): Welcome page with feature highlights
- **About** (`/about`): Information about the project and technologies
- **Contact** (`/contact`): Contact information and form

## 🛡️ Security Notes

- This is a development setup - not ready for production
- For production deployment, set `debug=False` and configure proper security settings
- Add environment variables for sensitive configuration
- Implement proper input validation and CSRF protection

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the project
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

If you have any questions or need help, please open an issue or contact the development team.

---

**Happy coding! 🐍✨**
