"""
FlashRead - A Spanish text processing and vocabulary flashcard application.

This module processes Spanish text files to extract word frequencies and creates
an interactive pygame-based flashcard interface for vocabulary learning.
"""

import string
import os
import re
import random
import sys
from collections import defaultdict

import nltk
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pygame
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from pygame.locals import QUIT, MOUSEBUTTONDOWN, MOUSEBUTTONUP
import silabeador


def setup_nltk():
    """Download required NLTK data."""
    nltk.download('punkt')
    nltk.download('stopwords')


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
    hyphenated_word = '-'.join(syllables)
    return hyphenated_word


def process_file(filename):
    """
    Process a text file and return a dictionary with words and their frequencies.
    
    Args:
        filename (str): Path to the text file to process
        
    Returns:
        dict: Dictionary with words as keys and frequencies as values
    """
    word_freq = defaultdict(int)

    with open(filename, 'r', encoding='utf-8') as file:
        text = file.read()

    # Remove punctuation and convert to lowercase
    text = text.translate(str.maketrans('', '', string.punctuation)).lower()

    # Remove unicode characters but preserve Spanish characters
    text = re.sub(r'[^\w\s.,;:!?¿¡áéíóúüñÁÉÍÓÚÜÑ]+', '', text)

    # Tokenize the text
    tokens = word_tokenize(text)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]

    # Count word frequencies
    for token in tokens:
        word_freq[token] += 1

    return dict(word_freq)


def plot_word_frequencies(word_freq):
    """
    Plot the word frequencies using seaborn.
    
    Args:
        word_freq (dict): Dictionary with words and their frequencies
    """
    df = pd.DataFrame(word_freq.items(), columns=['Word', 'Frequency'])
    df = df.sort_values(by='Frequency', ascending=False)
    
    print("Top 20 words:")
    print(df.head(20))
    
    plt.figure(figsize=(12, 6))
    sns.barplot(x='Frequency', y='Word', data=df.head(20))
    plt.title('Top 20 Words')
    plt.xlabel('Frequency')
    plt.ylabel('Word')
    plt.show()


def process_all_corpus_files(corpus_dir):
    """
    Process all text files in the given directory and return accumulated word frequencies.
    
    Args:
        corpus_dir (str): Directory containing text files to process
        
    Returns:
        dict: Dictionary with accumulated word frequencies across all files
    """
    total_word_freq = defaultdict(int)

    for filename in os.listdir(corpus_dir):
        if filename.endswith('.txt'):
            print(f"Processing file: {filename}")
            file_path = os.path.join(corpus_dir, filename)
            word_freq = process_file(file_path)
            for word, freq in word_freq.items():
                total_word_freq[word] += freq

    return dict(total_word_freq)


def read_word_list(file_path, word_count):
    """
    Read a file containing a list of words and return a DataFrame with word counts.
    
    Args:
        file_path (str): Path to the word list file
        word_count (dict): Dictionary with word frequencies from corpus
        
    Returns:
        pd.DataFrame: DataFrame with words and their counts
    """
    df = pd.read_csv(file_path, header=None, names=['Word'])
    df['Word'] = df['Word'].str.translate(str.maketrans('', '', string.punctuation)).str.lower()
    df['Count'] = df['Word'].map(word_count).fillna(0).astype(int)
    return df


def create_vocabulary_dataframe(word_count):
    """
    Create a filtered vocabulary DataFrame from word lists.
    
    Args:
        word_count (dict): Dictionary with word frequencies from corpus
        
    Returns:
        pd.DataFrame: Filtered DataFrame with words, counts, and lengths
    """
    # Read and combine word lists from files 04.txt through 08.txt
    dfs = []
    for i in range(4, 9):
        file_path = f'0{i}.txt'
        if os.path.exists(file_path):
            df = read_word_list(file_path, word_count)
            dfs.append(df)
    
    if not dfs:
        print("Warning: No word list files found (04.txt - 08.txt)")
        return pd.DataFrame(columns=['Word', 'Count', 'length'])
    
    # Combine all word lists
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Filter words that appear more than 3 times
    filtered_df = combined_df[combined_df['Count'] > 3]
    
    # Add word length column
    filtered_df['length'] = filtered_df['Word'].str.len()
    
    return filtered_df


