<p align="right">
<a href="https://pypi.org/project/ai-code-review/" target="_blank"><img src="https://badge.fury.io/py/ai-code-review.svg" alt="PYPI Release"></a>
<a href="https://github.com/Nayjest/ai-code-review/actions/workflows/code-style.yml" target="_blank"><img src="https://github.com/Nayjest/ai-code-review/actions/workflows/code-style.yml/badge.svg" alt="Pylint"></a>
<a href="https://github.com/Nayjest/ai-code-review/actions/workflows/tests.yml" target="_blank"><img src="https://github.com/Nayjest/ai-code-review/actions/workflows/tests.yml/badge.svg" alt="Tests"></a>
<img src="https://github.com/Nayjest/ai-code-review/blob/main/coverage.svg" alt="Code Coverage">
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
      run: pip install ai-code-review~=1.0
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
          code-review-report.md
          code-review-report.json
```

> ⚠️ Make sure to add `LLM_API_KEY` to your repository’s GitHub secrets.

💪 Done!  
PRs to your repository will now receive AI code reviews automatically. ✨  
See [GitHub Setup Guide](https://github.com/Nayjest/ai-code-review/blob/main/documentation/github_setup.md) for more details.

### 2. Running Code Analysis Locally

#### Initial Local Setup

**Prerequisites:** [Python](https://www.python.org/downloads/) 3.11 / 3.12 / 3.13  

**Step1:** Install [ai-code-review](https://github.com/Nayjest/ai-code-review) using [pip](https://en.wikipedia.org/wiki/Pip_(package_manager)).
```bash
pip install ai-code-review
```

> **Troubleshooting:**  
> pip may be also available via cli as `pip3` depending on your Python installation.

**Step2:** Perform initial setup

The following command will perform one-time setup using an interactive wizard.
You will be prompted to enter LLM configuration details (API type, API key, etc).
Configuration will be saved to ~/.env.ai-code-review.

```bash
ai-code-review setup
```

> **Troubleshooting:**  
> On some systems, `ai-code-review` command may not became available immediately after installation.  
> Try restarting your terminal or running `python -m ai_code_review` instead.


#### Perform your first AI code review locally

**Step1:** Navigate to your repository root directory.  
**Step2:** Switch to the branch you want to review.  
**Step3:** Run following command
```bash
ai-code-review
```

> **Note:** This will analyze the current branch against the repository main branch by default.  
> Files that are not staged for commit will be ignored.  
> See `ai-code-review --help` for more options.

**Reviewing remote repository**

```bash
ai-code-review remote git@github.com:owner/repo.git <FEATURE_BRANCH>..<MAIN_BRANCH>
```
Use interactive help for details:
```bash
ai-code-review remote --help
```

## 🔧 Configuration

Change behavior via `.ai-code-review.toml`:

- Prompt templates, filtering and post-processing using Python code snippets
- Tagging, severity, and confidence settings
- Custom AI awards for developer brilliance
- Output customization

You can override the default config by placing `.ai-code-review.toml` in your repo root.


See default configuration [here](https://github.com/Nayjest/ai-code-review/blob/main/ai_code_review/.ai-code-review.toml).

More details can be found in [📖 Configuration Cookbook](https://github.com/Nayjest/ai-code-review/blob/main/documentation/config_cookbook.md)

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
