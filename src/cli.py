"""
Command-line interface for FlashRead application.

This module provides CLI commands for processing text files and launching
the flashcard interface.
"""

import argparse
import os
import sys

from .flashcard_app import FlashCardApp
from .text_processor import TextProcessor


class FlashReadCLI:
    """Command-line interface for FlashRead application."""

    def __init__(self):
        """Initialize the CLI with argument parser."""
        self.parser = argparse.ArgumentParser(
            description="FlashRead - Spanish text processing and vocabulary flashcard application",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  flashread generate                 # Process corpus and generate vocabulary
  flashread generate --plot         # Generate files and show frequency plot
  flashread run                      # Launch flashcard interface
  flashread run --vocabulary custom # Use custom vocabulary file
            """,
        )
        self.setup_parser()

    def setup_parser(self):
        """Set up command-line argument parser."""
        subparsers = self.parser.add_subparsers(
            dest="command", help="Available commands"
        )

        # Generate command
        generate_parser = subparsers.add_parser(
            "generate", help="Process corpus files and generate vocabulary data"
        )
        generate_parser.add_argument(
            "--corpus-dir",
            default="corpus",
            help="Directory containing text files to process (default: corpus)",
        )
        generate_parser.add_argument(
            "--data-dir",
            default="data",
            help="Directory for saving processed data (default: data)",
        )
        generate_parser.add_argument(
            "--min-frequency",
            type=int,
            default=3,
            help="Minimum word frequency for inclusion in vocabulary (default: 3)",
        )
        generate_parser.add_argument(
            "--plot", action="store_true", help="Generate and show word frequency plot"
        )
        generate_parser.add_argument(
            "--force",
            action="store_true",
            help="Force reprocessing even if data files exist",
        )

        # Run command
        run_parser = subparsers.add_parser("run", help="Launch the flashcard interface")
        run_parser.add_argument(
            "--data-dir",
            default="data",
            help="Directory containing processed data (default: data)",
        )
        run_parser.add_argument(
            "--vocabulary",
            default="vocabulary.csv",
            help="Vocabulary file to use (default: vocabulary.csv)",
        )
        run_parser.add_argument(
            "--corpus-dir",
            default="corpus",
            help="Corpus directory (used if vocabulary needs to be generated)",
        )

    def command_generate(self, args):
        """
        Execute the generate command.

        Args:
            args: Parsed command-line arguments
        """
        print("🚀 Starting FlashRead data generation...")

        # Initialize text processor
        processor = TextProcessor(corpus_dir=args.corpus_dir, data_dir=args.data_dir)

        # Check if data already exists and force flag
        word_freq_file = os.path.join(args.data_dir, "word_frequencies.csv")
        vocab_file = os.path.join(args.data_dir, "vocabulary.csv")

        if (
            not args.force
            and os.path.exists(word_freq_file)
            and os.path.exists(vocab_file)
        ):
            print("📁 Data files already exist. Use --force to regenerate.")

            # Load existing data for stats
            if processor.load_word_frequencies() and processor.load_vocabulary():
                stats = processor.get_vocabulary_stats()
                print(f"📊 Current vocabulary: {stats['total_words']} words")

                if args.plot:
                    print("📈 Generating frequency plot...")
                    processor.plot_word_frequencies()

                return True

        # Process corpus files
        print("📚 Processing corpus files...")
        word_frequencies = processor.process_all_corpus_files()

        if not word_frequencies:
            print("❌ Error: No words processed from corpus files.")
            return False

        # Save word frequencies
        print("💾 Saving word frequencies...")
        processor.save_word_frequencies()

        # Create vocabulary
        print("📝 Creating vocabulary...")
        vocabulary_df = processor.create_vocabulary_dataframe(
            min_frequency=args.min_frequency
        )

        if vocabulary_df.empty:
            print("❌ Error: No vocabulary created.")
            return False

        # Save vocabulary
        print("💾 Saving vocabulary...")
        processor.save_vocabulary()

        # Display statistics
        stats = processor.get_vocabulary_stats()
        print("\n📊 Generation Complete!")
        print(f"   Total words: {stats['total_words']}")
        print(f"   Length range: {stats['min_length']}-{stats['max_length']} letters")
        print(
            f"   Frequency range: {stats['min_frequency']}-{stats['max_frequency']} occurrences"
        )

        # Generate plot if requested
        if args.plot:
            print("📈 Generating frequency plot...")
            processor.plot_word_frequencies()

        print("✅ Data generation completed successfully!")
        return True

    def command_run(self, args):
        """
        Execute the run command.

        Args:
            args: Parsed command-line arguments
        """
        print("🎮 Starting FlashRead flashcard interface...")

        # Initialize text processor
        processor = TextProcessor(corpus_dir=args.corpus_dir, data_dir=args.data_dir)

        # Try to load existing vocabulary
        vocab_file = os.path.join(args.data_dir, args.vocabulary)

        if os.path.exists(vocab_file):
            print(f"📁 Loading vocabulary from {vocab_file}...")
            if not processor.load_vocabulary(args.vocabulary):
                print("❌ Error: Could not load vocabulary file.")
                return False
        else:
            print("📁 Vocabulary file not found. Generating new vocabulary...")

            # Load or generate word frequencies
            if not processor.load_word_frequencies():
                print("📚 Processing corpus files...")
                word_frequencies = processor.process_all_corpus_files()
                if not word_frequencies:
                    print("❌ Error: Could not process corpus files.")
                    return False
                processor.save_word_frequencies()

            # Create vocabulary
            print("📝 Creating vocabulary...")
            vocabulary_df = processor.create_vocabulary_dataframe()
            if vocabulary_df.empty:
                print("❌ Error: Could not create vocabulary.")
                return False

            processor.save_vocabulary()

        # Display vocabulary stats
        stats = processor.get_vocabulary_stats()
        print(f"📊 Loaded vocabulary: {stats['total_words']} words")

        # Launch flashcard application
        try:
            print("🎯 Launching flashcard interface...")
            print("   Click on words to get new ones")
            print("   Use controls to filter by length and letters")
            print("   Close the window to exit")

            app = FlashCardApp(processor.vocabulary_df)
            app.run()

        except ValueError as e:
            print(f"❌ Error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

        print("👋 FlashRead session ended.")
        return True

    def run(self):
        """Parse arguments and execute the appropriate command."""
        args = self.parser.parse_args()

        if not args.command:
            self.parser.print_help()
            return False

        try:
            if args.command == "generate":
                return self.command_generate(args)
            elif args.command == "run":
                return self.command_run(args)
            else:
                print(f"❌ Unknown command: {args.command}")
                return False

        except KeyboardInterrupt:
            print("\n⏹️  Operation cancelled by user.")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False


def main():
    """Main entry point for the CLI."""
    cli = FlashReadCLI()
    success = cli.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
