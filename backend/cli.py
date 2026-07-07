import argparse
from pathlib import Path

from pipeline.analysis_pipeline import AnalysisPipeline
from reporting.json_exporter import JSONExporter
from reporting.html_exporter import HTMLExporter
from version import (
    __version__,
    PROJECT_NAME,
)


def build_parser():

    parser = argparse.ArgumentParser(
        prog="misra-analyzer",
        description="MISRA C:2012 Static Analyzer",
    )

    parser.add_argument(
        "source",
        help="C source file or directory",
    )

    parser.add_argument(
        "--json",
        help="JSON report output file",
    )

    parser.add_argument(
        "--html",
        help="HTML report output file",
    )

    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically apply available fixes",
    )

    parser.add_argument(
        "--profile",
        default="full",
        choices=(
            "full",
            "fast",
            "semantic",
        ),
        help="Analysis profile",
    )

    parser.add_argument(
        "--rule",
        help="Run only one rule (example: 8.1)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"{PROJECT_NAME} {__version__}",
    )

    return parser


def main():

    parser = build_parser()

    args = parser.parse_args()

    print("=" * 60)
    print(PROJECT_NAME)
    print(f"Version : {__version__}")
    print("=" * 60)

    print(f"Profile : {args.profile}")

    pipeline = AnalysisPipeline()

    source_path = Path(args.source)

    all_violations = []
    analyzed_files = []

    #
    # Directory mode
    #
    if source_path.is_dir():

        for c_file in source_path.rglob("*.c"):

            analyzed_files.append(str(c_file))

            violations = pipeline.analyze_file(
                str(c_file),
                rule_ids=[args.rule] if args.rule else None,
                profile=args.profile,
            )

            all_violations.extend(violations)

    #
    # Single file mode
    #
    else:

        analyzed_files.append(str(source_path))

        all_violations = pipeline.analyze_file(
            str(source_path),
            rule_ids=[args.rule] if args.rule else None,
            profile=args.profile,
        )

    #
    # Auto fix mode only works for single file
    #
    if args.fix:

        if source_path.is_dir():

            print()
            print("Automatic fixing is only supported for single files.")

        else:

            source = source_path.read_text(
                encoding="utf-8",
            )

            result = pipeline.apply_fixes(
                source,
                all_violations,
            )

            fixed_source = result["source"]
            applied = result["applied"]

            output_path = source_path.with_suffix(
                ".fixed.c"
            )

            output_path.write_text(
                fixed_source,
                encoding="utf-8",
            )

            print()
            print(f"Applied fixes : {len(applied)}")
            print(f"Output file   : {output_path}")

    summary = pipeline.execution_summary()

    print()
    print("=" * 60)
    print("MISRA ANALYSIS COMPLETE")
    print("=" * 60)

    if source_path.is_dir():

        print(f"Directory   : {args.source}")
        print(f"Files       : {len(analyzed_files)}")

    else:

        print(f"File        : {args.source}")

    print(f"Violations  : {len(all_violations)}")
    print(f"Rules Run   : {summary.get('executed', 0)}")
    print(
        f"Duration    : "
        f"{summary.get('duration_seconds', 0)} s"
    )

    print("=" * 60)

    if args.json:

        JSONExporter().export(
            all_violations,
            summary,
            args.json,
        )

        print(
            f"JSON report written to {args.json}"
        )

    if args.html:

        HTMLExporter().export(
            all_violations,
            summary,
            args.html,
        )

        print(
            f"HTML report written to {args.html}"
        )


if __name__ == "__main__":
    main()