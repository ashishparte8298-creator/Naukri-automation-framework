# Naukri Pytest POM Flow

This package runs the complete Naukri job search and application automation using
Pytest and Page Object Model.

## Complete Flow

1. Fetch jobs from Naukri for configured locations.
2. Insert only new job URLs into Excel.
3. Filter Excel rows by relevant job-title keywords.
4. Remove irrelevant jobs from Excel.
5. Reload filtered Excel jobs.
6. Login to Naukri.
7. Apply jobs one by one.
8. Skip jobs with final statuses such as Applied, Already Applied, Submit, Apply Button Not Found, Status Unclear, or Error.
9. Update Excel after every job.

## Run Directly

```bash
.venv/bin/python Naukari/Naukari_Job.py
```

## Run With Pytest

```bash
.venv/bin/python -m pytest Naukari/tests/test_naukri_apply_flow.py -s
```

## Main Files

- `Naukari/Naukari_Job.py` - direct runner
- `Naukari/naukri_flow.py` - complete flow orchestration
- `Naukari/pages/login_page.py` - login page object
- `Naukari/pages/search_page.py` - search and job extraction page object
- `Naukari/pages/job_page.py` - apply/status page object
- `Naukari/pages/chatbot_page.py` - chatbot page object
- `Naukari/utils/excel_utils.py` - Excel repository
- `Naukari/tests/conftest.py` - Pytest Selenium driver fixture
- `Naukari/tests/test_naukri_apply_flow.py` - Pytest flow test
