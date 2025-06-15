"""
Text processing and vocabulary management for FlashRead.

This module contains the TextProcessor class that handles all text analysis,
word frequency calculation, vocabulary creation, and data persistence.
"""

import os
import re
import string
from collections import defaultdict

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from .utils import setup_matplotlib, setup_nltk


class TextProcessor:
    """Handles text processing, word frequency analysis, and vocabulary management."""

    def __init__(self, corpus_dir="corpus", data_dir="data"):
        """
        Initialize the text processor.

        Args:
            corpus_dir (str): Directory containing text files to process
            data_dir (str): Directory for saving processed data
        """
        self.corpus_dir = corpus_dir
        self.data_dir = data_dir
        self.word_frequencies = {}
        self.vocabulary_df = pd.DataFrame()

        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "plots"), exist_ok=True)

        # Setup required libraries
        setup_nltk()
        setup_matplotlib()

    def process_file(self, filename):
        """
        Process a single text file and return word frequencies.

        Args:
            filename (str): Path to the text file to process

        Returns:
            dict: Dictionary with words as keys and frequencies as values
        """
        word_freq = defaultdict(int)

        try:
            with open(filename, "r", encoding="utf-8") as file:
                text = file.read()
        except FileNotFoundError:
            print(f"Warning: File {filename} not found.")
            return {}
        except UnicodeDecodeError:
            print(
                f"Warning: Could not decode file {filename}. Trying with different encoding."
            )
            try:
                with open(filename, "r", encoding="latin-1") as file:
                    text = file.read()
            except Exception as e:
                print(f"Error reading file {filename}: {e}")
                return {}

        # Remove punctuation and convert to lowercase
        text = text.translate(str.maketrans("", "", string.punctuation)).lower()

        # Remove unicode characters but preserve Spanish characters
        text = re.sub(r"[^\w\s.,;:!?¿¡áéíóúüñÁÉÍÓÚÜÑ]+", "", text)

        # Tokenize the text
        tokens = word_tokenize(text)

        # Remove stopwords (English stopwords for now, can be extended)
        stop_words = set(stopwords.words("english"))
        tokens = [word for word in tokens if word not in stop_words and len(word) > 1]

        # Count word frequencies
        for token in tokens:
            word_freq[token] += 1

        return dict(word_freq)

    def process_all_corpus_files(self):
        """
        Process all text files in the corpus directory.

        Returns:
            dict: Dictionary with accumulated word frequencies across all files
        """
        if not os.path.exists(self.corpus_dir):
            print(f"Error: Corpus directory '{self.corpus_dir}' not found.")
            return {}

        total_word_freq = defaultdict(int)
        processed_files = 0

        for filename in os.listdir(self.corpus_dir):
            if filename.endswith(".txt"):
                print(f"Processing file: {filename}")
                file_path = os.path.join(self.corpus_dir, filename)
                word_freq = self.process_file(file_path)

                for word, freq in word_freq.items():
                    total_word_freq[word] += freq

                processed_files += 1

        self.word_frequencies = dict(total_word_freq)
        print(
            f"Processed {processed_files} files with {len(self.word_frequencies)} unique words."
        )

        return self.word_frequencies

    def save_word_frequencies(self, filename="word_frequencies.csv"):
        """
        Save word frequencies to a CSV file.

        Args:
            filename (str): Name of the output CSV file
        """
        if not self.word_frequencies:
            print("No word frequencies to save. Process corpus files first.")
            return

        df = pd.DataFrame(self.word_frequencies.items(), columns=["Word", "Frequency"])
        df = df.sort_values(by="Frequency", ascending=False)

        filepath = os.path.join(self.data_dir, filename)
        df.to_csv(filepath, index=False, encoding="utf-8")
        print(f"Word frequencies saved to {filepath}")

    def load_word_frequencies(self, filename="word_frequencies.csv"):
        """
        Load word frequencies from a CSV file.

        Args:
            filename (str): Name of the CSV file to load

        Returns:
            bool: True if loaded successfully, False otherwise
        """
        filepath = os.path.join(self.data_dir, filename)

        try:
            df = pd.read_csv(filepath, encoding="utf-8")
            self.word_frequencies = dict(zip(df["Word"], df["Frequency"]))
            print(
                f"Loaded {len(self.word_frequencies)} word frequencies from {filepath}"
            )
            return True
        except FileNotFoundError:
            print(f"Word frequencies file {filepath} not found.")
            return False
        except Exception as e:
            print(f"Error loading word frequencies: {e}")
            return False

    def plot_word_frequencies(self, top_n=20, save_plot=True):
        """
        Plot the word frequencies using seaborn.

        Args:
            top_n (int): Number of top words to display
            save_plot (bool): Whether to save the plot to file
        """
        if not self.word_frequencies:
            print("No word frequencies available for plotting.")
            return

        df = pd.DataFrame(self.word_frequencies.items(), columns=["Word", "Frequency"])
        df = df.sort_values(by="Frequency", ascending=False)

        print(f"Top {top_n} words:")
        print(df.head(top_n))

        plt.figure(figsize=(12, 8))
        sns.barplot(x="Frequency", y="Word", data=df.head(top_n))
        plt.title(f"Top {top_n} Most Frequent Words")
        plt.xlabel("Frequency")
        plt.ylabel("Word")
        plt.tight_layout()

        if save_plot:
            plot_path = os.path.join(
                self.data_dir, "plots", f"word_frequencies_top_{top_n}.png"
            )
            plt.savefig(plot_path, dpi=300, bbox_inches="tight")
            print(f"Plot saved to {plot_path}")

        plt.show()

    def read_word_list(self, file_path):
        """
        Read a file containing a list of words and return a DataFrame with word counts.

        Args:
            file_path (str): Path to the word list file

        Returns:
            pd.DataFrame: DataFrame with words and their counts
        """
        try:
            df = pd.read_csv(file_path, header=None, names=["Word"])
            df["Word"] = (
                df["Word"]
                .str.translate(str.maketrans("", "", string.punctuation))
                .str.lower()
            )
            df["Count"] = df["Word"].map(self.word_frequencies).fillna(0).astype(int)
            return df
        except FileNotFoundError:
            print(f"Warning: Word list file {file_path} not found.")
            return pd.DataFrame(columns=["Word", "Count"])
        except Exception as e:
            print(f"Error reading word list {file_path}: {e}")
            return pd.DataFrame(columns=["Word", "Count"])

    def create_vocabulary_dataframe(self, min_frequency=3):
        """
        Create a filtered vocabulary DataFrame from word lists.

        Args:
            min_frequency (int): Minimum frequency for words to be included

        Returns:
            pd.DataFrame: Filtered DataFrame with words, counts, and lengths
        """
        if not self.word_frequencies:
            print("No word frequencies available. Process corpus files first.")
            return pd.DataFrame(columns=["Word", "Count", "length"])

        # Read and combine word lists from files 04.txt through 08.txt
        dfs = []
        for i in range(4, 9):
            file_path = f"0{i}.txt"
            if os.path.exists(file_path):
                df = self.read_word_list(file_path)
                if not df.empty:
                    dfs.append(df)

        if not dfs:
            print("Warning: No word list files found (04.txt - 08.txt)")
            print("Creating vocabulary from all processed words...")

            # Create vocabulary from all words with minimum frequency
            df = pd.DataFrame(self.word_frequencies.items(), columns=["Word", "Count"])
            filtered_df = df[df["Count"] > min_frequency]
        else:
            # Combine all word lists
            combined_df = pd.concat(dfs, ignore_index=True)

            # Filter words that appear more than min_frequency times
            filtered_df = combined_df[combined_df["Count"] > min_frequency]

        # Add word length column
        filtered_df = filtered_df.copy()  # Avoid SettingWithCopyWarning
        filtered_df["length"] = filtered_df["Word"].str.len()

        # Remove duplicates and reset index
        filtered_df = filtered_df.drop_duplicates(subset=["Word"]).reset_index(
            drop=True
        )

        self.vocabulary_df = filtered_df
        print(
            f"Created vocabulary with {len(self.vocabulary_df)} words (min frequency: {min_frequency})"
        )

        return self.vocabulary_df

    def save_vocabulary(self, filename="vocabulary.csv"):
        """
        Save vocabulary DataFrame to a CSV file.

        Args:
            filename (str): Name of the output CSV file
        """
        if self.vocabulary_df.empty:
            print("No vocabulary to save. Create vocabulary DataFrame first.")
            return

        filepath = os.path.join(self.data_dir, filename)
        self.vocabulary_df.to_csv(filepath, index=False, encoding="utf-8")
        print(f"Vocabulary saved to {filepath}")

    def load_vocabulary(self, filename="vocabulary.csv"):
        """
        Load vocabulary DataFrame from a CSV file.

        Args:
            filename (str): Name of the CSV file to load

        Returns:
            bool: True if loaded successfully, False otherwise
        """
        filepath = os.path.join(self.data_dir, filename)

        try:
            self.vocabulary_df = pd.read_csv(filepath, encoding="utf-8")
            print(
                f"Loaded vocabulary with {len(self.vocabulary_df)} words from {filepath}"
            )
            return True
        except FileNotFoundError:
            print(f"Vocabulary file {filepath} not found.")
            return False
        except Exception as e:
            print(f"Error loading vocabulary: {e}")
            return False

    def get_vocabulary_stats(self):
        """
        Get statistics about the current vocabulary.

        Returns:
            dict: Dictionary with vocabulary statistics
        """
        if self.vocabulary_df.empty:
            return {"error": "No vocabulary available"}

        stats = {
            "total_words": len(self.vocabulary_df),
            "min_length": self.vocabulary_df["length"].min(),
            "max_length": self.vocabulary_df["length"].max(),
            "avg_length": self.vocabulary_df["length"].mean(),
            "min_frequency": self.vocabulary_df["Count"].min(),
            "max_frequency": self.vocabulary_df["Count"].max(),
            "avg_frequency": self.vocabulary_df["Count"].mean(),
        }

        return stats
