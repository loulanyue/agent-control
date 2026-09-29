# Contributing to Agent Control

First off, thank you for considering contributing to **Agent Control**! It's people like you that make open source such a fantastic community.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Development Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/loulanyue/agent-control.git
   cd agent-control
   ```

2. **Create a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install pytest ruff
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   ```

4. **Run Tests**
   ```bash
   pytest
   ```

5. **Run the Linter**
   ```bash
   ruff check .
   ```

## Pull Request Guidelines

1. Create a branch from `main`: `git checkout -b feature/my-new-feature`
2. Follow PEP 8 and modern Python practices.
3. Add unit tests for any new features or bug fixes.
4. Ensure all existing tests pass.
5. Submit a descriptive Pull Request.
