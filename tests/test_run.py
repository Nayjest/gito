from typer.testing import CliRunner
from unittest.mock import AsyncMock
from ai_code_review.cli import app_no_subcommand, app
runner = CliRunner()


def test_review_command_calls_review(monkeypatch):
    mock_review = AsyncMock()
    monkeypatch.setattr("ai_code_review.cli.review", mock_review)
    result = runner.invoke(
        app,
        ["review", "--what", "HEAD", "--against", "HEAD~1"],
    )
    assert result.exit_code == 0
    mock_review.assert_awaited_once_with(
        what="HEAD",
        against="HEAD~1",
        filters="",
        out_folder=None,
        use_merge_base=True,
    )


def test_calls_review(monkeypatch):
    mock_review = AsyncMock()
    monkeypatch.setattr("ai_code_review.cli.review", mock_review)
    result = runner.invoke(
        app_no_subcommand,
        ["HEAD", "--filters", "*.py,*.md"],
    )
    assert result.exit_code == 0
    mock_review.assert_awaited_once_with(
        what="HEAD",
        against=None,
        filters="*.py,*.md",
        out_folder=None,
        use_merge_base=True,
    )
