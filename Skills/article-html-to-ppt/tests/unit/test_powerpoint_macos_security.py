from __future__ import annotations

from pathlib import Path

from ppt_qa.renderers import powerpoint_macos


def test_export_command_passes_paths_as_argv_not_applescript_source() -> None:
    builder = getattr(powerpoint_macos, "_powerpoint_export_command", None)
    assert callable(builder), "renderer must expose a safe command builder"

    pptx_path = Path('/tmp/report" & do shell script "touch /tmp/pwned" & ".pptx')
    pdf_path = Path('/tmp/output" & error "unsafe" & ".pdf')

    command = builder(pptx_path, pdf_path)

    assert command[:2] == ["osascript", "-e"]
    assert "on run argv" in command[2]
    assert str(pptx_path) not in command[2]
    assert str(pdf_path) not in command[2]
    assert command[-2:] == [str(pptx_path), str(pdf_path)]
