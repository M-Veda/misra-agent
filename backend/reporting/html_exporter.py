from pathlib import Path


class HTMLExporter:
    """
    Exports analysis results as an HTML report.
    """

    def export(
        self,
        violations,
        execution_summary,
        output_file,
    ):

        html = [
            "<html>",
            "<head>",
            "<title>MISRA Analysis Report</title>",
            "<style>",
            "body{font-family:Arial;margin:40px;}",
            "table{border-collapse:collapse;width:100%;}",
            "th,td{border:1px solid #ccc;padding:8px;}",
            "th{background:#f2f2f2;}",
            ".Required{color:red;font-weight:bold;}",
            ".Advisory{color:orange;font-weight:bold;}",
            "</style>",
            "</head>",
            "<body>",
        ]

        html.append(
            "<h1>MISRA Analysis Report</h1>"
        )

        html.append("<h2>Summary</h2>")

        html.append("<ul>")

        for key, value in execution_summary.items():

            html.append(
                f"<li><b>{key}</b>: {value}</li>"
            )

        html.append("</ul>")

        html.append(
            "<h2>Violations</h2>"
        )

        html.append(
            "<table>"
        )

        html.append(
            "<tr>"
            "<th>Rule</th>"
            "<th>Severity</th>"
            "<th>Line</th>"
            "<th>Description</th>"
            "</tr>"
        )

        for violation in violations:

            html.append(
                "<tr>"
                f"<td>{violation.rule_id}</td>"
                f"<td class='{violation.severity}'>"
                f"{violation.severity}</td>"
                f"<td>{violation.line_number}</td>"
                f"<td>{violation.description}</td>"
                "</tr>"
            )

        html.append("</table>")

        html.extend(
            [
                "</body>",
                "</html>",
            ]
        )

        Path(output_file).write_text(
            "\n".join(html),
            encoding="utf-8",
        )