"""
Unit tests for TextProcessor class.
"""

import os
from unittest.mock import patch

import pandas as pd

from text_processor import TextProcessor


class TestTextProcessor:
    """Test cases for TextProcessor class."""

    def test_init_default_directories(self):
        """Test TextProcessor initialization with default directories."""
        with patch("os.makedirs"):
            processor = TextProcessor()

            assert processor.corpus_dir == "corpus"
            assert processor.data_dir == "data"
            assert processor.word_frequencies == {}
            assert processor.vocabulary_df.empty

    def test_init_custom_directories(self):
        """Test TextProcessor initialization with custom directories."""
        with patch("os.makedirs"):
            processor = TextProcessor(corpus_dir="test_corpus", data_dir="test_data")

            assert processor.corpus_dir == "test_corpus"
            assert processor.data_dir == "test_data"

    def test_process_file_existing_file(self, sample_text_files):
        """Test processing an existing text file."""
        with patch("os.makedirs"):
            processor = TextProcessor(corpus_dir=str(sample_text_files))

            file_path = sample_text_files / "file1.txt"
            word_freq = processor.process_file(str(file_path))

            assert isinstance(word_freq, dict)
            assert len(word_freq) > 0
            # Should contain some words from the test file
            assert any(word in ["hola", "mundo", "casa"] for word in word_freq.keys())

    def test_process_file_nonexistent_file(self):
        """Test processing a non-existent file."""
        with patch("os.makedirs"):
            processor = TextProcessor()

            word_freq = processor.process_file("nonexistent.txt")
            assert word_freq == {}

    def test_process_all_corpus_files(self, sample_text_files):
        """Test processing all files in corpus directory."""
        with patch("os.makedirs"):
            processor = TextProcessor(corpus_dir=str(sample_text_files))

            word_frequencies = processor.process_all_corpus_files()

            assert isinstance(word_frequencies, dict)
            assert len(word_frequencies) > 0
            # Should contain words from all test files
            assert any(word in word_frequencies for word in ["hola", "agua", "python"])

    def test_process_all_corpus_files_empty_directory(self, temp_directory):
        """Test processing corpus files with empty directory."""
        empty_corpus = temp_directory / "empty_corpus"
        empty_corpus.mkdir()

        with patch("os.makedirs"):
            processor = TextProcessor(corpus_dir=str(empty_corpus))

            word_frequencies = processor.process_all_corpus_files()
            assert word_frequencies == {}

    def test_create_vocabulary_dataframe(self, mock_word_frequencies):
        """Test vocabulary DataFrame creation."""
        with patch("os.makedirs"):
            processor = TextProcessor()
            processor.word_frequencies = mock_word_frequencies

            # Mock the word list files don't exist, so it creates from all words
            with patch("os.path.exists", return_value=False):
                vocab_df = processor.create_vocabulary_dataframe()

                assert not vocab_df.empty
                assert "Word" in vocab_df.columns
                assert "length" in vocab_df.columns
                assert "Count" in vocab_df.columns  # Actual column name

                # Check that words with sufficient frequency are included
                for _, row in vocab_df.iterrows():
                    assert row["Count"] > 3  # Default min_frequency

                # Check length calculation
                for _, row in vocab_df.iterrows():
                    assert row["length"] == len(row["Word"])

    def test_create_vocabulary_dataframe_with_min_frequency(
        self, mock_word_frequencies
    ):
        """Test vocabulary DataFrame creation with minimum frequency filter."""
        with patch("os.makedirs"):
            processor = TextProcessor()
            processor.word_frequencies = mock_word_frequencies

            # Mock word list files don't exist
            with patch("os.path.exists", return_value=False):
                # Set high minimum frequency
                vocab_df = processor.create_vocabulary_dataframe(min_frequency=50)

                # Should only include words with frequency > 50
                for _, row in vocab_df.iterrows():
                    assert row["Count"] > 50

    def test_create_vocabulary_dataframe_empty_frequencies(self):
        """Test vocabulary DataFrame creation with empty word frequencies."""
        with patch("os.makedirs"):
            processor = TextProcessor()
            processor.word_frequencies = {}

            vocab_df = processor.create_vocabulary_dataframe()
            assert vocab_df.empty

    def test_save_word_frequencies(self, temp_directory, mock_word_frequencies):
        """Test saving word frequencies to CSV."""
        with patch("os.makedirs"):
            processor = TextProcessor(data_dir=str(temp_directory))
            processor.word_frequencies = mock_word_frequencies

            processor.save_word_frequencies()

            # Check file was created
            freq_file = temp_directory / "word_frequencies.csv"
            assert freq_file.exists()

            # Check file content
            df = pd.read_csv(freq_file)
            assert not df.empty
            assert "Word" in df.columns
            assert "Frequency" in df.columns

    def test_save_word_frequencies_empty(self, temp_directory):
        """Test saving empty word frequencies."""
        with patch("os.makedirs"):
            processor = TextProcessor(data_dir=str(temp_directory))
            processor.word_frequencies = {}

            processor.save_word_frequencies()
            # Method doesn't return anything, just prints message

    def test_load_word_frequencies(self, temp_directory, mock_word_frequencies):
        """Test loading word frequencies from CSV."""
        # First save frequencies
        with patch("os.makedirs"):
            processor = TextProcessor(data_dir=str(temp_directory))
            processor.word_frequencies = mock_word_frequencies
            processor.save_word_frequencies()

            # Clear and reload
            processor.word_frequencies = {}
            result = processor.load_word_frequencies()

            assert result is True
            assert len(processor.word_frequencies) > 0
            assert processor.word_frequencies["casa"] == mock_word_frequencies["casa"]

    def test_load_word_frequencies_nonexistent_file(self, temp_directory):
        """Test loading word frequencies when file doesn't exist."""
        with patch("os.makedirs"):
            processor = TextProcessor(data_dir=str(temp_directory))

            result = processor.load_word_frequencies()
            assert result is False
            assert processor.word_frequencies == {}

    def test_save_vocabulary(self, temp_directory, sample_vocabulary):
        """Test saving vocabulary DataFrame to CSV."""
        with patch("os.makedirs"):
            processor = TextProcessor(data_dir=str(temp_directory))
            processor.vocabulary_df = sample_vocabulary

            processor.save_vocabulary()

            # Check file was created
            vocab_file = temp_directory / "vocabulary.csv"
            assert vocab_file.exists()

            # Check file content
            df = pd.read_csv(vocab_file)
            assert not df.empty
            assert len(df) == len(sample_vocabulary)

    def test_save_vocabulary_empty(self, temp_directory):
        """Test saving empty vocabulary DataFrame."""
        with patch("os.makedirs"):
            processor = TextProcessor(data_dir=str(temp_directory))
            processor.vocabulary_df = pd.DataFrame()

            processor.save_vocabulary()
            # Method doesn't return anything, just prints message

    def test_load_vocabulary_default_filename(self, temp_directory, sample_vocabulary):
        """Test loading vocabulary with default filename."""
        # First save vocabulary
        with patch("os.makedirs"):
            processor = TextProcessor(data_dir=str(temp_directory))
            processor.vocabulary_df = sample_vocabulary
            processor.save_vocabulary()

            # Clear and reload
            processor.vocabulary_df = pd.DataFrame()
            result = processor.load_vocabulary()

            assert result is True
            assert not processor.vocabulary_df.empty
            assert len(processor.vocabulary_df) == len(sample_vocabulary)

    def test_load_vocabulary_custom_filename(self, temp_directory, sample_vocabulary):
        """Test loading vocabulary with custom filename."""
        custom_filename = "custom_vocab.csv"

        with patch("os.makedirs"):
            processor = TextProcessor(data_dir=str(temp_directory))
            processor.vocabulary_df = sample_vocabulary

            # Save with custom filename
            custom_path = temp_directory / custom_filename
            sample_vocabulary.to_csv(custom_path, index=False)

            # Load with custom filename
            processor.vocabulary_df = pd.DataFrame()
            result = processor.load_vocabulary(custom_filename)

            assert result is True
            assert not processor.vocabulary_df.empty

    def test_load_vocabulary_nonexistent_file(self, temp_directory):
        """Test loading vocabulary when file doesn't exist."""
        with patch("os.makedirs"):
            processor = TextProcessor(data_dir=str(temp_directory))

            result = processor.load_vocabulary()
            assert result is False
            assert processor.vocabulary_df.empty

    def test_get_vocabulary_stats(self, sample_vocabulary):
        """Test getting vocabulary statistics."""
        with patch("os.makedirs"):
            processor = TextProcessor()
            processor.vocabulary_df = sample_vocabulary

            stats = processor.get_vocabulary_stats()

            assert "total_words" in stats
            assert "min_length" in stats
            assert "max_length" in stats
            assert "min_frequency" in stats  # Note: this references "Count" column
            assert "max_frequency" in stats

            assert stats["total_words"] == len(sample_vocabulary)
            assert stats["min_length"] == sample_vocabulary["length"].min()
            assert stats["max_length"] == sample_vocabulary["length"].max()

    def test_get_vocabulary_stats_empty(self):
        """Test getting vocabulary statistics with empty DataFrame."""
        with patch("os.makedirs"):
            processor = TextProcessor()
            processor.vocabulary_df = pd.DataFrame()

            stats = processor.get_vocabulary_stats()

            assert "error" in stats
            assert stats["error"] == "No vocabulary available"

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.savefig")
    def test_plot_word_frequencies(
        self, mock_savefig, mock_show, temp_directory, mock_word_frequencies
    ):
        """Test plotting word frequencies."""
        with patch("os.makedirs"):
            processor = TextProcessor(data_dir=str(temp_directory))
            processor.word_frequencies = mock_word_frequencies

            # Should not raise an exception
            processor.plot_word_frequencies()

            # Check that plot was saved
            mock_savefig.assert_called()

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.savefig")
    def test_plot_word_frequencies_empty(self, mock_savefig, mock_show, temp_directory):
        """Test plotting word frequencies with empty data."""
        with patch("os.makedirs"):
            processor = TextProcessor(data_dir=str(temp_directory))
            processor.word_frequencies = {}

            # Should handle empty data gracefully
            processor.plot_word_frequencies()
            # No plot should be generated for empty data
            mock_savefig.assert_not_called()

    def test_directory_creation(self):
        """Test that required directories are created during initialization."""
        with patch("os.makedirs") as mock_makedirs:
            processor = TextProcessor(data_dir="test_data")

            # Check that makedirs was called for required directories
            expected_calls = [
                ("test_data",),
                (os.path.join("test_data", "plots"),),
            ]

            actual_calls = [call[0] for call in mock_makedirs.call_args_list]
            for expected in expected_calls:
                assert expected in actual_calls

    def test_process_file_encoding_handling(self, temp_directory):
        """Test processing files with different encodings."""
        # Create a file with special characters
        test_file = temp_directory / "encoding_test.txt"
        test_content = "Café niño año España"
        test_file.write_text(test_content, encoding="utf-8")

        with patch("os.makedirs"):
            processor = TextProcessor()

            word_freq = processor.process_file(str(test_file))

            # Should handle special characters correctly
            assert isinstance(word_freq, dict)
            # Check that accented characters are processed
            assert any(
                "caf" in word.lower() or "ni" in word.lower()
                for word in word_freq.keys()
            )

    def test_word_frequency_accumulation(self, sample_text_files):
        """Test that word frequencies are correctly accumulated across files."""
        with patch("os.makedirs"):
            processor = TextProcessor(corpus_dir=str(sample_text_files))

            # Process files individually to compare
            file1_freq = processor.process_file(str(sample_text_files / "file1.txt"))
            file2_freq = processor.process_file(str(sample_text_files / "file2.txt"))

            # Process all files together
            all_freq = processor.process_all_corpus_files()

            # Check that frequencies are accumulated
            for word in file1_freq:
                if word in file2_freq:
                    expected_freq = file1_freq[word] + file2_freq[word]
                    assert (
                        all_freq[word] >= expected_freq
                    )  # >= because file3 might also contain the word

    def test_vocabulary_length_calculation(self):
        """Test that word lengths are calculated correctly in vocabulary."""
        test_words = {"a": 10, "test": 5, "longer": 3, "verylongword": 1}

        with patch("os.makedirs"):
            processor = TextProcessor()
            processor.word_frequencies = test_words

            with patch("os.path.exists", return_value=False):
                vocab_df = processor.create_vocabulary_dataframe()

                for _, row in vocab_df.iterrows():
                    assert row["length"] == len(row["Word"])

    def test_min_frequency_filtering(self):
        """Test minimum frequency filtering in vocabulary creation."""
        test_words = {"frequent": 100, "common": 50, "rare": 5, "veryrare": 1}

        with patch("os.makedirs"):
            processor = TextProcessor()
            processor.word_frequencies = test_words

            with patch("os.path.exists", return_value=False):
                # Test different minimum frequencies
                vocab_df_all = processor.create_vocabulary_dataframe(min_frequency=1)
                assert len(vocab_df_all) == 3  # Only words > min_frequency

                vocab_df_filtered = processor.create_vocabulary_dataframe(
                    min_frequency=10
                )
                assert len(vocab_df_filtered) == 2  # Only "frequent" and "common"

                vocab_df_strict = processor.create_vocabulary_dataframe(
                    min_frequency=75
                )
                assert len(vocab_df_strict) == 1  # Only "frequent"
