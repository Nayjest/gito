# 🤖 AI Code Review Tool

An AI-powered GitHub code review tool that uses LLMs to detect high-confidence, high-impact issues—such as security vulnerabilities, bugs, and maintainability concerns.

## ✨ Features

- Automatically reviews pull requests via GitHub Actions
- Focuses on critical issues (e.g., bugs, security risks, design flaws)
- Posts review results as a comment on your PR
- Can be used locally; works with both local and remote Git repositories
- Optional, fun AI-generated code awards 🏆
- Easily configurable via [`.ai-code-review.toml`](ai_code_review/.ai-code-review.toml)
- Simple and minimal core logic—only 19 lines of code! ([main()](ai_code_review/ai_code_review.py))
- Extremely fast, parallel LLM usage
- Model-agnostic (OpenAI, Anthropic, Google, local PyTorch inference, etc.)

## 🚀 Quickstart

### 1. Review Pull Requests via GitHub Actions

Create a `.github/workflows/ai-code-review.yml` file:

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

> ⚠️ Make sure to add `LLM_API_KEY` to your repository’s GitHub secrets.

### 2. Run Locally

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


See default configuration [here](ai_code_review/.ai-code-review.toml).

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

We ❤️ contributions! See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📝 License

Licensed under the [MIT License](LICENSE).

© 2025 [Vitalii Stepanenko](mailto:mail@vitaliy.in)