class FlashCardApp:
    """Pygame-based flashcard application for vocabulary learning."""
    
    def __init__(self, vocabulary_df):
        """
        Initialize the flashcard application.
        
        Args:
            vocabulary_df (pd.DataFrame): DataFrame with vocabulary words
        """
        self.vocabulary_df = vocabulary_df
        self.setup_pygame()
        self.setup_ui_elements()
        
    def setup_pygame(self):
        """Initialize pygame and display settings."""
        pygame.init()
        self.WINDOW_WIDTH = 800
        self.WINDOW_HEIGHT = 600
        self.window = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption('FlashRead - Spanish Vocabulary')
        
        # Set up fonts
        self.font = pygame.font.Font(None, 170)
        self.slider_font = pygame.font.Font(None, 24)
        
        # Set up colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.GRAY = (200, 200, 200)
        
    def setup_ui_elements(self):
        """Set up all UI elements and their initial states."""
        # Set up sliders
        self.SLIDER_WIDTH = 150
        self.SLIDER_HEIGHT = 10
        self.slider_min_rect = pygame.Rect(100, 500, self.SLIDER_WIDTH, self.SLIDER_HEIGHT)
        self.slider_max_rect = pygame.Rect(300, 500, self.SLIDER_WIDTH, self.SLIDER_HEIGHT)
        self.slider_min_handle = pygame.Rect(100, 495, 10, 20)
        self.slider_max_handle = pygame.Rect(300, 495, 10, 20)
        self.slider_min_value = 4
        self.slider_max_value = 8
        
        # Set up alphabet toggles
        self.alphabet = "abcdefghijklmnopqrstuvwxyz"
        self.toggle_boxes = []
        self.toggle_states = {}
        self.box_size = 30
        
        for i, letter in enumerate(self.alphabet):
            x = 50 + (i % 13) * (self.box_size + 10)
            y = 400 + (i // 13) * (self.box_size + 10)
            self.toggle_boxes.append((pygame.Rect(x, y, self.box_size, self.box_size), letter))
            self.toggle_states[letter] = letter in "aeiouscl"
        
        # Set up case selection
        self.case_options = ["lower", "UPPER", "Title"]
        self.case_rects = []
        self.selected_case = "lower"
        
        for i, case in enumerate(self.case_options):
            x = 600
            y = 400 + i * 40
            self.case_rects.append((pygame.Rect(x, y, 100, 30), case))
        
        # Set up hyphenation toggle
        self.hyphenate_toggle_rect = pygame.Rect(600, 520, 100, 30)
        self.hyphenate_enabled = False
    
    def draw_sliders(self):
        """Draw the word length sliders."""
        pygame.draw.rect(self.window, self.GRAY, self.slider_min_rect)
        pygame.draw.rect(self.window, self.GRAY, self.slider_max_rect)
        pygame.draw.rect(self.window, self.BLACK, self.slider_min_handle)
        pygame.draw.rect(self.window, self.BLACK, self.slider_max_handle)
        
        min_text = self.slider_font.render(f"Min: {self.slider_min_value}", True, self.BLACK)
        max_text = self.slider_font.render(f"Max: {self.slider_max_value}", True, self.BLACK)
        self.window.blit(min_text, (self.slider_min_rect.x, self.slider_min_rect.y - 30))
        self.window.blit(max_text, (self.slider_max_rect.x, self.slider_max_rect.y - 30))
    
    def draw_toggles(self):
        """Draw the alphabet toggle buttons."""
        for box, letter in self.toggle_boxes:
            color = self.GREEN if self.toggle_states[letter] else self.RED
            pygame.draw.rect(self.window, color, box)
            letter_text = self.slider_font.render(letter.upper(), True, self.BLACK)
            text_rect = letter_text.get_rect(center=box.center)
            self.window.blit(letter_text, text_rect)
    
    def draw_case_selection(self):
        """Draw the case selection buttons."""
        for rect, case in self.case_rects:
            color = self.GREEN if case == self.selected_case else self.GRAY
            pygame.draw.rect(self.window, color, rect)
            case_text = self.slider_font.render(case, True, self.BLACK)
            text_rect = case_text.get_rect(center=rect.center)
            self.window.blit(case_text, text_rect)
    
    def draw_hyphenation_toggle(self):
        """Draw the hyphenation toggle button."""
        color = self.GREEN if self.hyphenate_enabled else self.GRAY
        pygame.draw.rect(self.window, color, self.hyphenate_toggle_rect)
        hyphenate_text = self.slider_font.render("Hyphenate", True, self.BLACK)
        text_rect = hyphenate_text.get_rect(center=self.hyphenate_toggle_rect.center)
        self.window.blit(hyphenate_text, text_rect)
    
    def get_filtered_df(self):
        """Filter the vocabulary DataFrame based on current UI settings."""
        active_letters = ''.join([letter for letter, state in self.toggle_states.items() if state])
        pattern = f"^[{active_letters}]+$"
        
        filtered_df = self.vocabulary_df[
            (self.vocabulary_df['Word'].str.contains(pattern)) &
            (self.vocabulary_df['length'] >= self.slider_min_value) &
            (self.vocabulary_df['length'] <= self.slider_max_value)
        ]
        
        return filtered_df
    
    def display_word(self, word):
        """
        Display a word on the screen with current formatting options.
        
        Args:
            word (str): Word to display
        """
        self.window.fill(self.WHITE)
        
        # Apply hyphenation if enabled
        if self.hyphenate_enabled:
            word = hyphenate_word(word)
        
        # Apply case formatting
        if self.selected_case == "lower":
            word = word.lower()
        elif self.selected_case == "UPPER":
            word = word.upper()
        elif self.selected_case == "Title":
            word = word.title()
        
        # Render and display the word
        word_text = self.font.render(word, True, self.BLACK)
        text_rect = word_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 4))
        self.window.blit(word_text, text_rect)
        
        # Draw all UI elements
        self.draw_sliders()
        self.draw_toggles()
        self.draw_case_selection()
        self.draw_hyphenation_toggle()
        
        pygame.display.flip()
    
    def run(self):
        """Main application loop."""
        if self.vocabulary_df.empty:
            print("Error: No vocabulary words available. Please check your word list files.")
            return
            
        dragging_min = dragging_max = False
        
        # Get initial word
        filtered_df = self.get_filtered_df()
        if filtered_df.empty:
            print("Warning: No words match current filters. Using all vocabulary.")
            current_word = random.choice(self.vocabulary_df['Word'].tolist())
        else:
            current_word = random.choice(filtered_df['Word'].tolist())
        
        self.display_word(current_word)
        
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return
                
                elif event.type == MOUSEBUTTONUP:
                    dragging_min = dragging_max = False
                
                elif event.type == MOUSEBUTTONDOWN:
                    # Click on word to get next word
                    word_rect = self.font.render(current_word, True, self.BLACK).get_rect(
                        center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 4)
                    )
                    if word_rect.collidepoint(event.pos):
                        filtered_df = self.get_filtered_df()
                        if not filtered_df.empty:
                            current_word = random.choice(filtered_df['Word'].tolist())
                            self.display_word(current_word)
                    
                    # Handle alphabet toggles
                    for box, letter in self.toggle_boxes:
                        if box.collidepoint(event.pos):
                            self.toggle_states[letter] = not self.toggle_states[letter]
                            self.display_word(current_word)
                    
                    # Handle case selection
                    for rect, case in self.case_rects:
                        if rect.collidepoint(event.pos):
                            self.selected_case = case
                            self.display_word(current_word)
                    
                    # Handle hyphenation toggle
                    if self.hyphenate_toggle_rect.collidepoint(event.pos):
                        self.hyphenate_enabled = not self.hyphenate_enabled
                        self.display_word(current_word)
                    
                    # Handle slider interactions
                    if self.slider_min_handle.collidepoint(event.pos):
                        dragging_min = True
                    if self.slider_max_handle.collidepoint(event.pos):
                        dragging_max = True
                
                elif event.type == pygame.MOUSEMOTION:
                    # Handle slider dragging
                    if dragging_min:
                        self.slider_min_handle.x = max(
                            self.slider_min_rect.x,
                            min(event.pos[0], self.slider_min_rect.x + self.SLIDER_WIDTH - self.slider_min_handle.width)
                        )
                        self.slider_min_value = 4 + (self.slider_min_handle.x - self.slider_min_rect.x) * 4 // (
                            self.SLIDER_WIDTH - self.slider_min_handle.width
                        )
                        self.display_word(current_word)
                    
                    elif dragging_max:
                        self.slider_max_handle.x = max(
                            self.slider_max_rect.x,
                            min(event.pos[0], self.slider_max_rect.x + self.SLIDER_WIDTH - self.slider_max_handle.width)
                        )
                        self.slider_max_value = 4 + (self.slider_max_handle.x - self.slider_max_rect.x) * 4 // (
                            self.SLIDER_WIDTH - self.slider_max_handle.width
                        )
                        self.display_word(current_word)


