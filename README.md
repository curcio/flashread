# FlashRead

A Spanish text processing and vocabulary flashcard application that analyzes Spanish literature and creates interactive learning tools.

## Features

- **Text Processing**: Analyze Spanish text files to extract word frequencies and create vocabulary lists
- **Interactive Flashcards**: Pygame-based interface for vocabulary practice
- **Word Filtering**: Filter words by length, frequency, and starting letters
- **Syllable Hyphenation**: Spanish word syllabification using the `silabeador` library
- **Statistical Analysis**: Visualize word frequency distributions with matplotlib and seaborn
- **Multiple Case Options**: Display words in lowercase, UPPERCASE, or Title Case

## Project Structure

```
flashread/
├── process.py          # Main application with text processing and GUI
├── corpus/            # Spanish text files for analysis
│   ├── Paulo Coelho - El Alquimista.txt
│   └── J.K. Rowling - Harry Potter (Books 1-7).txt
├── 04.txt - 08.txt    # Word lists for vocabulary filtering
├── requirements.txt   # Python dependencies
└── README.md         # This file
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

3. Download NLTK data (will be done automatically on first run):
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

## Usage

### Text Processing

The application automatically processes all `.txt` files in the `corpus/` directory:

```python
# Process all files and get word frequencies
word_count = process_all('corpus')
```

### Interactive Flashcard Interface

Run the main application to start the interactive flashcard interface:

```bash
python process.py
```

The application will:
1. Set up NLTK and download required data automatically
2. Process all text files in the `corpus/` directory
3. Load and filter vocabulary from word list files (04.txt - 08.txt)
4. Launch the interactive pygame interface

### Interface Controls

- **Word Display**: Random words appear at the top of the screen
- **Next Word Button**: Click to display a new random word
- **Length Sliders**: Adjust minimum and maximum word length
- **Letter Toggles**: Enable/disable words starting with specific letters
- **Case Selection**: Choose between lowercase, UPPERCASE, or Title case
- **Hyphenation Toggle**: Show/hide syllable breaks in Spanish words

## Features in Detail

### Code Organization
- **Modular Design**: All functionality is organized into well-structured functions and classes
- **FlashCardApp Class**: Encapsulates the entire pygame interface with proper state management
- **Sequential Execution**: The main() function orchestrates all operations in logical order
- **Error Handling**: Robust error checking for missing files and empty datasets

### Text Analysis
- Removes punctuation and normalizes text
- Preserves Spanish characters (ñ, á, é, í, ó, ú, ü)
- Filters out English stopwords
- Counts word frequencies across all corpus files

### Vocabulary Filtering
- Words must appear more than 3 times in the corpus
- Configurable word length filtering
- Letter-based filtering for targeted practice
- Integration with external word lists (04.txt - 08.txt)

### Spanish Language Support
- Syllable hyphenation using `silabeador` library
- Preservation of Spanish accents and special characters
- Optimized for Spanish text processing

## Dependencies

- `nltk`: Natural language processing
- `matplotlib`: Data visualization
- `seaborn`: Statistical plotting
- `pandas`: Data manipulation
- `pygame`: Interactive GUI
- `silabeador`: Spanish syllabification

## Data Sources

The application works with Spanish literature texts including:
- Paulo Coelho's "El Alquimista"
- J.K. Rowling's Harry Potter series (Spanish translations)

## Contributing

Feel free to contribute by:
- Adding more Spanish texts to the corpus
- Improving the user interface
- Adding new analysis features
- Optimizing text processing algorithms

## License

This project is for educational purposes. Please respect copyright of the included literary works. 