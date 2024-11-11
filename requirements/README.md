# Requirements

This directory contains different requirement files for different environments:

## base.txt
Contains the core requirements needed for the application to run in any environment.

## development.txt
Contains packages needed for development, including:
- Debugging tools
- Testing tools
- Code quality checkers
- Documentation generators

Install with:
```bash
pip install -r requirements/development.txt
```

## production.txt
Contains packages needed for production deployment, including:
- Production servers
- Monitoring tools
- Performance optimizers
- Security enhancements

Install with:
```bash
pip install -r requirements/production.txt
```

Note: Both development.txt and production.txt include base.txt requirements.