def main():
    """Main function that orchestrates the entire application."""
    print("Starting FlashRead - Spanish Vocabulary Flashcard Application")
    
    # Setup phase
    print("Setting up NLTK...")
    setup_nltk()
    
    print("Setting up matplotlib...")
    setup_matplotlib()
    
    # Text processing phase
    print("Processing corpus files...")
    corpus_dir = 'corpus'
    if not os.path.exists(corpus_dir):
        print(f"Error: Corpus directory '{corpus_dir}' not found.")
        return
    
    word_count = process_all_corpus_files(corpus_dir)
    print(f"Processed {len(word_count)} unique words from corpus.")
    
    # Optional: Display word frequency plot
    # Uncomment the next line to show frequency analysis
    # plot_word_frequencies(word_count)
    
    # Vocabulary preparation phase
    print("Creating vocabulary DataFrame...")
    vocabulary_df = create_vocabulary_dataframe(word_count)
    print(f"Created vocabulary with {len(vocabulary_df)} words.")
    
    if vocabulary_df.empty:
        print("Error: No vocabulary words found. Please check your word list files.")
        return
    
    # Launch flashcard application
    print("Launching flashcard interface...")
    app = FlashCardApp(vocabulary_df)
    app.run()
    
    print("FlashRead application closed.")


if __name__ == "__main__":
    main()
