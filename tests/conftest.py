"""
Pytest configuration and shared fixtures for FlashRead tests.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pygame
import pytest

# Add the project root to path and handle src as a package
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Mock NLTK setup to avoid downloads during testing
with patch("src.utils.setup_nltk"):
    # Import src modules using the package structure
    import src.cli as cli
    import src.flashcard_app as flashcard_app
    import src.text_processor as text_processor
    import src.utils as utils

# Make the modules available with their simple names for tests
sys.modules["flashcard_app"] = flashcard_app
sys.modules["text_processor"] = text_processor
sys.modules["cli"] = cli
sys.modules["utils"] = utils


@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    """Initialize pygame for all tests that need it."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"  # Use dummy video driver for testing
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def sample_vocabulary():
    """Create a sample vocabulary DataFrame for testing."""
    return pd.DataFrame(
        {
            "Word": [
                "casa",
                "perro",
                "gato",
                "agua",
                "libro",
                "escuela",
                "amigo",
                "familia",
                "trabajar",
                "estudiar",
            ],
            "length": [4, 5, 4, 4, 5, 7, 5, 7, 8, 8],
            "Count": [
                100,
                85,
                75,
                90,
                70,
                60,
                80,
                65,
                45,
                50,
            ],  # Use actual column name
        }
    )


@pytest.fixture
def empty_vocabulary():
    """Create an empty vocabulary DataFrame for testing error cases."""
    return pd.DataFrame(columns=["Word", "length", "Count"])  # Use actual column names


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing file operations."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_text_files(temp_directory):
    """Create sample text files for testing text processing."""
    corpus_dir = temp_directory / "corpus"
    corpus_dir.mkdir()

    # Create sample text files
    files = {
        "file1.txt": "Hola mundo. Este es un texto de prueba. Casa perro gato.",
        "file2.txt": "Agua libro escuela. Amigo familia trabajar estudiar.",
        "file3.txt": "Python es un lenguaje de programación. Flask Django web.",
    }

    for filename, content in files.items():
        (corpus_dir / filename).write_text(content, encoding="utf-8")

    return corpus_dir


@pytest.fixture
def mock_word_frequencies():
    """Create mock word frequency data for testing."""
    return {
        "casa": 100,
        "perro": 85,
        "gato": 75,
        "agua": 90,
        "libro": 70,
        "escuela": 60,
        "amigo": 80,
        "familia": 65,
        "trabajar": 45,
        "estudiar": 50,
        "python": 30,
        "flask": 25,
        "django": 20,
        "web": 35,
    }


@pytest.fixture
def mock_pygame_events():
    """Create mock pygame events for testing UI interactions."""

    class MockEvent:
        def __init__(self, event_type, **kwargs):
            self.type = event_type
            for key, value in kwargs.items():
                setattr(self, key, value)

    return MockEvent
