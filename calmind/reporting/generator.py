import os
import logging
from datetime import datetime
from markdown2 import markdown

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, reports_dir="reports", templates_dir="templates"):
        self.reports_dir = reports_dir
        self.templates_dir = templates_dir
        logger.info(f"Initializing with reports_dir={self.reports_dir}, templates_dir={self.templates_dir}")
        os.makedirs(self.reports_dir, exist_ok=True)

    def _load_template(self, template_name):
        template_path = os.path.join(self.templates_dir, template_name)
        logger.info(f"Attempting to load template from {template_path}")
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Template file not found at {template_path}")
            return "<h1>Template Not Found!</h1><p>{content}</p>"

    def generate_html_report(self, user_name: str, summary_content: str) -> str:
        logger.info(f"Generating HTML report for {user_name}...")
        template = self._load_template('report_template.html')
        report_date = datetime.now().strftime('%Y-%m-%d %H:%M')
        html_content = markdown(summary_content, extras=['fenced-code-blocks', 'tables'])

        rendered_html = template.format(
            user_name=user_name,
            report_date=report_date,
            summary_content=html_content
        )

        file_name = f"{user_name.replace(' ', '_')}_calendar_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        file_path = os.path.join(self.reports_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(rendered_html)
        logger.info(f"HTML report generated: {file_path}")
        return file_path

    def generate_md_report(self, user_name: str, summary_content: str) -> str:
        logger.info(f"Generating Markdown report for {user_name}...")
        report_date = datetime.now().strftime('%Y-%m-%d %H:%M')
        md_report = f"# Calendar Summary for {user_name}\n\n"
        md_report += f"**Report Date:** {report_date}\n\n"
        md_report += "## Summary\n\n"
        md_report += summary_content

        file_name = f"{user_name.replace(' ', '_')}_calendar_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        file_path = os.path.join(self.reports_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_report)
        logger.info(f"Markdown report generated: {file_path}")
        return file_path


if __name__ == '__main__':
    # Example usage
    generator = ReportGenerator()
    sample_summary = """
    This is a **sample summary** of your calendar events.

    *   **Key Meeting:** Project Alpha Review on Monday.
    *   **Task:** Complete documentation by Friday.

    ```python
    print("Code block example")
    ```

    | Header 1 | Header 2 |
    |----------|----------|
    | Data 1   | Data 2   |
    """
    # Ensure templates/report_template.html exists for HTML generation
    # with open('templates/report_template.html', 'w') as f:
    #     f.write("""
    # <!DOCTYPE 
    # <html>
    # <head>
    #     <title>Calendar Summary for {user_name}</title>
    #     <style>
    #         body { font-family: sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: auto; padding: 20px; }
    #         h1, h2 { color: #0056b3; }
    #         pre { background-color: #eee; padding: 10px; border-radius: 5px; overflow-x: auto; }
    #         table { width: 100%; border-collapse: collapse; margin-bottom: 1em; }
    #         th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    #         th { background-color: #f2f2f2; }
    #     </style>
    # </head>
    # <body>
    #     <h1>Calendar Summary for {user_name}</h1>
    #     <p><strong>Report Date:</strong> {report_date}</p>
    #     <hr/>
    #     {summary_content}
    # </body>
    # </html>
    # ")

    # html_report_path = generator.generate_html_report("Test User", sample_summary)
    # md_report_path = generator.generate_md_report("Test User", sample_summary)

    # logger.info(f"\nGenerated HTML report at: {html_report_path}")
    # logger.info(f"Generated Markdown report at: {md_report_path}")
