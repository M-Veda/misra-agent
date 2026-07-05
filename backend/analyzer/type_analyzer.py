from analyzer.declaration_model import infer_signedness


class TypeAnalyzer:
    def analyze(self, analysis_context):
        declarations = getattr(analysis_context, "get_declarations", None)
        if callable(declarations):
            declarations = declarations()
            typedef_map = {}
            typedef_signedness = {}
            for declaration in declarations:
                if declaration.kind == "typedef" and declaration.name:
                    typedef_map[declaration.name] = declaration.type_name
                    typedef_signedness[declaration.name] = declaration.signedness or infer_signedness(declaration.type_name)

            types = []
            for declaration in declarations:
                if not declaration.name:
                    continue
                signedness = declaration.signedness
                if signedness is None:
                    signedness = analysis_context.signedness.get(declaration.name)
                if signedness is None and declaration.type_name in typedef_signedness:
                    signedness = typedef_signedness[declaration.type_name]
                if signedness is None:
                    signedness = infer_signedness(declaration.type_name)
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
        return infer_signedness(getattr(declaration, "type_name", None))
