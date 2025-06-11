<p align="right">
<a href="https://pypi.org/project/ai-code-review/" target="_blank"><img src="https://badge.fury.io/py/ai-code-review.svg" alt="PYPI Release"></a>
<a href="https://github.com/Nayjest/ai-code-review/actions/workflows/code-style.yml" target="_blank"><img src="https://github.com/Nayjest/ai-code-review/actions/workflows/code-style.yml/badge.svg" alt="Pylint"></a>
<a href="https://github.com/Nayjest/ai-code-review/actions/workflows/tests.yml" target="_blank"><img src="https://github.com/Nayjest/ai-code-review/actions/workflows/tests.yml/badge.svg" alt="Tests"></a>
<a href="https://github.com/Nayjest/ai-code-review/blob/main/LICENSE" target="_blank"><img src="https://img.shields.io/static/v1?label=license&message=MIT&color=d08aff" alt="License"></a>
</p>

# 🤖 AI Code Review Tool

An AI-powered GitHub code review tool that uses LLMs to detect high-confidence, high-impact issues—such as security vulnerabilities, bugs, and maintainability concerns.

## ✨ Features

- Automatically reviews pull requests via GitHub Actions
- Focuses on critical issues (e.g., bugs, security risks, design flaws)
- Posts review results as a comment on your PR
- Can be used locally; works with both local and remote Git repositories
- Optional, fun AI-generated code awards 🏆
- Easily configurable via [`.ai-code-review.toml`](https://github.com/Nayjest/ai-code-review/blob/main/ai_code_review/.ai-code-review.toml) in your repository root
- Extremely fast, parallel LLM usage
- Model-agnostic (OpenAI, Anthropic, Google, local PyTorch inference, etc.)

See code review in action: [example](https://github.com/Nayjest/ai-code-review/pull/39#issuecomment-2906968729)

## 🚀 Quickstart

### 1. Review Pull Requests via GitHub Actions

Create a `.github/workflows/ai-code-review.yml` file:

```yaml
name: AI Code Review
on: { pull_request: { types: [opened, synchronize, reopened] } }
jobs:
  review:
    runs-on: ubuntu-latest
    permissions: { contents: read, pull-requests: write } # 'write' for leaving the summary comment
    steps:
    - uses: actions/checkout@v4
      with: { fetch-depth: 0 }
    - name: Set up Python
      uses: actions/setup-python@v5
      with: { python-version: "3.13" }
    - name: Install AI Code Review tool
      run: pip install ai-code-review==0.5.0
    - name: Run AI code analysis
      env:
        LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
        LLM_API_TYPE: openai
        MODEL: "gpt-4.1"
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: |
        ai-code-review
        ai-code-review github-comment --token ${{ secrets.GITHUB_TOKEN }}
    - uses: actions/upload-artifact@v4
      with:
        name: ai-code-review-results
        path: |
          code-review-report.txt
          code-review-report.json
```

> ⚠️ Make sure to add `LLM_API_KEY` to your repository’s GitHub secrets.

💪 Done!  
PRs to your repository will now receive AI code reviews automatically. ✨  
See [GitHub Setup Guide](https://github.com/Nayjest/ai-code-review/blob/main/documentation/github_setup.md) for more details.

### 2. Run Code Analysis Locally

Install and run:

```bash
# Prerequisites: Python 3.11+
pip install ai-code-review

# One-time setup using interactive wizard (saves configuration in ~/.env.ai-code-review)
ai-code-review setup

# Run review on committed changes in current branch vs main
ai-code-review
```

To review a remote repository:

```bash
ai-code-review remote --url https://github.com/owner/repo --branch feature-branch
```

## 🔧 Configuration

Change behavior via `.ai-code-review.toml`:

- Prompt templates, filtering and post-processing using Python code snippets
- Tagging, severity, and confidence settings
- Custom AI awards for developer brilliance
- Output customization

You can override the default config by placing `.ai-code-review.toml` in your repo root.


See default configuration [here](https://github.com/Nayjest/ai-code-review/blob/main/ai_code_review/.ai-code-review.toml).

## 💻 Development Setup

Install dependencies:

```bash
make install
```

Format code and check style:

```bash
make black
make cs
```

Run tests:

```bash
pytest
```

## 🤝 Contributing

**Looking for a specific feature or having trouble?**  
Contributions are welcome! ❤️  
See [CONTRIBUTING.md](https://github.com/Nayjest/ai-code-review/blob/main/CONTRIBUTING.md) for details.

## 📝 License

Licensed under the [MIT License](https://github.com/Nayjest/ai-code-review/blob/main/LICENSE).

© 2025 [Vitalii Stepanenko](mailto:mail@vitaliy.in)
