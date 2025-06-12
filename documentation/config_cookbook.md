# Configuration Cookbook

This document provides a comprehensive guide on how to configure and tune the [AI Code Review](https://pypi.org/project/ai-code-review/) using project-specific configuration.

## Configuration file
When runned locally or via GitHub actions, [AI Code Review](https://pypi.org/project/ai-code-review/)
looks for `.ai-code-review.toml` file in the repository root directory.  
Then it merges project-specific configuration (if exists) with the
[default one](https://github.com/Nayjest/ai-code-review/blob/main/ai_code_review/.ai-code-review.toml).  
This allows you to customize the behavior of the AI code review tool according to your project's needs.


## How to add custom code rewiew rule?
```toml
[prompt_vars]
requirements = """
- Issue descriptions should be written on Ukrainian language
  (Опис виявлених проблем має бути Українською мовою)
"""
# this instruction affects only summary text generation, not the issue detection itself
summary_requirements = """
- Rate the code quality of introduced changes on a scale from 1 to 100, where 1 is the worst and 100 is the best.
"""
