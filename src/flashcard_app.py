"""
Pygame-based flashcard application for vocabulary learning.

This module contains the FlashCardApp class that manages the interactive
flashcard interface using pygame for Spanish vocabulary practice.
"""

import math
import random

import pandas as pd
import pygame
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, QUIT

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
        self.setup_colors_and_fonts()
        self.setup_settings_panel()
        self.setup_ui_elements()

    def setup_pygame(self):
        """Initialize pygame and display settings."""
        pygame.init()
        self.WINDOW_WIDTH = 800
        self.WINDOW_HEIGHT = 600
        self.window = pygame.display.set_mode(
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.RESIZABLE
        )
        pygame.display.set_caption("FlashRead - Spanish Vocabulary")

    def setup_colors_and_fonts(self):
        """Set up colors and fonts for the application."""
        # Main colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.GRAY = (200, 200, 200)

        # Settings panel colors
        self.SETTINGS_BG = (240, 240, 245)  # Removed alpha for no transparency
        self.SETTINGS_BORDER = (180, 180, 190)
        self.PANEL_SHADOW = (0, 0, 0, 50)

        # Cogwheel colors
        self.COGWHEEL_NORMAL = (100, 100, 110)
        self.COGWHEEL_HOVER = (70, 130, 180)
        self.COGWHEEL_ACTIVE = (50, 100, 150)

        # Font size setting
        self.font_size = 170  # Default font size for main word display
        self.min_font_size = 50  # Minimum font size
        self.max_font_size = 300  # Maximum font size

        # Fonts
        self.font = pygame.font.Font(None, self.font_size)  # Main word display
        self.settings_title_font = pygame.font.Font(None, 24)
        self.settings_label_font = pygame.font.Font(None, 20)
        self.settings_text_font = pygame.font.Font(None, 18)
        self.slider_font = pygame.font.Font(None, 18)

    def update_font_size(self, new_size):
        """Update the main word display font size."""
        self.font_size = max(self.min_font_size, min(self.max_font_size, new_size))
        self.font = pygame.font.Font(None, self.font_size)

    def handle_window_resize(self, new_size):
        """Handle window resize events."""
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = new_size
        self.window = pygame.display.set_mode(new_size, pygame.RESIZABLE)

        # Update cogwheel position
        self.cogwheel_rect = pygame.Rect(
            self.WINDOW_WIDTH - self.COGWHEEL_SIZE - self.COGWHEEL_MARGIN,
            self.COGWHEEL_MARGIN,
            self.COGWHEEL_SIZE,
            self.COGWHEEL_SIZE,
        )

        # Update settings panel position (keep it centered)
        panel_x = (self.WINDOW_WIDTH - self.PANEL_WIDTH) // 2
        panel_y = 80  # Below the word display
        self.settings_panel_rect = pygame.Rect(
            panel_x, panel_y, self.PANEL_WIDTH, self.PANEL_HEIGHT
        )

        # Update close button position
        self.close_button_rect = pygame.Rect(
            self.settings_panel_rect.right - 30,
            self.settings_panel_rect.top + 10,
            20,
            20,
        )

    def setup_settings_panel(self):
        """Set up the collapsible settings panel."""
        # Panel state
        self.settings_visible = False
        self.cogwheel_hovered = False

        # Layout constants
        self.COGWHEEL_SIZE = 32
        self.COGWHEEL_MARGIN = 20
        self.PANEL_WIDTH = 480
        self.PANEL_HEIGHT = 480
        self.PANEL_MARGIN = 40
        self.SECTION_SPACING = 25
        self.ELEMENT_SPACING = 12

        # Cogwheel icon position (upper right)
        self.cogwheel_rect = pygame.Rect(
            self.WINDOW_WIDTH - self.COGWHEEL_SIZE - self.COGWHEEL_MARGIN,
            self.COGWHEEL_MARGIN,
            self.COGWHEEL_SIZE,
            self.COGWHEEL_SIZE,
        )

        # Settings panel position (centered)
        panel_x = (self.WINDOW_WIDTH - self.PANEL_WIDTH) // 2
        panel_y = 80  # Below the word display
        self.settings_panel_rect = pygame.Rect(
            panel_x, panel_y, self.PANEL_WIDTH, self.PANEL_HEIGHT
        )

        # Close button for settings panel
        self.close_button_rect = pygame.Rect(
            self.settings_panel_rect.right - 30,
            self.settings_panel_rect.top + 10,
            20,
            20,
        )

    def setup_ui_elements(self):
        """Set up all UI elements and their initial states."""
        # Word length sliders (positioned within settings panel)
        panel_x = self.settings_panel_rect.x + self.PANEL_MARGIN
        panel_y = self.settings_panel_rect.y + self.PANEL_MARGIN + 30  # After title

        self.SLIDER_WIDTH = 120
        self.SLIDER_HEIGHT = 8

        # Min slider
        self.slider_min_rect = pygame.Rect(
            panel_x, panel_y + 50, self.SLIDER_WIDTH, self.SLIDER_HEIGHT
        )
        self.slider_min_handle = pygame.Rect(panel_x, panel_y + 46, 8, 16)
        self.slider_min_value = 4

        # Max slider
        self.slider_max_rect = pygame.Rect(
            panel_x + 200, panel_y + 50, self.SLIDER_WIDTH, self.SLIDER_HEIGHT
        )
        self.slider_max_handle = pygame.Rect(panel_x + 200, panel_y + 46, 8, 16)
        self.slider_max_value = 8

        # Alphabet toggles (arranged in settings panel)
        self.alphabet = "abcdefghijklmnopqrstuvwxyz"
        self.toggle_boxes = []
        self.toggle_states = {}
        self.box_size = 24

        toggle_start_y = panel_y + 125
        for i, letter in enumerate(self.alphabet):
            x = panel_x + (i % 13) * (self.box_size + 6)
            y = toggle_start_y + (i // 13) * (self.box_size + 6)
            self.toggle_boxes.append(
                (pygame.Rect(x, y, self.box_size, self.box_size), letter)
            )
            self.toggle_states[letter] = letter in "aeiouscl"

        # Case selection (radio buttons in settings panel)
        self.case_options = ["lower", "UPPER", "Title"]
        self.case_rects = []
        self.selected_case = "lower"

        case_start_y = toggle_start_y + 110
        for i, case in enumerate(self.case_options):
            x = panel_x + i * 120
            y = case_start_y
            self.case_rects.append((pygame.Rect(x, y, 100, 25), case))

        # Hyphenation toggle (checkbox in settings panel)
        self.hyphenate_toggle_rect = pygame.Rect(panel_x, case_start_y + 65, 20, 20)
        self.hyphenate_enabled = False

        # Font size controls (+/- buttons in settings panel)
        font_size_y = case_start_y + 100
        self.font_size_decrease_rect = pygame.Rect(panel_x, font_size_y, 30, 30)
        self.font_size_increase_rect = pygame.Rect(panel_x + 35, font_size_y, 30, 30)

    def draw_cogwheel(self):
        """Draw the cogwheel icon in the upper right corner."""
        center_x = self.cogwheel_rect.centerx
        center_y = self.cogwheel_rect.centery

        # Choose color based on state
        if self.settings_visible:
            color = self.COGWHEEL_ACTIVE
        elif self.cogwheel_hovered:
            color = self.COGWHEEL_HOVER
        else:
            color = self.COGWHEEL_NORMAL

        # Draw cogwheel shape (simplified gear)
        outer_radius = 14
        inner_radius = 8
        teeth = 8

        # Draw gear teeth
        for i in range(teeth):
            angle1 = (i / teeth) * 2 * math.pi
            angle2 = ((i + 0.5) / teeth) * 2 * math.pi
            angle3 = ((i + 1) / teeth) * 2 * math.pi

            # Outer points
            x1 = center_x + outer_radius * math.cos(angle1)
            y1 = center_y + outer_radius * math.sin(angle1)
            x2 = center_x + outer_radius * math.cos(angle2)
            y2 = center_y + outer_radius * math.sin(angle2)
            x3 = center_x + outer_radius * math.cos(angle3)
            y3 = center_y + outer_radius * math.sin(angle3)

            # Inner points
            inner_angle1 = ((i + 0.2) / teeth) * 2 * math.pi
            inner_angle2 = ((i + 0.8) / teeth) * 2 * math.pi
            ix1 = center_x + inner_radius * math.cos(inner_angle1)
            iy1 = center_y + inner_radius * math.sin(inner_angle1)
            ix2 = center_x + inner_radius * math.cos(inner_angle2)
            iy2 = center_y + inner_radius * math.sin(inner_angle2)

            # Draw tooth polygon
            points = [(x1, y1), (x2, y2), (x3, y3), (ix2, iy2), (ix1, iy1)]
            pygame.draw.polygon(self.window, color, points)

        # Draw center circle
        pygame.draw.circle(self.window, color, (center_x, center_y), 4)

        # Draw center hole
        pygame.draw.circle(self.window, self.WHITE, (center_x, center_y), 2)

    def draw_settings_panel(self):
        """Draw the settings panel when visible."""
        if not self.settings_visible:
            return

        # Create settings panel surface without transparency
        panel_surface = pygame.Surface((self.PANEL_WIDTH, self.PANEL_HEIGHT))

        # Draw panel background with rounded corners effect
        pygame.draw.rect(
            panel_surface, self.SETTINGS_BG, (0, 0, self.PANEL_WIDTH, self.PANEL_HEIGHT)
        )
        pygame.draw.rect(
            panel_surface,
            self.SETTINGS_BORDER,
            (0, 0, self.PANEL_WIDTH, self.PANEL_HEIGHT),
            2,
        )

        # Draw title
        title_text = self.settings_title_font.render("SETTINGS", True, self.BLACK)
        panel_surface.blit(title_text, (self.PANEL_MARGIN, 15))

        # Draw close button (X)
        close_x = self.PANEL_WIDTH - 25
        close_y = 15
        pygame.draw.line(
            panel_surface,
            self.BLACK,
            (close_x, close_y),
            (close_x + 10, close_y + 10),
            2,
        )
        pygame.draw.line(
            panel_surface,
            self.BLACK,
            (close_x + 10, close_y),
            (close_x, close_y + 10),
            2,
        )

        # Draw settings content
        self.draw_settings_content(panel_surface)

        # Blit the panel to the main window
        self.window.blit(
            panel_surface, (self.settings_panel_rect.x, self.settings_panel_rect.y)
        )

    def draw_settings_content(self, surface):
        """Draw the content inside the settings panel."""
        margin = self.PANEL_MARGIN

        # Word Length section
        y_pos = 50
        label_text = self.settings_label_font.render("Word Length:", True, self.BLACK)
        surface.blit(label_text, (margin, y_pos))

        # Sliders (adjust positions relative to panel)
        self.settings_panel_rect.x
        self.settings_panel_rect.y

        slider_y = y_pos + self.SECTION_SPACING + 10
        # Min slider
        slider_rect = pygame.Rect(
            margin, slider_y, self.SLIDER_WIDTH, self.SLIDER_HEIGHT
        )
        handle_rect = pygame.Rect(
            margin + (self.slider_min_value - 4) * self.SLIDER_WIDTH // 4,
            slider_y - 4,
            8,
            16,
        )
        pygame.draw.rect(surface, self.GRAY, slider_rect)
        pygame.draw.rect(surface, self.BLACK, handle_rect)

        min_text = self.settings_text_font.render(
            f"Min: {self.slider_min_value}", True, self.BLACK
        )
        surface.blit(min_text, (margin, slider_y - 20))

        # Max slider
        max_slider_x = margin + 200
        slider_rect = pygame.Rect(
            max_slider_x, slider_y, self.SLIDER_WIDTH, self.SLIDER_HEIGHT
        )
        handle_rect = pygame.Rect(
            max_slider_x + (self.slider_max_value - 4) * self.SLIDER_WIDTH // 4,
            slider_y - 4,
            8,
            16,
        )
        pygame.draw.rect(surface, self.GRAY, slider_rect)
        pygame.draw.rect(surface, self.BLACK, handle_rect)

        max_text = self.settings_text_font.render(
            f"Max: {self.slider_max_value}", True, self.BLACK
        )
        surface.blit(max_text, (max_slider_x, slider_y - 20))

        # Starting Letters section
        y_pos += self.SECTION_SPACING + 75
        label_text = self.settings_label_font.render(
            "Starting Letters:", True, self.BLACK
        )
        surface.blit(label_text, (margin, y_pos))

        # Alphabet toggles
        toggle_y = y_pos + self.SECTION_SPACING
        for i, (_, letter) in enumerate(self.toggle_boxes):
            x = margin + (i % 13) * (self.box_size + 6)
            y = toggle_y + (i // 13) * (self.box_size + 6)

            color = self.GREEN if self.toggle_states[letter] else self.RED
            toggle_rect = pygame.Rect(x, y, self.box_size, self.box_size)
            pygame.draw.rect(surface, color, toggle_rect)

            letter_text = self.settings_text_font.render(
                letter.upper(), True, self.BLACK
            )
            text_rect = letter_text.get_rect(center=toggle_rect.center)
            surface.blit(letter_text, text_rect)

        # Display Case section
        y_pos += self.SECTION_SPACING + 85
        label_text = self.settings_label_font.render("Display Case:", True, self.BLACK)
        surface.blit(label_text, (margin, y_pos))

        case_y = y_pos + self.SECTION_SPACING
        for i, (_, case) in enumerate(self.case_rects):
            x = margin + i * 120
            radio_rect = pygame.Rect(x, case_y, 15, 15)

            # Draw radio button
            pygame.draw.circle(surface, self.BLACK, radio_rect.center, 8, 2)
            if case == self.selected_case:
                pygame.draw.circle(surface, self.BLACK, radio_rect.center, 4)

            # Draw label
            case_text = self.settings_text_font.render(case, True, self.BLACK)
            surface.blit(case_text, (x + 20, case_y - 2))

        # Spanish Hyphenation section
        y_pos += self.SECTION_SPACING + 40
        checkbox_rect = pygame.Rect(margin, y_pos, 18, 18)
        pygame.draw.rect(surface, self.WHITE, checkbox_rect)
        pygame.draw.rect(surface, self.BLACK, checkbox_rect, 2)

        if self.hyphenate_enabled:
            # Draw checkmark
            pygame.draw.line(
                surface,
                self.BLACK,
                (checkbox_rect.x + 3, checkbox_rect.y + 9),
                (checkbox_rect.x + 7, checkbox_rect.y + 13),
                2,
            )
            pygame.draw.line(
                surface,
                self.BLACK,
                (checkbox_rect.x + 7, checkbox_rect.y + 13),
                (checkbox_rect.x + 15, checkbox_rect.y + 5),
                2,
            )

        hyphen_text = self.settings_text_font.render(
            "Spanish Hyphenation", True, self.BLACK
        )
        surface.blit(hyphen_text, (margin + 25, y_pos))

        # Font Size section
        y_pos += self.SECTION_SPACING + 35
        label_text = self.settings_label_font.render("Font Size:", True, self.BLACK)
        surface.blit(label_text, (margin, y_pos))

        font_size_y = y_pos + self.SECTION_SPACING

        # Decrease font size button (-)
        decrease_rect = pygame.Rect(margin, font_size_y, 30, 30)
        pygame.draw.rect(surface, self.GRAY, decrease_rect)
        pygame.draw.rect(surface, self.BLACK, decrease_rect, 2)
        minus_text = self.settings_text_font.render("-", True, self.BLACK)
        minus_rect = minus_text.get_rect(center=decrease_rect.center)
        surface.blit(minus_text, minus_rect)

        # Font size display
        font_size_text = self.settings_text_font.render(
            f"{self.font_size}", True, self.BLACK
        )
        surface.blit(font_size_text, (margin + 80, font_size_y + 8))

        # Increase font size button (+)
        increase_rect = pygame.Rect(margin + 35, font_size_y, 30, 30)
        pygame.draw.rect(surface, self.GRAY, increase_rect)
        pygame.draw.rect(surface, self.BLACK, increase_rect, 2)
        plus_text = self.settings_text_font.render("+", True, self.BLACK)
        plus_rect = plus_text.get_rect(center=increase_rect.center)
        surface.blit(plus_text, plus_rect)

    def get_filtered_df(self):
        """Filter the vocabulary DataFrame based on current UI settings."""
        active_letters = "".join(
            [letter for letter, state in self.toggle_states.items() if state]
        )

        # Handle case when no letters are selected
        if not active_letters:
            # Return empty DataFrame when no letters are allowed
            return pd.DataFrame(columns=self.vocabulary_df.columns)

        # Pattern to match words that contain ONLY the allowed letters
        # ^[allowed_letters]+$ means the entire word must consist only of allowed letters
        pattern = f"^[{active_letters}]+$"

        filtered_df = self.vocabulary_df[
            (self.vocabulary_df["Word"].str.contains(pattern, regex=True, case=False))
            & (self.vocabulary_df["length"] >= self.slider_min_value)
            & (self.vocabulary_df["length"] <= self.slider_max_value)
        ]

        return filtered_df

    def display_word(self, word):
        """
        Display a word on the screen with current formatting options.

        Args:
            word (str): Word to display, or None if no words match filters
        """
        self.window.fill(self.WHITE)

        # Handle case when no words match the current filters
        if word is None:
            display_word = "no words"
        else:
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
        text_rect = word_text.get_rect(
            center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 4)
        )
        self.window.blit(word_text, text_rect)

        # Draw cogwheel icon (always visible)
        self.draw_cogwheel()

        # Draw settings panel (if visible)
        self.draw_settings_panel()

        pygame.display.flip()

    def handle_cogwheel_click(self, pos):
        """Handle click on the cogwheel icon."""
        if self.cogwheel_rect.collidepoint(pos):
            self.settings_visible = not self.settings_visible
            return True
        return False

    def handle_settings_panel_click(self, pos):
        """Handle clicks within the settings panel."""
        if not self.settings_visible:
            return False

        # Check if click is outside panel to close it
        if not self.settings_panel_rect.collidepoint(pos):
            self.settings_visible = False
            return True

        # Adjust position relative to panel
        panel_pos = (
            pos[0] - self.settings_panel_rect.x,
            pos[1] - self.settings_panel_rect.y,
        )

        # Check close button
        close_rect = pygame.Rect(self.PANEL_WIDTH - 25, 15, 15, 15)
        if close_rect.collidepoint(panel_pos):
            self.settings_visible = False
            return True

        # Handle settings interactions
        return self.handle_settings_interactions(panel_pos)

    def handle_settings_interactions(self, panel_pos):
        """Handle interactions with settings elements."""
        margin = self.PANEL_MARGIN

        # Use the same coordinate calculation as in drawing
        y_pos = 50  # Starting position in draw_settings_content

        # Skip to Starting Letters section (after Word Length section)
        y_pos += self.SECTION_SPACING + 75  # Word Length section height

        # Handle alphabet toggles
        toggle_y = y_pos + self.SECTION_SPACING  # Same as in draw_settings_content
        for i, letter in enumerate(self.alphabet):
            x = margin + (i % 13) * (self.box_size + 6)
            y = toggle_y + (i // 13) * (self.box_size + 6)
            toggle_rect = pygame.Rect(x, y, self.box_size, self.box_size)

            if toggle_rect.collidepoint(panel_pos):
                self.toggle_states[letter] = not self.toggle_states[letter]
                return True

        # Handle case selection
        y_pos += self.SECTION_SPACING + 85  # Skip alphabet toggles section
        case_y = y_pos + self.SECTION_SPACING  # Same as in draw_settings_content
        for i, case in enumerate(self.case_options):
            x = margin + i * 120
            radio_area = pygame.Rect(x, case_y, 100, 20)

            if radio_area.collidepoint(panel_pos):
                self.selected_case = case
                return True

        # Handle hyphenation toggle
        y_pos += self.SECTION_SPACING + 40  # Skip case selection section
        checkbox_rect = pygame.Rect(
            margin, y_pos, 18, 18
        )  # Same as in draw_settings_content
        if checkbox_rect.collidepoint(panel_pos):
            self.hyphenate_enabled = not self.hyphenate_enabled
            return True

        # Handle font size controls
        y_pos += self.SECTION_SPACING + 35  # Skip hyphenation section
        font_size_y = y_pos + self.SECTION_SPACING

        # Decrease font size button
        decrease_rect = pygame.Rect(margin, font_size_y, 30, 30)
        if decrease_rect.collidepoint(panel_pos):
            self.update_font_size(self.font_size - 10)
            return True

        # Increase font size button
        increase_rect = pygame.Rect(margin + 35, font_size_y, 30, 30)
        if increase_rect.collidepoint(panel_pos):
            self.update_font_size(self.font_size + 10)
            return True

        return False

    def handle_slider_interaction(self, pos, dragging_min, dragging_max):
        """Handle slider interactions."""
        if not self.settings_visible:
            return dragging_min, dragging_max

        # Adjust position relative to window - use same calculation as drawing
        slider_y = self.settings_panel_rect.y + 50 + self.SECTION_SPACING + 10

        # Min slider handle
        min_handle_x = (
            self.settings_panel_rect.x
            + self.PANEL_MARGIN
            + (self.slider_min_value - 4) * self.SLIDER_WIDTH // 4
        )
        min_handle_rect = pygame.Rect(min_handle_x, slider_y - 4, 8, 16)

        # Max slider handle
        max_handle_x = (
            self.settings_panel_rect.x
            + self.PANEL_MARGIN
            + 200
            + (self.slider_max_value - 4) * self.SLIDER_WIDTH // 4
        )
        max_handle_rect = pygame.Rect(max_handle_x, slider_y - 4, 8, 16)

        if min_handle_rect.collidepoint(pos):
            dragging_min = True
        elif max_handle_rect.collidepoint(pos):
            dragging_max = True

        return dragging_min, dragging_max

    def update_sliders(self, pos, dragging_min, dragging_max):
        """Update slider values during dragging."""
        if not self.settings_visible:
            return

        slider_start_x = self.settings_panel_rect.x + self.PANEL_MARGIN

        if dragging_min:
            relative_x = pos[0] - slider_start_x
            relative_x = max(0, min(relative_x, self.SLIDER_WIDTH))
            self.slider_min_value = 4 + (relative_x * 4) // self.SLIDER_WIDTH

        elif dragging_max:
            max_slider_start_x = slider_start_x + 200
            relative_x = pos[0] - max_slider_start_x
            relative_x = max(0, min(relative_x, self.SLIDER_WIDTH))
            self.slider_max_value = 4 + (relative_x * 4) // self.SLIDER_WIDTH

    def get_random_word(self):
        """
        Get a random word from the filtered vocabulary.

        Returns:
            str: Random word or None if no words match filters
        """
        filtered_df = self.get_filtered_df()
        if filtered_df.empty:
            return None
        else:
            return random.choice(filtered_df["Word"].tolist())

    def validate_word_matches_filters(self, word):
        """
        Validate that a word matches the current filter settings.

        Args:
            word (str): Word to validate

        Returns:
            bool: True if word matches current filters, False otherwise
        """
        if word is None:
            return False

        # Get active letters
        active_letters = set(
            letter.lower() for letter, state in self.toggle_states.items() if state
        )

        # Check if any letters are selected
        if not active_letters:
            return False

        # Check if word contains ONLY allowed letters (case insensitive)
        word_letters = set(word.lower())
        if not word_letters.issubset(active_letters):
            return False

        # Check word length
        word_length = len(word)
        if word_length < self.slider_min_value or word_length > self.slider_max_value:
            return False

        return True

    def get_display_word(self):
        """
        Get a word to display that is guaranteed to match current filter settings.

        This function ensures that the returned word (if any) matches the current
        letter selection and length filters. It provides additional validation
        beyond the basic filtering to prevent showing invalid words.

        Returns:
            str: A valid word matching current filters, or None if no valid words exist
        """
        # First try to get a word using the standard filtering
        candidate_word = self.get_random_word()

        # Validate the word matches our filters (double-check)
        if candidate_word is not None and self.validate_word_matches_filters(
            candidate_word
        ):
            return candidate_word

        # If validation failed, try a few more times to find a valid word
        max_attempts = 10
        for _ in range(max_attempts):
            candidate_word = self.get_random_word()
            if candidate_word is not None and self.validate_word_matches_filters(
                candidate_word
            ):
                return candidate_word

        # If we couldn't find a valid word after multiple attempts, return None
        return None

    def run(self):
        """Main application loop."""
        if self.vocabulary_df.empty:
            print(
                "Error: No vocabulary words available. Please check your word list files."
            )
            return

        dragging_min = dragging_max = False

        # Get initial word (can be None if no words match current filters)
        current_word = self.get_display_word()
        self.display_word(current_word)

        clock = pygame.time.Clock()

        while True:
            clock.tick(60)  # Limit to 60 FPS

            # Handle mouse hover for cogwheel
            mouse_pos = pygame.mouse.get_pos()
            self.cogwheel_hovered = self.cogwheel_rect.collidepoint(mouse_pos)

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return

                elif event.type == pygame.VIDEORESIZE:
                    self.handle_window_resize(event.size)
                    self.display_word(current_word)

                elif event.type == MOUSEBUTTONUP:
                    dragging_min = dragging_max = False

                elif event.type == MOUSEBUTTONDOWN:
                    # Handle cogwheel click first
                    if self.handle_cogwheel_click(event.pos):
                        self.display_word(current_word)
                        continue

                    # Handle settings panel interactions
                    if self.handle_settings_panel_click(event.pos):
                        self.display_word(current_word)
                        continue

                    # Handle slider interactions
                    dragging_min, dragging_max = self.handle_slider_interaction(
                        event.pos, dragging_min, dragging_max
                    )

                    # Click on word to get next word (only if settings not visible)
                    if not self.settings_visible:
                        # Handle click on word area (even if current_word is None)
                        display_text = (
                            current_word if current_word is not None else "no words"
                        )
                        word_rect = self.font.render(
                            display_text, True, self.BLACK
                        ).get_rect(
                            center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 4)
                        )
                        if word_rect.collidepoint(event.pos):
                            new_word = self.get_display_word()
                            current_word = new_word  # Can be None
                            self.display_word(current_word)

                elif event.type == pygame.MOUSEMOTION:
                    # Handle slider dragging
                    if dragging_min or dragging_max:
                        self.update_sliders(event.pos, dragging_min, dragging_max)
                        self.display_word(current_word)

            # Redraw if cogwheel hover state changed
            if (
                hasattr(self, "_last_cogwheel_hovered")
                and self._last_cogwheel_hovered != self.cogwheel_hovered
            ):
                self.display_word(current_word)
            self._last_cogwheel_hovered = self.cogwheel_hovered

    def close(self):
        """Clean up pygame resources."""
        pygame.quit()
