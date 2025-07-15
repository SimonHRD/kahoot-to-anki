# kahoot-to-anki
`kahoot-to-anki` is a simple CLI tool to convert exported Kahoot quiz reports into fully usable Anki flashcards (`.apkg` files). <br>
Perfect for students, teachers, and anyone who wants to review quiz material with Anki.

## Installation
### Option 1: Install via pip
```
pip install kahoot-to-anki
```
Then run:
```
kahoot-to-anki --help
```

### Option 2: Run with Docker
```
# Clone Repository
git clone https://github.com/SimonHRD/kahoot-to-anki.git

# Move into Repository
cd kahoot-to-anki

# Build docker image with the kahoot-to-anki tag
docker build -t kahoot-to-anki .

# Check help command
docker run --rm -v "$(pwd)/data:/app/data" kahoot-to-anki --help

# Run with local data
docker run --rm -v "$(pwd)/data:/app/data" kahoot-to-anki --out "./data" --csv
```

On PowerShell:
```
docker run --rm -v ${PWD}\data:/app/data kahoot-to-anki --out "./data" --csv
```

## CLI Usage

| Argument            | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `-i`, `--inp`        | Path to the input Excel file or directory (default: `./data`)               |
| `-o`, `--out`        | Path to the output directory for the Anki deck (default: `./`)              |
| `--csv`, `--no-csv`  | Enable or disable CSV export of the questions (default: disabled)           |
| `-t`, `--title`      | Title of the generated Anki deck (default: `"Kahoot"`)                      |


## Example
An example Kahoot export file is available in `data/`. The generated deck will be saved as `anki.apkg` in the specified `--out` directory (default: `./`).

## License
MIT — see [LICENSE](./LICENSE)
