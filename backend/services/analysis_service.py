from analyzer.ast_extractor import ASTExtractor
from analyzer.cppcheck_runner import run_cppcheck_analysis
from config.settings import ENABLE_CPPCHECK
from models.session_state import SessionState
from rules.rule_engine import RuleEngine
from services.session_service import SessionService
from utils.logger import logger


class AnalysisService:
    def __init__(self):
        self.sessions = SessionService()
        self.rule_engine = RuleEngine()
        self.ast_extractor = ASTExtractor()

    def start_analysis(self, session_id, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as source_file:
                source = source_file.read()
        except UnicodeDecodeError as exc:
            logger.exception("Failed to read source file %s as UTF-8", file_path)
            source = ""

        try:
            analysis_context = self.ast_extractor.extract(file_path)
        except Exception as exc:
            logger.exception("AST extraction failed for %s", file_path)
            analysis_context = None

        violations = self.rule_engine.execute(source, file_path, analysis_context=analysis_context)

        analysis_report = run_cppcheck_analysis(file_path) if ENABLE_CPPCHECK else ""

        session = {
            "session_id": session_id,
            "file_path": file_path,
            "original_code": source,
            "violations": violations,
            "current_index": 0,
            "decisions": [],
            "patches": [],
            "analysis_report": analysis_report,
            "final_code": "",
            "validation_result": None,
            "compliance_report": None,
            "output_file_path": "",
            "report_path": "",
            "status": SessionState.REVIEWING.value if violations else SessionState.BUILDING.value,
            "analysis_context": analysis_context,
        }

        self.sessions.save(session_id, session)
        return session
