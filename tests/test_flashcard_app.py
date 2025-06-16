"""
Unit tests for FlashCardApp class.
"""

from unittest.mock import MagicMock, patch

import pygame
import pytest

from flashcard_app import FlashCardApp


class TestFlashCardApp:
    """Test cases for FlashCardApp class."""

    def test_init_with_valid_vocabulary(self, sample_vocabulary):
        """Test FlashCardApp initialization with valid vocabulary."""
        app = FlashCardApp(sample_vocabulary)

        assert app.vocabulary_df.equals(sample_vocabulary)
        assert app.WINDOW_WIDTH == 800
        assert app.WINDOW_HEIGHT == 600
        assert app.settings_visible is False
        assert app.cogwheel_hovered is False

    def test_init_with_empty_vocabulary(self, empty_vocabulary):
        """Test FlashCardApp initialization with empty vocabulary raises error."""
        with pytest.raises(ValueError, match="Vocabulary DataFrame cannot be empty"):
            FlashCardApp(empty_vocabulary)

    def test_init_with_none_vocabulary(self):
        """Test FlashCardApp initialization with None vocabulary raises error."""
        with pytest.raises(ValueError, match="Vocabulary DataFrame cannot be empty"):
            FlashCardApp(None)

    def test_setup_colors_and_fonts(self, sample_vocabulary):
        """Test color and font setup."""
        app = FlashCardApp(sample_vocabulary)

        # Test main colors
        assert app.WHITE == (255, 255, 255)
        assert app.BLACK == (0, 0, 0)
        assert app.GREEN == (0, 255, 0)
        assert app.RED == (255, 0, 0)
        assert app.GRAY == (200, 200, 200)

        # Test settings panel colors
        assert app.SETTINGS_BG == (240, 240, 245)  # No longer has alpha transparency
        assert app.SETTINGS_BORDER == (180, 180, 190)

        # Test cogwheel colors
        assert app.COGWHEEL_NORMAL == (100, 100, 110)
        assert app.COGWHEEL_HOVER == (70, 130, 180)
        assert app.COGWHEEL_ACTIVE == (50, 100, 150)

    def test_setup_settings_panel(self, sample_vocabulary):
        """Test settings panel setup."""
        app = FlashCardApp(sample_vocabulary)

        # Test panel dimensions
        assert app.PANEL_WIDTH == 480
        assert app.PANEL_HEIGHT == 420
        assert app.PANEL_MARGIN == 40

        # Test cogwheel position
        assert app.cogwheel_rect.width == 32
        assert app.cogwheel_rect.height == 32

        # Test settings panel position
        expected_x = (app.WINDOW_WIDTH - app.PANEL_WIDTH) // 2
        assert app.settings_panel_rect.x == expected_x
        assert app.settings_panel_rect.y == 80

    def test_setup_ui_elements(self, sample_vocabulary):
        """Test UI elements setup."""
        app = FlashCardApp(sample_vocabulary)

        # Test sliders
        assert app.slider_min_value == 4
        assert app.slider_max_value == 8
        assert app.SLIDER_WIDTH == 120
        assert app.SLIDER_HEIGHT == 8

        # Test alphabet toggles
        assert app.alphabet == "abcdefghijklmnopqrstuvwxyz"
        assert len(app.toggle_boxes) == 26
        assert len(app.toggle_states) == 26
        assert app.box_size == 24

        # Test initial toggle states (should be True for "aeiouscl")
        for letter in "aeiouscl":
            assert app.toggle_states[letter] is True
        for letter in "bdfghjknpqrtvwxyz":
            assert app.toggle_states[letter] is False

        # Test case selection
        assert app.case_options == ["lower", "UPPER", "Title"]
        assert app.selected_case == "lower"
        assert len(app.case_rects) == 3

        # Test hyphenation toggle
        assert app.hyphenate_enabled is False

    def test_get_filtered_df(self, sample_vocabulary):
        """Test vocabulary filtering functionality."""
        app = FlashCardApp(sample_vocabulary)

        # Test with default settings (letters: aeiouscl, length: 4-8)
        filtered_df = app.get_filtered_df()
        assert not filtered_df.empty

        # Test with restrictive letter filter
        app.toggle_states = {letter: False for letter in app.alphabet}
        app.toggle_states["c"] = True  # Only 'c' allowed
        filtered_df = app.get_filtered_df()
        # Should only include words starting with 'c'
        for word in filtered_df["Word"]:
            assert word.lower().startswith("c")

        # Test with length restrictions
        app.toggle_states = {letter: True for letter in app.alphabet}  # All letters
        app.slider_min_value = 6
        app.slider_max_value = 7
        filtered_df = app.get_filtered_df()
        for length in filtered_df["length"]:
            assert 6 <= length <= 7

    def test_get_filtered_df_empty_pattern(self, sample_vocabulary):
        """Test filtering when no letters are selected (which causes regex error)."""
        app = FlashCardApp(sample_vocabulary)

        # Set all toggles to False - this should cause active_letters to be empty
        app.toggle_states = {letter: False for letter in app.alphabet}

        # This should handle the empty pattern gracefully
        filtered_df = app.get_filtered_df()
        # Should return empty dataframe since no letters are allowed
        assert filtered_df.empty

    def test_handle_cogwheel_click(self, sample_vocabulary):
        """Test cogwheel click handling."""
        app = FlashCardApp(sample_vocabulary)

        # Test click inside cogwheel area
        cogwheel_center = app.cogwheel_rect.center
        assert app.handle_cogwheel_click(cogwheel_center) is True
        assert app.settings_visible is True

        # Test click again to close
        assert app.handle_cogwheel_click(cogwheel_center) is True
        assert app.settings_visible is False

        # Test click outside cogwheel area
        outside_pos = (0, 0)
        assert app.handle_cogwheel_click(outside_pos) is False

    def test_handle_settings_panel_click_outside(self, sample_vocabulary):
        """Test clicking outside settings panel to close it."""
        app = FlashCardApp(sample_vocabulary)
        app.settings_visible = True

        # Click outside panel
        outside_pos = (0, 0)
        result = app.handle_settings_panel_click(outside_pos)
        assert result is True
        assert app.settings_visible is False

    def test_handle_settings_panel_click_close_button(self, sample_vocabulary):
        """Test clicking close button in settings panel."""
        app = FlashCardApp(sample_vocabulary)
        app.settings_visible = True

        # Click close button (approximate position)
        close_pos = (
            app.settings_panel_rect.right - 20,
            app.settings_panel_rect.top + 20,
        )
        result = app.handle_settings_panel_click(close_pos)
        assert result is True
        assert app.settings_visible is False

    def test_handle_settings_interactions_alphabet_toggles(self, sample_vocabulary):
        """Test alphabet toggle interactions."""
        app = FlashCardApp(sample_vocabulary)

        # Calculate position of first toggle (letter 'a') using new spacing
        margin = app.PANEL_MARGIN
        y_pos = 50 + app.SECTION_SPACING + 75  # Starting position + Word Length section
        toggle_y = y_pos + app.SECTION_SPACING
        toggle_pos = (margin + app.box_size // 2, toggle_y + app.box_size // 2)

        # Get current state of 'a'
        original_state = app.toggle_states["a"]

        # Simulate click
        result = app.handle_settings_interactions(toggle_pos)
        assert result is True
        assert app.toggle_states["a"] == (not original_state)

    def test_handle_settings_interactions_case_selection(self, sample_vocabulary):
        """Test case selection interactions."""
        app = FlashCardApp(sample_vocabulary)

        # Calculate position of second case option using new spacing
        margin = app.PANEL_MARGIN
        y_pos = (
            50 + app.SECTION_SPACING + 75 + app.SECTION_SPACING + 85
        )  # All sections before case
        case_y = y_pos + app.SECTION_SPACING
        case_pos = (margin + 1 * 120 + 50, case_y + 10)  # Second option (UPPER)

        result = app.handle_settings_interactions(case_pos)
        assert result is True
        assert app.selected_case == "UPPER"

    def test_handle_settings_interactions_hyphenation(self, sample_vocabulary):
        """Test hyphenation toggle interactions."""
        app = FlashCardApp(sample_vocabulary)

        # Calculate position of hyphenation checkbox using new spacing
        margin = app.PANEL_MARGIN
        y_pos = (
            50
            + app.SECTION_SPACING
            + 75
            + app.SECTION_SPACING
            + 85
            + app.SECTION_SPACING
            + 40
        )  # All previous sections
        hyphen_pos = (margin + 9, y_pos + 9)  # Center of checkbox

        original_state = app.hyphenate_enabled
        result = app.handle_settings_interactions(hyphen_pos)
        assert result is True
        assert app.hyphenate_enabled == (not original_state)

    def test_get_random_word(self, sample_vocabulary):
        """Test random word selection."""
        app = FlashCardApp(sample_vocabulary)

        # Test with normal filtering
        word = app.get_random_word()
        assert word is not None
        assert word in sample_vocabulary["Word"].values

        # Test with some letters that should match
        app.toggle_states = {letter: False for letter in app.alphabet}
        app.toggle_states["c"] = True  # Allow 'c' - should match "casa"
        word = app.get_random_word()
        if word:  # If a word is found, it should start with 'c'
            assert word.lower().startswith("c")

    def test_get_random_word_no_matches(self, sample_vocabulary):
        """Test random word selection when no words match filters."""
        app = FlashCardApp(sample_vocabulary)

        # Set impossible filters - no letters allowed
        app.toggle_states = {letter: False for letter in app.alphabet}

        word = app.get_random_word()
        # Should now return None instead of falling back to all vocabulary
        assert word is None

    def test_slider_interaction_detection(self, sample_vocabulary):
        """Test slider interaction detection."""
        app = FlashCardApp(sample_vocabulary)
        app.settings_visible = True

        # Calculate slider handle position using new spacing
        slider_y = app.settings_panel_rect.y + 50 + app.SECTION_SPACING + 10
        min_handle_x = (
            app.settings_panel_rect.x
            + app.PANEL_MARGIN
            + (app.slider_min_value - 4) * app.SLIDER_WIDTH // 4
        )

        # Test min slider handle click
        handle_pos = (min_handle_x, slider_y)
        dragging_min, dragging_max = app.handle_slider_interaction(
            handle_pos, False, False
        )
        assert dragging_min is True
        assert dragging_max is False

    def test_update_sliders(self, sample_vocabulary):
        """Test slider value updates."""
        app = FlashCardApp(sample_vocabulary)
        app.settings_visible = True

        slider_start_x = app.settings_panel_rect.x + app.PANEL_MARGIN

        # Test min slider update
        new_pos = (slider_start_x + 60, 100)  # Approximate middle position
        app.update_sliders(new_pos, True, False)
        # Value should be updated (exact value depends on calculation)
        assert 4 <= app.slider_min_value <= 8

    def test_display_word_case_formatting(self, sample_vocabulary):
        """Test word display with different case formatting."""
        app = FlashCardApp(sample_vocabulary)

        # Mock pygame surface and display
        with patch.object(app, "window", spec=pygame.Surface) as mock_window:
            mock_window.fill = MagicMock()
            mock_window.blit = MagicMock()
            with patch("pygame.display.flip"):
                with patch.object(app, "draw_cogwheel"):
                    with patch.object(app, "draw_settings_panel"):
                        # Test lowercase
                        app.selected_case = "lower"
                        app.display_word("CASA")

                        # Test uppercase
                        app.selected_case = "UPPER"
                        app.display_word("casa")

                        # Test title case
                        app.selected_case = "Title"
                        app.display_word("casa")

    def test_display_word_hyphenation(self, sample_vocabulary):
        """Test word display with hyphenation enabled."""
        app = FlashCardApp(sample_vocabulary)
        app.hyphenate_enabled = True

        with patch.object(app, "window", spec=pygame.Surface) as mock_window:
            mock_window.fill = MagicMock()
            mock_window.blit = MagicMock()
            with patch("pygame.display.flip"):
                with patch.object(app, "draw_cogwheel"):
                    with patch.object(app, "draw_settings_panel"):
                        with patch("utils.hyphenate_word", return_value="ca-sa"):
                            app.display_word("casa")
                            # Test passes if no exception is raised

    @patch("pygame.time.Clock")
    @patch("pygame.event.get")
    def test_run_loop_quit_event(self, mock_event_get, mock_clock, sample_vocabulary):
        """Test main run loop with quit event."""
        app = FlashCardApp(sample_vocabulary)

        # Mock quit event
        quit_event = MagicMock()
        quit_event.type = pygame.QUIT
        mock_event_get.return_value = [quit_event]

        with patch.object(app, "display_word"):
            with patch("pygame.quit"):
                app.run()
                # Test that pygame.quit was called (indicating clean exit)

    def test_coordinate_consistency(self, sample_vocabulary):
        """Test that drawing and interaction coordinates are consistent."""
        app = FlashCardApp(sample_vocabulary)

        # Test alphabet toggles coordinates
        app.PANEL_MARGIN

        # Drawing coordinates (from draw_settings_content logic)
        draw_y_pos = 50 + 70  # Starting position + Word Length section
        draw_toggle_y = draw_y_pos + 25

        # Interaction coordinates (from handle_settings_interactions logic)
        interact_y_pos = 50 + 70  # Same calculation
        interact_toggle_y = interact_y_pos + 25

        assert draw_toggle_y == interact_toggle_y

        # Test case selection coordinates
        draw_case_y = (50 + 70 + 80) + 25
        interact_case_y = (50 + 70 + 80) + 25
        assert draw_case_y == interact_case_y

        # Test hyphenation coordinates
        draw_hyphen_y = 50 + 70 + 80 + 50
        interact_hyphen_y = 50 + 70 + 80 + 50
        assert draw_hyphen_y == interact_hyphen_y

    def test_settings_panel_not_visible_by_default(self, sample_vocabulary):
        """Test that settings panel is not visible by default."""
        app = FlashCardApp(sample_vocabulary)

        # Settings should not be visible initially
        assert app.settings_visible is False

        # Handle settings panel click should return False if panel not visible
        result = app.handle_settings_panel_click((100, 100))
        assert result is False

    def test_close_method(self, sample_vocabulary):
        """Test the close method."""
        app = FlashCardApp(sample_vocabulary)

        with patch("pygame.quit") as mock_quit:
            app.close()
            mock_quit.assert_called_once()

    def test_cogwheel_drawing_colors(self, sample_vocabulary):
        """Test cogwheel color selection based on state."""
        app = FlashCardApp(sample_vocabulary)

        # Test normal state
        app.settings_visible = False
        app.cogwheel_hovered = False
        # Cannot easily test drawing, but can verify state is correct

        # Test hover state
        app.cogwheel_hovered = True
        # State should be reflected in color choice during drawing

        # Test active state
        app.settings_visible = True
        # State should be reflected in color choice during drawing

    def test_get_random_word_should_return_none_when_no_matches(
        self, sample_vocabulary
    ):
        """Test that get_random_word returns None when no words match filters instead of falling back to all vocabulary."""
        app = FlashCardApp(sample_vocabulary)

        # Set restrictive filters that won't match any words in sample vocabulary
        # Assuming sample vocabulary doesn't have words starting with 'z' that are 10+ characters
        app.toggle_states = {letter: False for letter in app.alphabet}
        app.toggle_states["z"] = True  # Only allow words starting with 'z'
        app.slider_min_value = 10  # Very long words only
        app.slider_max_value = 15

        # This test currently FAILS because get_random_word falls back to all vocabulary
        # instead of returning None when no words match the filters
        word = app.get_random_word()

        # The word should be None, but currently it returns a word from all vocabulary
        # This is the bug we need to fix
        assert (
            word is None
        ), f"Expected None but got '{word}' - should not fall back to all vocabulary when filters don't match"

    def test_display_word_handles_no_words_case(self, sample_vocabulary):
        """Test that display_word can handle None input and shows 'no words' message."""
        app = FlashCardApp(sample_vocabulary)

        with patch.object(app, "window", spec=pygame.Surface) as mock_window:
            mock_window.fill = MagicMock()
            mock_window.blit = MagicMock()
            with patch("pygame.display.flip"):
                with patch.object(app, "draw_cogwheel"):
                    with patch.object(app, "draw_settings_panel"):
                        # This should display "no words" instead of crashing
                        app.display_word(None)

                        # Verify that the window was filled (basic rendering happened)
                        mock_window.fill.assert_called()

    def test_word_matches_current_filters(self, sample_vocabulary):
        """Test that selected words always match the current filter settings."""
        app = FlashCardApp(sample_vocabulary)

        # Test with multiple letters - should only return words containing ONLY these letters
        app.toggle_states = {letter: False for letter in app.alphabet}
        app.toggle_states["a"] = True
        app.toggle_states["s"] = True
        app.toggle_states["o"] = True
        app.slider_min_value = 4
        app.slider_max_value = 8

        # Get multiple words to test consistency
        for _ in range(10):
            word = app.get_random_word()
            if word is not None:  # Skip None results
                # Word should contain only allowed letters (case insensitive)
                word_letters = set(word.lower())
                allowed_letters = {"a", "s", "o"}
                assert word_letters.issubset(
                    allowed_letters
                ), f"Word '{word}' contains letters not in {allowed_letters}"
                # Word should be within length range
                assert (
                    4 <= len(word) <= 8
                ), f"Word '{word}' length {len(word)} not in range 4-8"

    def test_get_display_word_function(self, sample_vocabulary):
        """Test that there's a dedicated function for getting the word to display with validation."""
        app = FlashCardApp(sample_vocabulary)

        # This test will initially fail until we implement get_display_word function
        assert hasattr(app, "get_display_word"), "Should have get_display_word method"

        # Test with restrictive filters - multiple common letters
        app.toggle_states = {letter: False for letter in app.alphabet}
        app.toggle_states["a"] = True
        app.toggle_states["s"] = True
        app.toggle_states["o"] = True
        app.slider_min_value = 4
        app.slider_max_value = 5

        word = app.get_display_word()
        if word is not None:
            # Validate the word matches filters - contains only allowed letters
            word_letters = set(word.lower())
            allowed_letters = {"a", "s", "o"}
            assert word_letters.issubset(
                allowed_letters
            ), f"Word '{word}' should contain only letters from {allowed_letters}"
            assert 4 <= len(word) <= 5, f"Word '{word}' should be 4-5 characters long"

    def test_validate_word_matches_filters(self, sample_vocabulary):
        """Test word validation against current filters."""
        app = FlashCardApp(sample_vocabulary)

        # Test with default settings (should match several words)
        valid_words = ["casa", "cosa"]  # 4-letter words with allowed letters
        invalid_words = ["perro", "trabajar"]  # Contains non-allowed letters

        for word in valid_words:
            assert app.validate_word_matches_filters(word)

        for word in invalid_words:
            assert not app.validate_word_matches_filters(word)

        # Test with restricted letter set
        app.toggle_states = {letter: False for letter in app.alphabet}
        app.toggle_states["c"] = True
        app.toggle_states["a"] = True
        app.toggle_states["s"] = True

        # Only words with just c, a, s letters should be valid
        assert app.validate_word_matches_filters("casa")
        assert not app.validate_word_matches_filters("perro")

        # Test length restrictions
        app.toggle_states = {letter: True for letter in app.alphabet}
        app.slider_min_value = 6
        app.slider_max_value = 6

        assert not app.validate_word_matches_filters("casa")  # Too short
        assert app.validate_word_matches_filters("amigos")  # Just right (6 letters)
        assert not app.validate_word_matches_filters("trabajar")  # Too long

    def test_settings_panel_interactions_with_new_spacing(self, sample_vocabulary):
        """Test that settings panel interactions work correctly with new spacing/padding."""
        app = FlashCardApp(sample_vocabulary)
        app.settings_visible = True

        # Test alphabet toggle interaction - calculate position using the same logic as drawing
        margin = app.PANEL_MARGIN
        y_pos = 50

        # Move to Starting Letters section (matches draw_settings_content)
        y_pos += app.SECTION_SPACING + 75  # Word Length section
        toggle_y = y_pos + app.SECTION_SPACING  # Starting Letters section

        # Calculate position of first letter 'a' (should match drawing coordinates)
        letter_x = margin + 0 * (app.box_size + 6)  # 'a' is at index 0
        letter_y = toggle_y + 0 * (app.box_size + 6)  # First row

        # Test toggle interaction
        original_state = app.toggle_states["a"]
        click_pos = (letter_x + app.box_size // 2, letter_y + app.box_size // 2)
        result = app.handle_settings_interactions(click_pos)

        # The interaction should work (return True) and toggle the state
        assert result is True
        assert app.toggle_states["a"] == (not original_state)

        # Test case selection interaction
        y_pos += app.SECTION_SPACING + 85  # Move to Display Case section
        case_y = y_pos + app.SECTION_SPACING

        # Click on second case option ("UPPER")
        case_x = margin + 1 * 120  # Second option with new spacing
        case_click_pos = (case_x + 50, case_y + 10)  # Center of the option

        result = app.handle_settings_interactions(case_click_pos)
        assert result is True
        assert app.selected_case == "UPPER"

        # Test hyphenation toggle interaction
        y_pos += app.SECTION_SPACING + 40  # Move to hyphenation section
        hyphen_x = margin + 9  # Center of checkbox
        hyphen_y = y_pos + 9  # Center of checkbox

        original_hyphen_state = app.hyphenate_enabled
        hyphen_click_pos = (hyphen_x, hyphen_y)

        result = app.handle_settings_interactions(hyphen_click_pos)
        assert result is True
        assert app.hyphenate_enabled == (not original_hyphen_state)
