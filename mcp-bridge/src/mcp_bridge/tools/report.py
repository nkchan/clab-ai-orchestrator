"""Report generation tools."""

import logging
import pathlib

logger = logging.getLogger(__name__)

class ReportTools:
    """Tools for saving investigation reports."""

    def __init__(self, reports_dir: str = "/app/reports"):
        self.reports_dir = pathlib.Path(reports_dir)
        # Ensure directory exists (if mounted, it should, but just in case)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, filename: str, content: str) -> str:
        """Save a Markdown report to the reports directory.

        Args:
            filename: Name of the report file (e.g., 'bgp_investigation.md').
            content: Markdown content of the report.

        Returns:
            Success message with the saved path.
        """
        # Sanitize filename
        safe_filename = pathlib.Path(filename).name
        if not safe_filename.endswith(".md"):
            safe_filename += ".md"

        filepath = self.reports_dir / safe_filename
        
        try:
            filepath.write_text(content, encoding="utf-8")
            logger.info(f"Saved report to {filepath}")
            return f"Report successfully saved to {filepath}"
        except Exception as e:
            logger.error(f"Failed to save report {filepath}: {e}")
            return f"Error: Failed to save report: {e}"
