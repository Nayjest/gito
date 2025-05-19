# 🤖 AI Code Review Tool

An AI-powered code review tool for GitHub that uses LLMs to analyze pull requests and highlight only high-confidence and high-impact issues (e.g., security, bugs, maintainability).

## ✨ Features

- Automatic GitHub PR reviews via GitHub Actions
- Filters only significant issues (e.g., bugs, security concerns)
- Posts results as comments in PRs
- Supports both local and remote repositories
- Optional humorous AI-generated code awards
- Customizable via `.ai-code-review.toml`

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
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install ai-code-review==0.2.1
      - name: Run AI review
        env:
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
          LLM_API_TYPE: openai
        run: ai-code-review
      - uses: actions/upload-artifact@v4
        with:
          name: ai-code-review-results
          path: code-review-report.txt
      - uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const body = fs.existsSync('code-review-report.txt')
              ? fs.readFileSync('code-review-report.txt', 'utf8')
              : 'No review report found.';
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body,
            });
```

> ⚠️ Make sure `LLM_API_KEY` is set in your repo's GitHub secrets.

### 2. Local Review

Install and run the tool:

```bash
pip install ai-code-review
ai-code-review setup
ai-code-review
```

To review a remote repo:

```bash
ai-code-review remote --url https://github.com/owner/repo --branch branch-name
```

## 🔧 Configuration

Review behavior is defined in `.ai-code-review.toml`, including:

- LLM prompts
- Filtering by severity and confidence
- Award descriptions
- Markdown output formatting

You may override this configuration by placing a `.ai-code-review.toml` file in your project root.

## 💻 Development

Set up your environment:

```bash
make install
```

Run code checks and formatting:

```bash
make cs
make black
```

Run tests:

```bash
pytest
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md)

## 📝 License

Licensed under the [MIT License](LICENSE)

© 2025 [Vitalii Stepanenko](mailto:mail@vitaliy.in)