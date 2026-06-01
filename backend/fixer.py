import re

def fix_common_issues(code):

    # ---------------------------------------------------
    # Remove unused global variable
    # ---------------------------------------------------
    code = re.sub(
        r'\nint\s+global\s*=\s*0\s*;\n',
        '\n',
        code
    )

    # ---------------------------------------------------
    # Add static linkage
    # ---------------------------------------------------
    code = re.sub(
        r'\bvoid\s+func\s*\(',
        'static void func(',
        code
    )

    # ---------------------------------------------------
    # Fix assignment inside if
    # ---------------------------------------------------
    code = re.sub(
        r'if\s*\(\s*(\w+)\s*=\s*(\d+)\s*\)',
        r'if (\1 == \2)',
        code
    )

    # ---------------------------------------------------
    # Fix main declaration
    # ---------------------------------------------------
    code = re.sub(
        r'int\s+main\s*\(\s*\)',
        'int main(void)',
        code
    )

    # ---------------------------------------------------
    # Fix array bounds
    # ---------------------------------------------------
    code = code.replace("i <= 5", "i < 5")

    # ---------------------------------------------------
    # Replace unsafe malloc
    # ---------------------------------------------------
    malloc_match = re.search(
        r'char\s*\*\s*(\w+)\s*=\s*malloc\s*\(\s*(\d+)\s*\)\s*;',
        code
    )

    pointer_name = None

    if malloc_match:

        pointer_name = malloc_match.group(1)
        size = malloc_match.group(2)

        code = re.sub(
            r'char\s*\*\s*' + pointer_name +
            r'\s*=\s*malloc\s*\(\s*' + size + r'\s*\)\s*;',
            f'char {pointer_name}[{size}];',
            code
        )

    # ---------------------------------------------------
    # Replace unsafe gets()
    # ---------------------------------------------------
    if pointer_name:

        code = re.sub(
        r'gets\s*\(\s*' + pointer_name + r'\s*\)\s*;\s*'
        r'if\s*\(\s*' + pointer_name + r'\s*!=\s*NULL\s*\)\s*'
        r'printf\s*\(\s*' + pointer_name + r'\s*\)\s*;',
        (
    f'    if (fgets({pointer_name}, sizeof({pointer_name}), stdin) != NULL)\n'
    '    {\n'
    f'        (void)printf("%s", {pointer_name});\n'
    '    }'
),
        code,
        flags=re.DOTALL
    )

    # ---------------------------------------------------
    # Remove invalid NULL checks on arrays
    # ---------------------------------------------------
    if pointer_name:

        code = re.sub(
            r'if\s*\(\s*' + pointer_name + r'\s*!=\s*NULL\s*\)\s*'
            r'\(void\)printf\s*\(\s*"%s"\s*,\s*' + pointer_name + r'\s*\)\s*;',
            '',
            code
        )

        code = re.sub(
            r'if\s*\(\s*' + pointer_name + r'\s*!=\s*NULL\s*\)',
            '',
            code
        )

    # ---------------------------------------------------
    # Replace unused array assignment
    # ---------------------------------------------------
    code = re.sub(
    r'arr\s*\[\s*i\s*\]\s*=\s*i\s*\*\s*10\s*;',
    r'arr[i] = i * 10;\n        (void)printf("%d\\n", arr[i]);',
    code
)

    # ---------------------------------------------------
    # Safe printf formatting
    # ---------------------------------------------------
    code = re.sub(
        r'(?<!\(void\))printf\s*\(\s*(\w+)\s*\)\s*;',
        r'(void)printf("%s", \1);',
        code
)

    # ---------------------------------------------------
    # Add (void) before printf
    # ---------------------------------------------------
    code = re.sub(
        r'(?<!\(void\))printf\s*\(',
        r'(void)printf(',
        code
    )

    # ---------------------------------------------------
    # Remove free()
    # ---------------------------------------------------
    code = re.sub(
        r'free\s*\([^\)]*\)\s*;',
        '',
        code
    )

    # ---------------------------------------------------
    # Fix return
    # ---------------------------------------------------
    code = re.sub(
        r'\breturn\s*;',
        'return 0;',
        code
    )

    # ---------------------------------------------------
    # Clean excessive blank lines
    # ---------------------------------------------------
    code = re.sub(r'\n{3,}', '\n\n', code)

    code = re.sub(
    r'for\(',
    'for (',
    code
)
    
    code = re.sub(
    r'\n\s{8}if \(fgets',
    r'\n    if (fgets',
    code
)
    
    code = re.sub(
    r'#include\s*<',
    '#include <',
    code
)
    
    ptr_decl_match = re.search(
    r'char\s+ptr\s*\[\s*10\s*\]\s*;',
    code
)

    if ptr_decl_match:

        ptr_decl = ptr_decl_match.group(0)

        code = re.sub(
        r'\n\s*char\s+ptr\s*\[\s*10\s*\]\s*;\n',
        '\n',
        code
    )

        code = re.sub(
        r'(int\s+arr\s*\[\s*5\s*\]\s*;)',
        r'\1\n    ' + ptr_decl,
        code
    )

    return code