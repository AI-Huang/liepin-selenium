import logging
from pathlib import Path


def setup_logging(log_dir=None):
    if log_dir is None:
        log_dir = Path(__file__).resolve().parent.parent.parent / "logs"

    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "crawler.log"),
            logging.StreamHandler(),
        ],
    )

    return logging.getLogger("liepin_crawler")


def validate_job_data(job_data):
    required_fields = ["title", "location", "salary", "experience", "education", "url"]
    missing_fields = [field for field in required_fields if field not in job_data]

    if missing_fields:
        return False, f"Missing fields: {', '.join(missing_fields)}"

    return True, "Valid"
