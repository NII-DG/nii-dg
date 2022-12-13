import pytest
from py.xml import html


def pytest_html_results_table_header(cells) -> None:
    cells.insert(2, html.th("Description"))


def pytest_html_results_table_row(report, cells) -> None:
    cells.insert(2, html.td(report.description))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call) -> None:
    outcome = yield
    report = outcome.get_result()
    report.description = str(item.function.__doc__)