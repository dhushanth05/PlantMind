import logging
from pathlib import Path

logger = logging.getLogger(__name__)
_installed = False


class OptionalMLDependencyError(RuntimeError):
    pass


def _requirements_path() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / "requirements.ml.txt"
        if candidate.exists():
            return candidate
    return current.parents[3] / "requirements.ml.txt"


def ensure_optional_ml_dependencies() -> None:
    global _installed
    if _installed:
        return

    requirements = _requirements_path()
    if not requirements.exists():
        raise OptionalMLDependencyError(f"Optional ML requirements file not found: {requirements}")

    logger.warning("optional_ml_dependencies_missing_using_fallback", extra={"requirements": str(requirements)})
    raise OptionalMLDependencyError(
        "Optional ML dependencies are not installed; runtime pip installation is disabled for ingestion stability."
    )
