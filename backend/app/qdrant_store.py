from pathlib import Path

from qdrant_client import QdrantClient


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Qdrant storage directory
QDRANT_PATH = PROJECT_ROOT / "qdrant_data"

# Create one shared Qdrant client
qdrant = QdrantClient(
    path=str(QDRANT_PATH)
)