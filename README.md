# PPT Generator

A web application that generates PowerPoint presentations from URLs by capturing screenshots of web pages.

## Features

- Capture screenshots from any URL
- Generate PowerPoint presentations with multiple slides
- Modern and responsive user interface
- Customizable number of slides
- Clean and professional presentation layout

## Prerequisites

- Python 3.8 or higher
- Chrome browser installed

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ppt-generator.git
cd ppt-generator
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

Note: The application uses webdriver-manager to automatically handle ChromeDriver installation, so you don't need to manually install it.

## Usage

You can run the application in several ways:

### Using an IDE (Recommended)
1. Open the project in your IDE (e.g., Cursor, VS Code, PyCharm)
2. Open `app/main.py`
3. Click the "Run" button or press F5
4. The application will start and be available at http://localhost:8000

### Using the Command Line
1. Start the application (from the project root directory):
```bash
uvicorn app.main:app --reload
```
or
```bash
python -m uvicorn app.main:app --reload
```

2. Open your web browser and navigate to `http://localhost:8000`

3. Enter a URL and the number of slides you want to generate

4. Click "Generate Presentation" and wait for the download to complete

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
```

### Linting

```bash
pylint app/
flake8
mypy app/
```

## Project Structure

```
ppt-generator/
├── app/
│   ├── __init__.py        # Package initialization
│   ├── api.py             # API endpoints
│   ├── main.py            # Main FastAPI application
│   ├── services/          # Business logic services
│   │   ├── __init__.py
│   │   ├── screenshot_service.py
│   │   └── pptx_service.py
│   ├── static/           # Static files (CSS, JS)
│   │   ├── css/
│   │   └── js/
│   └── templates/        # HTML templates
├── tests/                # Test files
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 