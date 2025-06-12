# GitHub Setup Guide: Integrating AI Code Review with Your Repository

Automate code review for all Pull Requests using AI.  
This step-by-step guide shows how to connect [AI Code Review](https://pypi.org/project/ai-code-review/) to a GitHub repository for **continuous, automated PR reviews**.

---

## Prerequisites

- **Admin access** to your GitHub repository.
- An **API key** for your preferred language model provider (e.g., OpenAI, Google Gemini, Anthropic Claude, etc).

---

## 1. Add Your LLM API Key as a GitHub Secret

1. In your GitHub repository, go to **Settings → Secrets and variables → Actions**.
2. Click **New repository secret**.
3. Enter a name (e.g. `LLM_API_KEY`), and paste your API key value.
4. Click **Add secret**.

> **Tip:** LLM API keys allow the workflow to analyze code changes using an AI model.  
> If you don't have the necessary permission, ask a repository administrator to add the secret.

You may use a secret manager (such as HashiCorp Vault) to fetch keys at runtime, but for most teams, GitHub Secrets is the simplest approach.

---

## 2. Add the AI Code Review GitHub Actions Workflow

Create a file at `.github/workflows/ai-code-review.yml` in your repo with the following content:

```yaml
name: AI Code Review
on: { pull_request: { types: [opened, synchronize, reopened] } }
jobs:
  review:
    runs-on: ubuntu-latest
    permissions: { contents: read, pull-requests: write } # required to post review comments
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - name: Set up Python
        uses: actions/setup-python@v5
        with: { python-version: "3.13" }
      - name: Install AI Code Review tool
        run: pip install ai-code-review==0.6.0
      - name: Run AI code review
        env:
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
          LLM_API_TYPE: openai
          MODEL: "gpt-4.1"
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          ai-code-review
          ai-code-review github-comment --token "$GITHUB_TOKEN"
      - uses: actions/upload-artifact@v4
        with:
          name: ai-code-review-results
          path: |
            code-review-report.md
            code-review-report.json
```

#### Notes

- **Set `LLM_API_TYPE` and `MODEL` as needed** for your chosen LLM provider (see below for links).
- If you used a different secret name in step 1, update `${{ secrets.GITHUB_TOKEN }}` accordingly.
- This workflow will:
  - Analyze all pull requests using an LLM,
  - Post a review summary as a PR comment,
  - Upload code review reports as workflow artifacts for you to download if needed.

#### Example .env setups for other language model providers:

- [Mistral](https://github.com/Nayjest/ai-microcore/blob/main/.env.mistral.example)
- [Gemini via Google AI Studio](https://github.com/Nayjest/ai-microcore/blob/main/.env.gemini.example)
- [Gemini via Google Vertex](https://github.com/Nayjest/ai-microcore/blob/main/.env.google-vertex-gemini.example) *(add `pip install vertexai` to your workflow)*
- [Anthropic Claude](https://github.com/Nayjest/ai-microcore/blob/main/.env.anthropic.example)

---

## Done! See AI Review Results on Pull Requests

Whenever a PR is opened or updated, you'll see an **AI-generated code review comment** in the PR discussion.

**Tips:**
- To trigger a review for older existing PRs, merge the `main` branch containing `.github/workflows/ai-code-review.yml`
- You may close and reopen the PR to trigger the review again.
- Download full review artifacts from the corresponding GitHub Actions workflow run.

---

## Customize Review if Needed


- Create a `.ai-code-review.toml` file at your repository root to override [default configuration](https://github.com/Nayjest/ai-code-review/blob/main/ai_code_review/.ai-code-review.toml).
- You can adjust prompts, filtering, report templates, issue criteria, and more.

## Troubleshooting

- **Not seeing a PR comment?**
  1. On the PR page, click the status icon near the latest commit hash.
  2. Click **Details** to open the Actions run.
  3. Review logs for any errors (e.g., API key missing, token issues).

Example:

![Workflow Diagnostics](img.png)

---

## Additional Resources

- More usage documentation: [README.md](../README.md)
- For help or bug reports, [open an issue](https://github.com/Nayjest/ai-code-review/issues)

---

**Enjoy fast, LLM-powered pull request reviews and safer merges! 🚀**