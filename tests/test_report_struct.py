import json
import os
from gito.bootstrap import bootstrap
from gito.report_struct import Report, Issue


def test_report_plain_issues():
    bootstrap()
    report = Report(
        issues={
            "file1.py": [
                {
                    "title": "Bug 1",
                    "details": "desc",
                    "tags": ["bug"],
                    "severity": 1,
                    "confidence": 1,
                    "affected_lines": [],
                }
            ],
            "file2.py": [
                {
                    "title": "Bug 2",
                    "details": "desc",
                    "tags": ["bug"],
                    "severity": 2,
                    "confidence": 1,
                    "affected_lines": [],
                }
            ],
        }
    )
    issues = report.plain_issues
    assert isinstance(issues, list)
    assert len(issues) == 2
    assert all(isinstance(i, Issue) for i in issues)
    assert report.total_issues == 2
    assert issues[0].id == 1
    assert issues[1].id == 2
    # test field transfer
    assert issues[0].file == "file1.py"
    assert issues[1].file == "file2.py"


def test_report_save_load(tmp_path):
    bootstrap()
    data = {
        "issues": {
            "file.py": [
                {
                    "title": "Bug",
                    "details": "desc",
                    "tags": ["bug"],
                    "severity": 1,
                    "confidence": 1,
                    "affected_lines": [],
                }
            ]
        },
        "summary": "SUMMARY",
        "number_of_processed_files": 2,
    }
    file_name = tmp_path / "report.json"
    report = Report(**data)
    report.save(file_name)
    assert os.path.exists(file_name)
    # test it's valid JSON
    with open(file_name, "r") as f:
        loaded = json.load(f)
    assert loaded["summary"] == "SUMMARY"
    assert loaded["number_of_processed_files"] == 2
    # test reload with .load
    loaded_report = Report.load(file_name)
    assert loaded_report.summary == "SUMMARY"
    assert loaded_report.number_of_processed_files == 2
    assert loaded_report.total_issues == 1
    assert loaded_report.issues["file.py"][0].title == "Bug"


def test_issue_affected_lines_init():
    bootstrap()
    D = {
        "id": "x",
        "title": "T",
        "tags": [],
        "file": "X.py",
        "affected_lines": [
            {
                "start_line": 2,
                "end_line": 3,
                "proposal": "foo",
                "affected_code": "code",
                # file field should be auto set to parent file!
            }
        ],
    }
    issue = Issue(**D)
    line = issue.affected_lines[0]
    assert isinstance(line, Issue.AffectedCode)
    assert line.file == "X.py"
    assert line.proposal == "foo"
    assert line.start_line == 2
    assert line.syntax_hint == "python"
