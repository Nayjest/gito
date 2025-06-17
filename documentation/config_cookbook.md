# Configuration Cookbook

This document provides a comprehensive guide on how to configure and tune [Gito AI Code Reviewer](https://pypi.org/project/gito.bot/) using project-specific configuration.

## Configuration file
When run locally or via GitHub actions, [Gito](https://pypi.org/project/gito.bot/)
looks for `.gito/config.toml` file in the repository root directory.  
Then it merges project-specific configuration (if exists) with the
[default one](https://github.com/Nayjest/Gito/blob/main/gito/config.toml).  
This allows you to customize the behavior of the AI code review tool according to your project's needs.


## How to add custom code review rule?
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
