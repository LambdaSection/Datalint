"""
Reporting modules with separate implementations for each format (ISP, SRP).
"""
import json
from typing import List
from jinja2 import Template
from datalint.engine.base import Formatter, ValidationResult

class TextFormatter(Formatter):
    """
    Formats validation results as human-readable text for terminal.
    SRP: Handles only text formatting.
    """
    
    def format(self, results: List[ValidationResult]) -> str:
        lines = []
        lines.append("🔍 DataLint Validation Report")
        lines.append("=" * 40)

        total_checks = len(results)
        passed_checks = sum(1 for r in results if r.passed)
        failed_checks = total_checks - passed_checks

        lines.append(f"Summary: {passed_checks} passed, {failed_checks} warnings/failed")
        lines.append("")

        for result in results:
            icon = "✅" if result.passed else ("⚠️" if result.status == "warning" else "❌")
            lines.append(f"{icon} {result.name.replace('_', ' ').title()}")

            if not result.passed:
                for issue in result.issues:
                    lines.append(f"  • {issue}")

                for rec in result.recommendations:
                    lines.append(f"  💡 {rec}")

            lines.append("")

        if failed_checks > 0:
            lines.append("💡 Tip: Address failed checks before training ML models")
        else:
            lines.append("🎉 Dataset looks good for ML training!")

        return "\n".join(lines)


class JsonFormatter(Formatter):
    """
    Formats validation results as JSON for CI/CD integration.
    SRP: Handles only JSON formatting.
    """
    
    def format(self, results: List[ValidationResult]) -> str:
        output = {
            'summary': {
                'total': len(results),
                'passed': sum(1 for r in results if r.passed),
                'failed': sum(1 for r in results if not r.passed)
            },
            'results': [r.to_dict() for r in results]
        }
        return json.dumps(output, indent=2)


class HtmlFormatter(Formatter):
    """
    Formats validation results as HTML document.
    SRP: Handles only HTML formatting.
    """
    
    TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DataLint Validation Report</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; max-width: 800px; margin: 0 auto; padding: 20px; color: #333; }
            .header { text-align: center; margin-bottom: 40px; }
            .summary { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; display: flex; justify-content: space-around; }
            .stat { text-align: center; }
            .stat-number { font-size: 24px; font-weight: bold; display: block; }
            .check-card { border: 1px solid #e1e4e8; border-radius: 8px; margin-bottom: 20px; overflow: hidden; }
            .check-header { padding: 15px; background: #fff; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #eee; }
            .passed .check-header { border-left: 5px solid #28a745; }
            .failed .check-header { border-left: 5px solid #dc3545; }
            .warning .check-header { border-left: 5px solid #ffc107; }
            .issues { background: #fff5f5; padding: 15px; }
            .recommendations { background: #e6fffa; padding: 15px; }
            ul { margin: 0; padding-left: 20px; }
            li { margin-bottom: 5px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔍 DataLint Report</h1>
        </div>
        
        <div class="summary">
            <div class="stat">
                <span class="stat-number">{{ summary.total }}</span>
                <span>Total Checks</span>
            </div>
            <div class="stat">
                <span class="stat-number" style="color: #28a745">{{ summary.passed }}</span>
                <span>Passed</span>
            </div>
            <div class="stat">
                <span class="stat-number" style="color: #dc3545">{{ summary.failed }}</span>
                <span>Failed</span>
            </div>
        </div>

        {% for result in results %}
        <div class="check-card {{ result.status }}">
            <div class="check-header">
                <h3>{{ result.name|replace('_', ' ')|title }}</h3>
                <span class="status-badge">{{ result.status|upper }}</span>
            </div>

            {% if not result.passed %}
            <div class="issues">
                <strong>Issues:</strong>
                <ul>
                {% for issue in result.issues %}
                    <li>{{ issue }}</li>
                {% endfor %}
                </ul>
            </div>

            <div class="recommendations">
                <strong>💡 Recommendations:</strong>
                <ul>
                {% for rec in result.recommendations %}
                    <li>{{ rec }}</li>
                {% endfor %}
                </ul>
            </div>
            {% endif %}
        </div>
        {% endfor %}
    </body>
    </html>
    """
    
    def format(self, results: List[ValidationResult]) -> str:
        summary = {
            'total': len(results),
            'passed': sum(1 for r in results if r.passed),
            'failed': sum(1 for r in results if not r.passed)
        }
        template = Template(self.TEMPLATE)
        return template.render(results=results, summary=summary)


class FormatterFactory:
    """
    Simple factory to get the right formatter (OCP - easy to add new formats).
    """
    @staticmethod
    def get_formatter(format_name: str) -> Formatter:
        formatters = {
            'text': TextFormatter,
            'json': JsonFormatter,
            'html': HtmlFormatter
        }
        formatter_class = formatters.get(format_name.lower())
        if not formatter_class:
            raise ValueError(f"Unknown format: {format_name}")
        return formatter_class()