# 🤖 AI Code Review Tool for GitHub

A GitHub-integrated AI-powered code review tool that uses LLMs to analyze pull requests and highlight only high-confidence, valuable issues (security, bugs, maintainability, etc).

## ✨ Features

- Runs on GitHub Actions automatically on PRs
- Supports OpenAI and other LLMs via `ai-microcore`
- Reports only high-confidence and valuable issues
- Generates markdown summary of results
- Optional AI-generated awards for high-quality code
- Works locally or on remote URLs

## 🚀 Quickstart

### 1. GitHub Actions Setup

Add to `.github/workflows/ai-code-review.yml`:

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

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: 3.11

      - name: Install AI Code Review
        run: pip install ai-code-review==0.2.1

      - name: Run Review
        env:
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
          LLM_API_TYPE: openai
        run: ai-code-review

      - name: Attach Report
        uses: actions/upload-artifact@v4
        with:
          name: ai-code-review-results
          path: code-review-report.txt

      - name: Comment on PR
        uses: actions/github-script@v7
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

Set LLM_API_KEY value in GitHub secrets.

### 2. Local Usage

```bash
pip install ai-code-review==0.2.1
ai-code-review setup        # interactive setup
ai-code-review              # run in current Git repo
```

Review remote code:

```bash
ai-code-review remote --url https://github.com/owner/repo --branch MY_BRANCH
```

## 🔧 Configuration

Tool is configured with `.ai-code-review.toml`, including:

- LLM prompts
- issue filtering
- custom summary and report render
- award definitions

See example in `ai_code_review/.ai-code-review.toml`.

## 🛠 Development

Install dependencies:

```bash
make install
```

Run style checks:

```bash
make cs
make black
```

Run tests:

```bash
pytest
```

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## 📝 License

Licensed under the [MIT License](LICENSE)

© 2025 [Vitalii Stepanenko](mailto:mail@vitaliy.in)