"""
Shared utilities for FlashRead application.

This module contains utility functions used across the application
for setup, configuration, and word processing.
"""

import nltk
import seaborn as sns
import silabeador


def setup_nltk():
    """Download required NLTK data."""
    nltk.download("punkt", quiet=True)
    nltk.download("stopwords", quiet=True)


def setup_matplotlib():
    """Configure matplotlib and seaborn settings."""
    sns.set(style="whitegrid")


def hyphenate_word(word):
    """
    Hyphenate a Spanish word using the silabeador library.

    Args:
        word (str): Spanish word to hyphenate

    Returns:
        str: Word with syllables separated by hyphens
    """
    syllables = silabeador.syllabify(word)
    hyphenated_word = "-".join(syllables)
    return hyphenated_word
