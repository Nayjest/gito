# 🤖 AI Code Review Tool

AI-powered GitHub code review tool that leverages LLMs to highlight only high-confidence, high-impact issues—e.g., security flaws, bugs, or maintainability concerns.

## ✨ Features

- Automatic PR reviews via GitHub Actions
- Highlights only significant issues (e.g., bugs, security, maintainability)
- Posts results as a PR comment
- Supports both local and remote repositories
- Optional fun AI-generated code awards
- Fully configurable via `.ai-code-review.toml`

## 🚀 Quickstart

### 1. GitHub PR Review (via GitHub Actions)

Create `.github/workflows/ai-code-review.yml`:

```yaml
name: AI Code Review
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write

    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0
    - name: Set up Python 3.11
      uses: actions/setup-python@v5
      with:
        python-version: "3.11"
    - name: Install AI Code Review tool
      run: pip install ai-code-review==0.2.1
    - name: Run AI code review
      env:
        LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
        LLM_API_TYPE: openai
        MODEL: "gpt-4.1"
      run: ai-code-review
    - uses: actions/upload-artifact@v4
      with:
        name: ai-code-review-results
        path: code-review-report.txt
    - name: Comment on PR with review
      uses: actions/github-script@v7
      with:
        script: |
          await github.rest.issues.createComment({
            owner: context.repo.owner,
            repo: context.repo.repo,
            issue_number: context.issue.number,
            body: require('fs').readFileSync('code-review-report.txt', 'utf8')
          });
```

> ⚠️ Make sure to add `LLM_API_KEY` to your repo’s GitHub secrets.

### 2. Local Review

Install and run locally:

```bash
# Prerequisites: Python 3.11+, pip
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

Customize review behavior via `.ai-code-review.toml`:

- LLM prompt and behavior
- Filtering logic (severity & confidence)
- Award definitions
- Output customization

You can override the default config by placing `.ai-code-review.toml` in your repo root.

See default configuration here: [.ai-code-review.toml](https://github.com/Nayjest/github-ai-code-review/blob/main/ai_code_review/.ai-code-review.toml).
## 💻 Development Setup

Install dependencies:

```bash
make install
```

Check & format code:

```bash
make cs
make black
```

Run tests:

```bash
pytest
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📝 License

Licensed under the [MIT License](LICENSE)

© 2025 [Vitalii Stepanenko](mailto:mail@vitaliy.in)