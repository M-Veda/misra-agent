from analyzer.ast_extractor import ASTExtractor
from analyzer.cppcheck_runner import run_cppcheck_analysis
from config.settings import ENABLE_CPPCHECK
from models.session_state import SessionState
from rules.rule_engine import RuleEngine
from services.session_service import SessionService


class AnalysisService:
    def __init__(self):
        self.sessions = SessionService()
        self.rule_engine = RuleEngine()
        self.ast_extractor = ASTExtractor()

    def start_analysis(self, session_id, file_path):
        with open(file_path, "r", encoding="utf-8") as source_file:
            source = source_file.read()

        analysis_context = self.ast_extractor.extract(file_path)
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
