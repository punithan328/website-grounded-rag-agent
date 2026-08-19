import sys
from pathlib import Path

# Add repository root to sys.path
script_path = Path(__file__).resolve()
candidate = script_path.parents[1]

if (candidate / "app").exists():
    repo_root = candidate
else:
    repo_root = script_path.parents[0]

if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from app.logger import logger

modules = [
    'app.ingestion.registry',
    'app.ingestion.crawler',
    'app.ingestion.pipeline',
    'app.ingestion.validator',
    'app.ingestion.document_processor',
]

for m in modules:
    try:
        mod = __import__(m, fromlist=['*'])
        logger.info('Imported %s OK', m)
    except Exception as e:
        logger.exception('ERROR importing %s: %s', m, e)
        raise
logger.info('Done')
