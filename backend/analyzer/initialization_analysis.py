"""
Initialization state analysis.
"""

from dataclasses import dataclass, field

from rules.rule_helpers import (
    declaration_match,
    extract_declarators,
    extract_symbol,
    is_function_prototype,
    strip_comments,
)


@dataclass(slots=True)
class InitializationTracker:
    """
    Tracks initialization state of declared objects.
    """

    initialized: dict = field(default_factory=dict)

    declarations: list = field(default_factory=list)

    assignments: list = field(default_factory=list)

    uses: list = field(default_factory=list)

    def declare(
        self,
        declarator,
        line=None,
    ):
        """
        Register a declaration.
        """

        symbol = extract_symbol(declarator)

        if not symbol:
            return

        initialized = "=" in declarator

        self.initialized[symbol] = initialized

        self.declarations.append(
            {
                "symbol": symbol,
                "initialized": initialized,
                "line": line,
            }
        )

    def assign(
        self,
        symbol,
        line=None,
    ):
        """
        Mark an object as initialized.
        """

        self.initialized[symbol] = True

        self.assignments.append(
            {
                "symbol": symbol,
                "line": line,
            }
        )

    def initialized_state(
        self,
        symbol,
    ):
        """
        Return whether a symbol is initialized.
        """

        return self.initialized.get(
            symbol,
            True,
        )

    def use(
        self,
        symbol,
        line=None,
    ):
        """
        Record a symbol use.
        """

        self.uses.append(
            {
                "symbol": symbol,
                "line": line,
                "initialized": self.initialized_state(
                    symbol
                ),
            }
        )


def build_initialization_tracker(
    code,
):
    """
    Build initialization information for a translation unit.
    """

    tracker = InitializationTracker()

    for line_number, raw_line in enumerate(
        code.splitlines(),
        start=1,
    ):

        line = strip_comments(raw_line)

        match = declaration_match(line)

        if not match:
            continue

        declaration = match.group("decl")

        if is_function_prototype(declaration):
            continue

        for declarator in extract_declarators(
            declaration
        ):
            tracker.declare(
                declarator,
                line=line_number,
            )

    return tracker


__all__ = (
    "InitializationTracker",
    "build_initialization_tracker",
)