from pathlib import Path
from datetime import datetime

from analyzer.ast_extractor import ASTExtractor
from analyzer.cppcheck_runner import run_cppcheck_analysis
from config.settings import ENABLE_CPPCHECK
from models.session_state import SessionState
from rules.rule_engine import RuleEngine
from services.session_service import SessionService
from utils.logger import logger


class AnalysisService:
    """
    Entry point for MISRA analysis.

    Responsibilities
    ----------------
    - Read source file
    - Extract AST
    - Execute MISRA rule engine
    - Execute optional Cppcheck analysis
    - Create analysis session
    """

    def __init__(self):
        self.sessions = SessionService()
        self.rule_engine = RuleEngine()
        self.ast_extractor = ASTExtractor()

    def start_analysis(self, session_id, file_path):
        logger.info("Starting analysis for session %s", session_id)

        source = self._read_source(file_path)

        analysis_context = self._extract_ast(file_path)

        violations = self.rule_engine.execute(
            source,
            file_path,
            analysis_context=analysis_context,
        )

        cppcheck_result = self._run_cppcheck(file_path)

        session = {
            "session_id": session_id,
            "file_path": file_path,
            "file_name": Path(file_path).name,
            "original_code": source,
            "violations": violations,
            "current_index": 0,
            "decisions": [],
            "patches": [],
            "patch_queue": [],
            "patch_history": [],
            "analysis_report": cppcheck_result,
            "analysis_context": analysis_context,
            "analysis_metadata": {
                "started_at": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "total_violations": len(violations),
                "cppcheck_enabled": ENABLE_CPPCHECK,
            },
            "final_code": "",
            "validation_result": None,
            "compliance_report": None,
            "output_file_path": "",
            "report_path": "",
            "status": (
                SessionState.REVIEWING.value
                if violations
                else SessionState.BUILDING.value
            ),
        }

        self.sessions.save(session_id, session)

        logger.info(
            "Analysis completed (%d violations)",
            len(violations),
        )

        return session

    def _read_source(self, file_path):
        try:
            with open(
                file_path,
                "r",
                encoding="utf-8",
            ) as fp:
                return fp.read()

        except UnicodeDecodeError:
            logger.exception(
                "UTF-8 decode failed for %s",
                file_path,
            )
            return ""

        except FileNotFoundError:
            logger.exception(
                "Source file not found: %s",
                file_path,
            )
            return ""

        except Exception:
            logger.exception(
                "Unexpected file read failure."
            )
            return ""

    def _extract_ast(self, file_path):
        try:
            return self.ast_extractor.extract(file_path)

        except Exception:
            logger.exception(
                "AST extraction failed."
            )
            return None

    def _run_cppcheck(self, file_path):
        if not ENABLE_CPPCHECK:
            return ""

        try:
            return run_cppcheck_analysis(file_path)

        except Exception:
            logger.exception(
                "Cppcheck execution failed."
            )
            return ""