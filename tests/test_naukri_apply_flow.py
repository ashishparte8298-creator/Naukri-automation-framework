import pytest

from Naukari.naukri_flow import NaukriApplicationFlow


def test_naukri_job_apply_flow(driver):
    """
    Test the real Naukri job application flow.
    Runs the complete automation workflow and verifies summary is generated.
    """
    flow = NaukriApplicationFlow(driver)
    summary = flow.run()

    assert summary is not None
