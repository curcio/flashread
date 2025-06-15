# Contributing to FlashRead

Thank you for your interest in contributing to FlashRead! This document provides guidelines for setting up the development environment and contributing to the project.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git

### Setting up the Development Environment

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd flashread
   ```

2. **Install runtime dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install development dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Set up pre-commit hooks:**
   ```bash
   pre-commit install
   ```

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality and consistency. The following hooks are configured:

- **black**: Python code formatter (line length: 88)
- **isort**: Import sorter (compatible with black)
- **autoflake**: Removes unused imports and variables
- **trailing-whitespace**: Removes trailing whitespace
- **end-of-file-fixer**: Ensures files end with a newline
- **check-added-large-files**: Prevents committing large files (>500kB)
- **check-yaml**: Validates YAML syntax
- **check-json**: Validates JSON syntax
- **check-merge-conflict**: Checks for merge conflict markers
- **check-case-conflict**: Checks for case conflicts

### Running Pre-commit Manually

To run all pre-commit hooks on all files:
```bash
pre-commit run --all-files
```

To run a specific hook:
```bash
pre-commit run black --all-files
pre-commit run isort --all-files
pre-commit run autoflake --all-files
```

### Code Style Guidelines

- **Line length**: 88 characters (black default)
- **Import sorting**: Use isort with black profile
- **Formatting**: Use black for consistent formatting
- **Unused imports**: Will be automatically removed by autoflake

### Testing Your Changes

Before submitting a pull request:

1. **Run the application:**
   ```bash
   python flashread.py run
   ```

2. **Test the settings panel functionality:**
   - Click the cogwheel icon to open settings
   - Test alphabet letter toggles
   - Test case selection radio buttons
   - Test hyphenation checkbox
   - Test sliders for word length

3. **Ensure pre-commit hooks pass:**
   ```bash
   pre-commit run --all-files
   ```

### Submitting Changes

1. Create a feature branch from main
2. Make your changes
3. Ensure all pre-commit hooks pass
4. Test your changes thoroughly
5. Commit with descriptive messages
6. Push your branch and create a pull request

### Project Structure

```
flashread/
├── src/                    # Source code
│   ├── flashcard_app.py   # Main application logic
│   ├── text_processor.py  # Text processing utilities
│   ├── cli.py             # Command-line interface
│   └── utils.py           # Utility functions
├── data/                  # Generated vocabulary data
├── corpus/                # Text corpus files
├── requirements.txt       # Runtime dependencies
├── requirements-dev.txt   # Development dependencies
└── .pre-commit-config.yaml # Pre-commit configuration
```

### Common Issues

**Pre-commit hooks fail:**
- Run `pre-commit run --all-files` to see specific issues
- Most formatting issues are auto-fixed by the hooks
- Re-stage files after auto-fixes and commit again

**Import errors:**
- Ensure you're running from the project root
- Check that all dependencies are installed

### Getting Help

If you encounter issues or have questions about contributing, please:
1. Check existing issues in the repository
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce
