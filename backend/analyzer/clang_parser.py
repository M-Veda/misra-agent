from pathlib import Path


class ClangParser:
    def parse(self, file_path):
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(file_path)

        try:
            with path.open("r", encoding="utf-8") as handle:
                source = handle.read()
        except Exception as exc:
            raise RuntimeError(f"Unable to read source: {exc}") from exc

        return {"file_path": str(path), "source": source, "kind": "clang-translation-unit"}