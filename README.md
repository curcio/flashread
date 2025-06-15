# FlashRead

A Spanish text processing and vocabulary flashcard application that analyzes Spanish literature and creates interactive learning tools.

## Features

- **Text Processing**: Analyze Spanish text files to extract word frequencies and create vocabulary lists
- **Interactive Flashcards**: Pygame-based interface for vocabulary practice
- **Word Filtering**: Filter words by length, frequency, and starting letters
- **Syllable Hyphenation**: Spanish word syllabification using the `silabeador` library
- **Statistical Analysis**: Visualize word frequency distributions with matplotlib and seaborn
- **Multiple Case Options**: Display words in lowercase, UPPERCASE, or Title Case
- **Data Persistence**: Save and load processed data for faster startup
- **Command-Line Interface**: Easy-to-use CLI for data generation and app launching

## Project Structure

```
flashread/
├── src/                          # Source code modules
│   ├── __init__.py              # Package initialization
│   ├── cli.py                   # Command-line interface
│   ├── text_processor.py        # Text processing and vocabulary management
│   ├── flashcard_app.py         # Pygame flashcard interface
│   └── utils.py                 # Shared utilities
├── data/                        # Generated data files
│   ├── word_frequencies.csv     # Processed word counts
│   ├── vocabulary.csv           # Filtered vocabulary
│   └── plots/                   # Generated visualizations
├── corpus/                      # Spanish text files for analysis
│   ├── Paulo Coelho - El Alquimista.txt
│   └── J.K. Rowling - Harry Potter (Books 1-7).txt
├── 04.txt - 08.txt             # Word lists for vocabulary filtering
├── flashread.py                # Main entry point
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd flashread
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. NLTK data will be downloaded automatically on first run.

## Usage

FlashRead now provides a modern command-line interface with two main commands:

### Generate Vocabulary Data

Process corpus files and generate vocabulary data:

```bash
# Basic generation
python flashread.py generate

# Generate with frequency plot
python flashread.py generate --plot

# Use custom parameters
python flashread.py generate --min-frequency 5 --corpus-dir my_corpus --data-dir my_data

# Force regeneration of existing data
python flashread.py generate --force
```

**Generate Command Options:**
- `--corpus-dir`: Directory containing text files (default: `corpus`)
- `--data-dir`: Directory for saving processed data (default: `data`)
- `--min-frequency`: Minimum word frequency for vocabulary inclusion (default: 3)
- `--plot`: Generate and display word frequency plot
- `--force`: Force reprocessing even if data files exist

### Launch Flashcard Interface

Run the interactive pygame flashcard application:

```bash
# Basic launch
python flashread.py run

# Use custom data directory
python flashread.py run --data-dir my_data

# Use specific vocabulary file
python flashread.py run --vocabulary custom_vocab.csv
```

**Run Command Options:**
- `--data-dir`: Directory containing processed data (default: `data`)
- `--vocabulary`: Vocabulary file to use (default: `vocabulary.csv`)
- `--corpus-dir`: Corpus directory (used if vocabulary needs generation)

### Interface Controls

- **Word Display**: Random words appear at the top of the screen
- **Next Word**: Click on the word to display a new random word
- **Length Sliders**: Adjust minimum and maximum word length
- **Letter Toggles**: Enable/disable words starting with specific letters
- **Case Selection**: Choose between lowercase, UPPERCASE, or Title case
- **Hyphenation Toggle**: Show/hide syllable breaks in Spanish words

## Architecture

### Class-Based Design

FlashRead uses a clean, object-oriented architecture:

**TextProcessor Class** (`src/text_processor.py`):
- File processing and text analysis
- Word frequency calculation
- Vocabulary DataFrame creation
- Statistical analysis and plotting
- Data persistence (save/load processed data)

**FlashCardApp Class** (`src/flashcard_app.py`):
- Pygame interface and UI management
- Word display and formatting
- User interaction handling
- Application state management

**FlashReadCLI Class** (`src/cli.py`):
- Command-line argument parsing
- Orchestrates text processing and app launching
- Progress reporting and error handling

### Data Management

- **Persistent Storage**: Generated files are stored in the `data/` directory
- **Cached Processing**: Word frequencies and vocabulary are saved to avoid reprocessing
- **Incremental Updates**: Only reprocess when forced or when source files change
- **Organized Output**: Plots and data files are systematically organized

## Advanced Usage

### Custom Word Lists

You can use custom word list files by placing them as `04.txt` through `08.txt` in the project root. These files should contain one word per line and will be filtered against the corpus word frequencies.

### Data Analysis

Generate detailed frequency analysis:

```python
from src.text_processor import TextProcessor

processor = TextProcessor()
processor.process_all_corpus_files()
processor.plot_word_frequencies(top_n=50, save_plot=True)
stats = processor.get_vocabulary_stats()
print(stats)
```

### Custom Vocabulary Creation

Create vocabulary with different frequency thresholds:

```python
processor = TextProcessor()
processor.load_word_frequencies()  # Load existing frequencies
vocab_df = processor.create_vocabulary_dataframe(min_frequency=10)
processor.save_vocabulary('high_frequency_vocab.csv')
```

## Dependencies

- `nltk`: Natural language processing
- `matplotlib`: Data visualization
- `seaborn`: Statistical plotting
- `pandas`: Data manipulation
- `pygame`: Interactive GUI
- `silabeador`: Spanish syllabification

## Development

### Running Tests

```bash
# Test data generation
python flashread.py generate --corpus-dir corpus --data-dir test_data

# Test flashcard interface
python flashread.py run --data-dir test_data
```

### Adding New Features

The modular architecture makes it easy to extend:

1. **Text Processing**: Add methods to `TextProcessor` class
2. **UI Features**: Extend `FlashCardApp` class
3. **CLI Commands**: Add new subparsers to `FlashReadCLI`
4. **Utilities**: Add shared functions to `utils.py`

## Data Sources

The application works with Spanish literature texts including:
- Paulo Coelho's "El Alquimista"
- J.K. Rowling's Harry Potter series (Spanish translations)

## Performance

- **Efficient Processing**: Text files are processed once and cached
- **Smart Loading**: Only loads necessary data for each operation  
- **Memory Management**: Large datasets are handled efficiently with pandas
- **Responsive UI**: Pygame interface maintains 60 FPS performance

## Contributing

Feel free to contribute by:
- Adding more Spanish texts to the corpus
- Improving the user interface
- Adding new analysis features
- Optimizing text processing algorithms
- Adding tests and documentation

## License

This project is for educational purposes. Please respect copyright of the included literary works. 