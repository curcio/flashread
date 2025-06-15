"""
Unit tests for FlashReadCLI class.
"""

from unittest.mock import MagicMock, patch

import pandas as pd

from cli import FlashReadCLI


class TestFlashReadCLI:
    """Test cases for FlashReadCLI class."""

    def test_init(self):
        """Test CLI initialization."""
        cli = FlashReadCLI()

        assert cli.parser is not None
        assert hasattr(cli, "parser")

    @patch("argparse.ArgumentParser.parse_args")
    def test_parse_args_generate_command(self, mock_parse_args):
        """Test argument parsing for generate command."""
        # Mock arguments for generate command
        mock_args = MagicMock()
        mock_args.command = "generate"
        mock_args.corpus_dir = "test_corpus"
        mock_args.data_dir = "test_data"
        mock_args.min_frequency = 15
        mock_args.plot = False
        mock_args.force = False
        mock_parse_args.return_value = mock_args

        cli = FlashReadCLI()
        cli.parser.parse_args(["generate", "--corpus-dir", "test_corpus"])

        # This would be the actual parsing result
        assert mock_parse_args.called

    @patch("src.utils.setup_nltk")
    @patch("src.cli.TextProcessor")
    def test_command_generate_success(self, mock_text_processor_class, mock_setup_nltk):
        """Test successful generate command execution."""
        # Mock TextProcessor instance
        mock_processor = MagicMock()
        mock_processor.process_all_corpus_files.return_value = {"word": 10}
        mock_processor.create_vocabulary_dataframe.return_value = pd.DataFrame(
            {"Word": ["test"]}
        )
        mock_processor.save_word_frequencies.return_value = (
            None  # Method doesn't return value
        )
        mock_processor.save_vocabulary.return_value = (
            None  # Method doesn't return value
        )
        mock_processor.get_vocabulary_stats.return_value = {
            "total_words": 100,
            "min_length": 3,
            "max_length": 12,
            "min_frequency": 5,
            "max_frequency": 100,
        }
        mock_text_processor_class.return_value = mock_processor

        cli = FlashReadCLI()

        # Mock args
        args = MagicMock()
        args.corpus_dir = "test_corpus"
        args.data_dir = "test_data"
        args.min_frequency = 5
        args.plot = False
        args.force = False

        with patch("os.path.exists", return_value=False):
            result = cli.command_generate(args)

            assert result is True
            mock_processor.process_all_corpus_files.assert_called_once()
            mock_processor.create_vocabulary_dataframe.assert_called_once_with(
                min_frequency=5
            )

    @patch("src.utils.setup_nltk")
    @patch("src.cli.TextProcessor")
    def test_command_generate_no_files(
        self, mock_text_processor_class, mock_setup_nltk
    ):
        """Test generate command with no corpus files."""
        mock_processor = MagicMock()
        mock_processor.process_all_corpus_files.return_value = {}
        mock_text_processor_class.return_value = mock_processor

        cli = FlashReadCLI()

        args = MagicMock()
        args.force = False

        with patch("os.path.exists", return_value=False):
            with patch("builtins.print"):
                result = cli.command_generate(args)

                assert result is False

    @patch("src.cli.FlashCardApp")
    @patch("src.utils.setup_nltk")
    @patch("src.cli.TextProcessor")
    def test_command_run_success(
        self, mock_text_processor_class, mock_setup_nltk, mock_flashcard_app_class
    ):
        """Test successful run command execution."""
        # Mock vocabulary loading
        mock_processor = MagicMock()
        mock_processor.load_vocabulary.return_value = True
        mock_processor.vocabulary_df = pd.DataFrame(
            {"Word": ["casa", "perro"], "length": [4, 5], "Count": [100, 85]}
        )
        mock_processor.get_vocabulary_stats.return_value = {"total_words": 2}
        mock_text_processor_class.return_value = mock_processor

        # Mock FlashCardApp
        mock_app = MagicMock()
        mock_flashcard_app_class.return_value = mock_app

        cli = FlashReadCLI()

        args = MagicMock()
        args.data_dir = "test_data"
        args.vocabulary = "vocabulary.csv"
        args.corpus_dir = "test_corpus"

        with patch("os.path.exists", return_value=True):
            with patch("builtins.print"):
                result = cli.command_run(args)

                assert result is True
                mock_processor.load_vocabulary.assert_called_once_with("vocabulary.csv")
                mock_flashcard_app_class.assert_called_once()
                mock_app.run.assert_called_once()

    @patch("src.utils.setup_nltk")
    @patch("src.cli.TextProcessor")
    def test_command_run_load_failure(self, mock_text_processor_class, mock_setup_nltk):
        """Test run command with vocabulary loading failure."""
        mock_processor = MagicMock()
        mock_processor.load_vocabulary.return_value = False
        mock_text_processor_class.return_value = mock_processor

        cli = FlashReadCLI()

        args = MagicMock()
        args.data_dir = "test_data"
        args.vocabulary = "nonexistent.csv"
        args.corpus_dir = "test_corpus"

        with patch("os.path.exists", return_value=True):
            with patch("builtins.print"):
                result = cli.command_run(args)

                assert result is False

    def test_run_generate_command(self):
        """Test run method with generate command."""
        cli = FlashReadCLI()

        with patch.object(cli, "command_generate", return_value=True) as mock_generate:
            with patch.object(cli.parser, "parse_args") as mock_parse_args:
                mock_args = MagicMock()
                mock_args.command = "generate"
                mock_parse_args.return_value = mock_args

                result = cli.run()

                assert result is True
                mock_generate.assert_called_once_with(mock_args)

    def test_run_run_command(self):
        """Test run method with run command."""
        cli = FlashReadCLI()

        with patch.object(cli, "command_run", return_value=True) as mock_run:
            with patch.object(cli.parser, "parse_args") as mock_parse_args:
                mock_args = MagicMock()
                mock_args.command = "run"
                mock_parse_args.return_value = mock_args

                result = cli.run()

                assert result is True
                mock_run.assert_called_once_with(mock_args)

    def test_run_no_command(self):
        """Test run method with no command."""
        cli = FlashReadCLI()

        with patch.object(cli.parser, "parse_args") as mock_parse_args:
            with patch.object(cli.parser, "print_help") as mock_print_help:
                mock_args = MagicMock()
                mock_args.command = None
                mock_parse_args.return_value = mock_args

                result = cli.run()

                assert result is False
                mock_print_help.assert_called_once()

    def test_run_invalid_command(self):
        """Test run method with invalid command."""
        cli = FlashReadCLI()

        with patch.object(cli.parser, "parse_args") as mock_parse_args:
            mock_args = MagicMock()
            mock_args.command = "invalid"
            mock_parse_args.return_value = mock_args

            with patch("builtins.print"):
                result = cli.run()
                assert result is False

    def test_argument_parser_setup(self):
        """Test that argument parser is set up correctly."""
        cli = FlashReadCLI()

        # Test that parser exists and has subparsers
        assert hasattr(cli, "parser")
        assert cli.parser is not None

        # Test help generation
        help_text = cli.parser.format_help()
        assert isinstance(help_text, str)
        assert len(help_text) > 0
        assert "generate" in help_text
        assert "run" in help_text

    @patch("src.utils.setup_nltk")
    @patch("src.cli.TextProcessor")
    def test_command_generate_existing_files_no_force(
        self, mock_text_processor_class, mock_setup_nltk
    ):
        """Test generate command with existing files and no force."""
        mock_processor = MagicMock()
        mock_processor.load_word_frequencies.return_value = True
        mock_processor.load_vocabulary.return_value = True
        mock_processor.get_vocabulary_stats.return_value = {"total_words": 100}
        mock_processor.corpus_dir = "test_corpus"
        mock_text_processor_class.return_value = mock_processor

        cli = FlashReadCLI()

        args = MagicMock()
        args.data_dir = "test_data"
        args.corpus_dir = "test_corpus"
        args.force = False
        args.plot = False

        with patch("os.path.exists", return_value=True):
            with patch("builtins.print"):
                result = cli.command_generate(args)

                assert result is True
                mock_processor.load_word_frequencies.assert_called_once()
                mock_processor.load_vocabulary.assert_called_once()

    @patch("src.cli.FlashCardApp")
    @patch("src.utils.setup_nltk")
    @patch("src.cli.TextProcessor")
    def test_command_run_exception_handling(
        self, mock_text_processor_class, mock_setup_nltk, mock_flashcard_app_class
    ):
        """Test exception handling in run command."""
        # Mock vocabulary loading to succeed
        mock_processor = MagicMock()
        mock_processor.load_vocabulary.return_value = True
        mock_processor.vocabulary_df = pd.DataFrame(
            {"Word": ["casa"], "length": [4], "Count": [100]}
        )
        mock_processor.get_vocabulary_stats.return_value = {"total_words": 1}
        mock_text_processor_class.return_value = mock_processor

        # Mock FlashCardApp to raise an exception
        mock_flashcard_app_class.side_effect = Exception("Test exception")

        cli = FlashReadCLI()

        args = MagicMock()
        args.data_dir = "test_data"
        args.vocabulary = "vocabulary.csv"
        args.corpus_dir = "test_corpus"

        with patch("os.path.exists", return_value=True):
            with patch("builtins.print"):
                result = cli.command_run(args)

                assert result is False

    @patch("src.utils.setup_nltk")
    @patch("src.cli.TextProcessor")
    def test_command_generate_with_plotting(
        self, mock_text_processor_class, mock_setup_nltk
    ):
        """Test generate command with plotting enabled."""
        mock_processor = MagicMock()
        mock_processor.process_all_corpus_files.return_value = {"word": 10}
        mock_processor.create_vocabulary_dataframe.return_value = pd.DataFrame(
            {"Word": ["test"]}
        )
        mock_processor.save_word_frequencies.return_value = (
            None  # Method doesn't return value
        )
        mock_processor.save_vocabulary.return_value = (
            None  # Method doesn't return value
        )
        mock_processor.get_vocabulary_stats.return_value = {
            "total_words": 100,
            "min_length": 3,
            "max_length": 12,
            "min_frequency": 5,
            "max_frequency": 100,
        }
        mock_text_processor_class.return_value = mock_processor

        cli = FlashReadCLI()

        args = MagicMock()
        args.corpus_dir = "test_corpus"
        args.data_dir = "test_data"
        args.min_frequency = 5
        args.plot = True
        args.force = False

        with patch("os.path.exists", return_value=False):
            with patch("builtins.print"):
                result = cli.command_generate(args)

                assert result is True
                # Should call plot_word_frequencies
                mock_processor.plot_word_frequencies.assert_called()

    def test_parser_help_format(self):
        """Test that parser help includes examples."""
        cli = FlashReadCLI()

        help_text = cli.parser.format_help()
        assert "Examples:" in help_text
        assert "generate" in help_text
        assert "run" in help_text
