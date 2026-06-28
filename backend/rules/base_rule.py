from abc import ABC, abstractmethod

from models.rule import Rule


class BaseRule(ABC):
    """Common interface for every MISRA C:2012 rule plugin."""

    RULE_ID = ""
    TITLE = ""
    CHAPTER = ""
    CATEGORY = ""
    SEVERITY = "Required"
    DESCRIPTION = ""
    RATIONALE = ""
    FIXABLE = False
    REFERENCES = ()
    PRIORITY = 100
    ENABLED_BY_DEFAULT = True
    FIX_STRATEGY = ""
    METADATA = {}

    @classmethod
    def metadata(cls):
        cls.validate_metadata()
        return Rule(
            rule_id=cls.RULE_ID,
            title=cls.TITLE,
            chapter=cls.CHAPTER or cls._chapter_from_rule_id(),
            category=cls.CATEGORY,
            severity=cls.SEVERITY,
            description=cls.DESCRIPTION,
            rationale=cls.RATIONALE,
            fixable=cls.FIXABLE,
            auto_fixable=cls.FIXABLE,
            references=tuple(cls.REFERENCES),
            priority=cls.PRIORITY,
            enabled_by_default=cls.ENABLED_BY_DEFAULT,
            fix_strategy=cls.FIX_STRATEGY,
            metadata=dict(cls.METADATA),
        )

    @classmethod
    def validate_metadata(cls):
        missing = []
        for field_name in ("RULE_ID", "TITLE", "CHAPTER", "CATEGORY", "SEVERITY", "DESCRIPTION"):
            if not getattr(cls, field_name, ""):
                missing.append(field_name)
        if missing:
            raise ValueError(f"Rule {cls.__name__} is missing metadata: {', '.join(missing)}")
        if not isinstance(cls.PRIORITY, int) or cls.PRIORITY < 0:
            raise ValueError(f"Rule {cls.__name__} priority must be a non-negative integer.")

    @classmethod
    def _chapter_from_rule_id(cls):
        return cls.RULE_ID.split(".", 1)[0] if cls.RULE_ID else ""

    @abstractmethod
    def check(self, code: str, file_path: str):
        """Return a list of Violation objects for this rule."""

    def check_with_context(self, code: str, file_path: str, analysis_context=None):
        return self.check(code=code, file_path=file_path)

    def suggest_fix(self, violation):
        return None

    def create_violation(self, file_path, line, original, suggestion="", explanation="", column=0, metadata=None):
        from rules.violation_factory import create_violation

        return create_violation(
            rule=self,
            file_path=file_path,
            line=line,
            original=original,
            suggestion=suggestion,
            explanation=explanation,
            column=column,
            metadata=metadata,
        )

    @property
    def id(self):
        return self.RULE_ID

    @property
    def title(self):
        return self.TITLE

    @property
    def chapter(self):
        return self.CHAPTER or self._chapter_from_rule_id()

    @property
    def category(self):
        return self.CATEGORY

    @property
    def severity(self):
        return self.SEVERITY

    @property
    def description(self):
        return self.DESCRIPTION