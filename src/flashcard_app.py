"""
Pygame-based flashcard application for vocabulary learning.

This module contains the FlashCardApp class that manages the interactive
flashcard interface using pygame for Spanish vocabulary practice.
"""

import random
import pandas as pd
import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN, MOUSEBUTTONUP

from .utils import hyphenate_word


class FlashCardApp:
    """Pygame-based flashcard application for vocabulary learning."""
    
    def __init__(self, vocabulary_df):
        """
        Initialize the flashcard application.
        
        Args:
            vocabulary_df (pd.DataFrame): DataFrame with vocabulary words
        """
        if vocabulary_df is None or vocabulary_df.empty:
            raise ValueError("Vocabulary DataFrame cannot be empty")
        
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
            (self.vocabulary_df['Word'].str.contains(pattern, regex=True)) &
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
        display_word = word
        if self.hyphenate_enabled:
            try:
                display_word = hyphenate_word(word)
            except Exception as e:
                print(f"Warning: Could not hyphenate word '{word}': {e}")
                display_word = word
        
        # Apply case formatting
        if self.selected_case == "lower":
            display_word = display_word.lower()
        elif self.selected_case == "UPPER":
            display_word = display_word.upper()
        elif self.selected_case == "Title":
            display_word = display_word.title()
        
        # Render and display the word
        word_text = self.font.render(display_word, True, self.BLACK)
        text_rect = word_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 4))
        self.window.blit(word_text, text_rect)
        
        # Draw all UI elements
        self.draw_sliders()
        self.draw_toggles()
        self.draw_case_selection()
        self.draw_hyphenation_toggle()
        
        pygame.display.flip()
    
    def get_random_word(self):
        """
        Get a random word from the filtered vocabulary.
        
        Returns:
            str: Random word or None if no words match filters
        """
        filtered_df = self.get_filtered_df()
        if filtered_df.empty:
            print("Warning: No words match current filters. Using all vocabulary.")
            if self.vocabulary_df.empty:
                return None
            return random.choice(self.vocabulary_df['Word'].tolist())
        else:
            return random.choice(filtered_df['Word'].tolist())
    
    def run(self):
        """Main application loop."""
        if self.vocabulary_df.empty:
            print("Error: No vocabulary words available. Please check your word list files.")
            return
            
        dragging_min = dragging_max = False
        
        # Get initial word
        current_word = self.get_random_word()
        if current_word is None:
            print("Error: Could not get any words from vocabulary.")
            return
        
        self.display_word(current_word)
        
        clock = pygame.time.Clock()
        
        while True:
            clock.tick(60)  # Limit to 60 FPS
            
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
                        new_word = self.get_random_word()
                        if new_word:
                            current_word = new_word
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
    
    def close(self):
        """Clean up pygame resources."""
        pygame.quit() 