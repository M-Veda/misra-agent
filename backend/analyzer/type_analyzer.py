class TypeAnalyzer:
    def analyze(self, analysis_context):
        declarations = getattr(analysis_context, "get_declarations", None)
        if callable(declarations):
            typedef_map = {}
            for declaration in declarations():
                if declaration.kind == "typedef" and declaration.name:
                    typedef_map[declaration.name] = declaration.type_name

            types = []
            for declaration in declarations():
                if not declaration.name:
                    continue
                signedness = declaration.signedness
                if signedness is None:
                    signedness = self._infer_signedness(declaration)
                if declaration.kind == "typedef":
                    types.append(
                        {
                            "name": declaration.name,
                            "kind": "typedef",
                            "alias_of": declaration.type_name,
                            "signedness": signedness,
                        }
                    )
                    continue

                resolved_type = declaration.type_name
                if resolved_type in typedef_map:
                    alias_target = typedef_map[resolved_type]
                    types.append(
                        {
                            "name": declaration.name,
                            "kind": "typedef",
                            "alias_of": alias_target,
                            "signedness": signedness,
                        }
                    )
                    continue

                kind = "char" if declaration.type_name in {"char", "signed char", "unsigned char"} else "other"
                types.append(
                    {
                        "name": declaration.name,
                        "kind": kind,
                        "type": declaration.type_name,
                        "signedness": signedness,
                        "storage_specifiers": list(declaration.storage_specifiers),
                        "qualifiers": list(declaration.qualifiers),
                        "is_bit_field": declaration.is_bit_field,
                        "bit_width": declaration.bit_width,
                    }
                )
            if types:
                return types

        source = analysis_context.source_code or ""
        types = []
        for line in source.splitlines():
            if line.strip().startswith("int"):
                types.append({"name": line.strip().split()[1].split("=")[0].split("*")[0].strip(), "type": "int"})
        return types

    def _infer_signedness(self, declaration):
        if not declaration.type_name:
            return None
        lowered = declaration.type_name.lower()
        if lowered.startswith("unsigned"):
            return "unsigned"
        if lowered.startswith("signed"):
            return "signed"
        if lowered == "char":
            return "plain"
        if lowered.endswith("char") and "signed" in lowered:
            return "signed"
        if lowered.endswith("char") and "unsigned" in lowered:
            return "unsigned"
        return None