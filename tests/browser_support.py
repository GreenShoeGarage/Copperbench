"""Use Playwright's installed Chromium, or an explicit local executable override."""
from pathlib import Path
import os
from playwright.sync_api import Playwright, Browser


def launch_chromium(playwright: Playwright) -> Browser:
    options = {"headless": True}
    executable = os.environ.get("CHROMIUM_EXECUTABLE")
    if executable:
        if not Path(executable).is_file():
            raise RuntimeError(f"CHROMIUM_EXECUTABLE does not exist: {executable}")
        options["executable_path"] = executable
    # The browser harness loads only the repository's own test content.
    # Do not change administrator policies to make navigation tests pass.
    return playwright.chromium.launch(**options)
