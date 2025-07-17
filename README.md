# kahoot-to-anki
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](#installation)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![PyPI](https://img.shields.io/pypi/v/kahoot-to-anki.svg)

<br>

**kahoot-to-anki** is a command-line tool that converts exported Kahoot quiz reports (`.xlsx` files) into Anki flashcard decks (`.apkg` format).<br>
Designed for educators, students, and any self-learners to easily turn quiz results into effective spaced‑repetition decks.

## Installation & Usage
### Option 1: Install via pip
```
pip install kahoot-to-anki
```
Then run:
```
kahoot-to-anki --help
```
Example: Process all Kahoot Exports in the `./exports/` folder and write the flashcard deck and CSV file to `./data/`:
```
kahoot-to-anki --inp "./exports" --out "./data" --csv
```

### Option 2: Run with Docker
You can run **kahoot-to-anki** in a Docker container in three ways:

#### A) Build Image from Source Code (Clone Repo)
```
# Clone Repository
git clone https://github.com/SimonHRD/kahoot-to-anki.git

# Move into Repository
cd kahoot-to-anki

# Build docker image with the kahoot-to-anki tag
docker build -t kahoot-to-anki .

# Check help command
docker run --rm kahoot-to-anki --help

# Run with local data
docker run --rm -v "$(pwd)/data:/app/data" kahoot-to-anki \
  --inp "./data" --out "./data" --csv
```

On PowerShell:
```
docker run --rm -v ${PWD}\data:/app/data kahoot-to-anki \
  --inp "./data" --out "./data" --csv
```

#### B) Use a Minimal Dockerfile That Installs from PyPI
It is not needed to clone the repository, you can just create a minimal Dockerfile:
```Dockerfile
FROM python:3.13-slim

WORKDIR /app
RUN pip install kahoot-to-anki
ENTRYPOINT ["kahoot-to-anki"]
```
Then run:
```bash
# Build the image
docker build -t kahoot-to-anki-pypi .

# Run the tool
docker run --rm -v "$(pwd)/data:/app/data" kahoot-to-anki-pypi \
  --inp "./data" --out "./data" --csv
```

On PowerShell:
```
docker run --rm -v ${PWD}\data:/app/data kahoot-to-anki-pypi \
  --inp "./data" --out "./data" --csv
```

#### C) Run Without a Dockerfile (Install from PyPI at Runtime)
If you want to avoid writing a Dockerfile, just run the CLI directly from a fresh Python container. This method downloads everything at runtime in a temporary container. No files or installed packages will persist after the container exits.

```bash
docker run --rm -v "$(pwd)/data:/app/data" python:3.13-slim \
  sh -c "pip install kahoot-to-anki && kahoot-to-anki --out ./data --csv"
```

On PowerShell:
```
docker run --rm -v ${PWD}\data:/app/data python:3.13-slim `
  sh -c "pip install kahoot-to-anki && kahoot-to-anki --out ./data --csv"

```

## CLI Arguments
You can provide either a single Kahoot Excel file or a directory containing multiple `.xlsx` files as input.<br>
All valid Excel files in the directory will be processed.

| Argument             | Description                                                                    |
|----------------------|--------------------------------------------------------------------------------|
| `-i`, `--inp`        | Path to the input Excel file or directory (default: `./data`)                  |
| `-o`, `--out`        | Path to the output directory for the Anki deck (default: `./`)                 |
| `--sheet`            | The Excel Sheet with the raw Kahoot quiz data (default: `RawReportData Data`)  |    
| `--csv`, `--no-csv`  | Enable or disable CSV export of the questions (default: disabled)              |
| `-t`, `--title`      | Title of the generated Anki deck (default: `"Kahoot"`)                         |
| `--version`          | Show the version of the installed kahoot-to-anki package                       |


## Example
An example Kahoot export file is available in `data/`. The generated deck will be saved as `anki.apkg` in the specified `--out` directory (default: `./`).

## License
MIT — see [LICENSE](./LICENSE)
