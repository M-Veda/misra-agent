from datetime import datetime
from pathlib import Path

from utils.logger import logger


class ClangParser:
    """
    Lightweight parser wrapper.

    Current implementation:
        - Reads C source
        - Produces parser metadata
        - Serves as the interface for future libclang integration

    The public API intentionally matches what the rest of the
    project expects so that a real Clang parser can later replace
    this implementation without changing other modules.
    """

    def parse(self, file_path):
        started = datetime.now()

        path = Path(file_path)

        if not path.exists():
            logger.error(
                "Source file not found: %s",
                file_path,
            )
            raise FileNotFoundError(file_path)

        try:
            source = path.read_text(
                encoding="utf-8"
            )

        except UnicodeDecodeError as exc:
            logger.exception(
                "UTF-8 decoding failed."
            )
            raise RuntimeError(
                "Unable to decode source file."
            ) from exc

        except Exception as exc:
            logger.exception(
                "Unable to read source."
            )
            raise RuntimeError(
                f"Unable to read source: {exc}"
            ) from exc

        duration = (
            datetime.now() - started
        ).total_seconds()

        logger.info(
            "Parsed %s in %.3f seconds.",
            path.name,
            duration,
        )

        return {
            "file_path": str(path.resolve()),
            "file_name": path.name,
            "source": source,
            "kind": "clang-translation-unit",
            "available": True,
            "parser": "internal",
            "language": "C",
            "encoding": "utf-8",
            "metadata": {
                "lines": len(source.splitlines()),
                "characters": len(source),
                "size_bytes": path.stat().st_size,
                "parsed_at": started.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "duration_seconds": round(
                    duration,
                    4,
                ),
            },
        }