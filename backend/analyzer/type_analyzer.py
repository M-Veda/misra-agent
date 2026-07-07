from analyzer.declaration_model import infer_signedness


class TypeAnalyzer:
    """
    Performs lightweight semantic type analysis.

    Current capabilities
    --------------------
    ✓ Typedef resolution
    ✓ Signedness inference
    ✓ Primitive type classification
    ✓ Pointer detection
    ✓ Character type detection
    ✓ Integer/Floating categorization
    ✓ Struct/Enum recognition
    """

    def analyze(self, analysis_context):

        declarations = getattr(
            analysis_context,
            "get_declarations",
            None,
        )

        if callable(declarations):

            declarations = declarations()

            typedef_map = {}

            typedef_signedness = {}

            analysed = []

            for declaration in declarations:

                if (
                    declaration.kind == "typedef"
                    and declaration.name
                ):

                    typedef_map[
                        declaration.name
                    ] = declaration.type_name

                    typedef_signedness[
                        declaration.name
                    ] = (
                        declaration.signedness
                        or infer_signedness(
                            declaration.type_name
                        )
                    )

            for declaration in declarations:

                if not declaration.name:
                    continue

                type_name = (
                    declaration.type_name
                    or ""
                )

                signedness = (
                    declaration.signedness
                )

                if signedness is None:

                    signedness = (
                        analysis_context.signedness.get(
                            declaration.name
                        )
                    )

                if (
                    signedness is None
                    and type_name
                    in typedef_signedness
                ):

                    signedness = typedef_signedness[
                        type_name
                    ]

                if signedness is None:

                    signedness = infer_signedness(
                        type_name
                    )

                resolved_type = (
                    typedef_map.get(
                        type_name,
                        type_name,
                    )
                )

                analysed.append(
                    {
                        "name": declaration.name,
                        "kind": declaration.kind,
                        "type": type_name,
                        "resolved_type": resolved_type,
                        "category": self._category(
                            resolved_type
                        ),
                        "signedness": signedness,
                        "storage_specifiers": list(
                            declaration.storage_specifiers
                        ),
                        "qualifiers": list(
                            declaration.qualifiers
                        ),
                        "is_pointer": "*" in type_name,
                        "is_typedef": (
                            declaration.kind
                            == "typedef"
                        ),
                        "is_bit_field": (
                            declaration.is_bit_field
                        ),
                        "bit_width": (
                            declaration.bit_width
                        ),
                    }
                )

            if analysed:
                return analysed

        return self._fallback(
            analysis_context
        )

    def _fallback(
        self,
        analysis_context,
    ):
        """
        Used when declaration extraction
        is unavailable.
        """

        source = (
            analysis_context.source_code
            or ""
        )

        results = []

        primitive_types = [
            "char",
            "short",
            "int",
            "long",
            "float",
            "double",
            "void",
        ]

        for line in source.splitlines():

            stripped = line.strip()

            for primitive in primitive_types:

                if stripped.startswith(
                    primitive + " "
                ):

                    try:

                        name = (
                            stripped
                            .split()[1]
                            .split("=")[0]
                            .split(";")[0]
                            .replace("*", "")
                            .strip()
                        )

                        results.append(
                            {
                                "name": name,
                                "kind": "variable",
                                "type": primitive,
                                "resolved_type": primitive,
                                "category": self._category(
                                    primitive
                                ),
                                "signedness": infer_signedness(
                                    primitive
                                ),
                                "storage_specifiers": [],
                                "qualifiers": [],
                                "is_pointer": "*" in stripped,
                                "is_typedef": False,
                                "is_bit_field": False,
                                "bit_width": None,
                            }
                        )

                    except Exception:
                        pass

                    break

        return results

    def _category(
        self,
        type_name,
    ):
        """
        Classify types for the rule engine.
        """

        t = (
            type_name
            or ""
        ).lower()

        if "*" in t:
            return "pointer"

        if t in {
            "char",
            "signed char",
            "unsigned char",
        }:
            return "char"

        if any(
            token in t
            for token in (
                "int",
                "short",
                "long",
            )
        ):
            return "integer"

        if (
            "float" in t
            or "double" in t
        ):
            return "floating"

        if t.startswith(
            "struct"
        ):
            return "struct"

        if t.startswith(
            "enum"
        ):
            return "enum"

        if t.startswith(
            "union"
        ):
            return "union"

        if t == "void":
            return "void"

        return "other"

    def _infer_signedness(
        self,
        declaration,
    ):
        return infer_signedness(
            getattr(
                declaration,
                "type_name",
                None,
            )
        )