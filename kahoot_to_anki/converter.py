# Standard library imports
import argparse
import logging
import os
import glob
from typing import Iterator, Optional
from dataclasses import dataclass

# Third-party library imports
import genanki
import pandas as pd

# Configure logging settings
logging.basicConfig(level=logging.INFO)

# Constants
DEFAULT_INPUT_DIRECTORY = "./data"
DEFAULT_OUTPUT_DIRECTORY = "./"
DEFAULT_DECK_TITLE = "Kahoot"
KAHOOT_EXCEL_SHEET_NAME_RAW_DATA = "RawReportData Data"

# Dataclass to hold CLI arguments
@dataclass
class CLIArgs:
    input_path: str
    output_path: str
    export_csv: bool
    deck_title: str


def main() -> None:
    # Check command line arguments
    args = get_commandline_arguments()

    validation(args.input_path, args.output_path)

    df = get_questions(args.input_path)

    if args.export_csv:
        df.to_csv(
            os.path.join(args.output_path, "kahoot.csv"),
            sep=";",
            index=False,
            encoding="utf-8-sig",
        )
        
    make_anki(df, args.output_path, args.deck_title)


def get_commandline_arguments() -> CLIArgs:
    """
    Parses the command line arguments and returns a CLIArgs dataclass instance.

    :return: A CLIArgs dataclass instance
    :rtype: CLIArgs
    """
    parser = argparse.ArgumentParser(description="Create Anki Deck from Kahoot answer")
    parser.add_argument(
        "-i",
        "--inp",
        default=DEFAULT_INPUT_DIRECTORY,
        help=f"Path to the directory containing input Excel files or a single input Excel file. If a directory is "
        f"provided, all Excel files in the directory will be processed. Default: {DEFAULT_INPUT_DIRECTORY}",
        type=str,
    )
    parser.add_argument(
        "-o",
        "--out",
        default=DEFAULT_OUTPUT_DIRECTORY,
        help="Path to the directory where the Anki flashcards package will be generated. "
        "If not specified, the package will be created in the current working directory.",
        type=str,
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Generate a CSV file with the question data.",
    )
    parser.add_argument(
        "-t",
        "--title",
        default=DEFAULT_DECK_TITLE,
        help="Name of the Anki deck to be created. "
        f"If not specified, the default deck name '{DEFAULT_DECK_TITLE}' will be used.",
        type=str,
    )
    args = parser.parse_args()

    return CLIArgs(
        input_path=os.path.abspath(args.inp),
        output_path=os.path.abspath(args.out),
        export_csv=args.csv,
        deck_title=args.title
    )


def validation(input_directory: str, output_directory: str) -> None:
    """
    This function validates the command line arguments, checking if the input path is a valid Excel file or directory
    and if the output path is a valid directory.
    The input path needs to be an Excel file or a directory that contains Excel files.
    The output path needs to be a directory and not a file.

    :param input_directory: The path of the input Excel or directory
    :param output_directory: The path of the output directory
    :return: None
    :rtype: None
    """
    # Check if input is a file
    if not os.path.exists(input_directory):
        logging.error(f"Input directory {input_directory} does not exist!")
        raise FileNotFoundError(f"Input directory {input_directory} does not exist!")
    elif (
        os.path.isfile(input_directory)
        and os.path.splitext(input_directory)[-1] != ".xlsx"
    ):
        logging.error("Input file is not an excel file!")
        raise ValueError("Input file is not an excel file!")
    elif os.path.isdir(input_directory):
        input_excels = os.path.join(input_directory, "*.xlsx")
        if not glob.glob(input_excels):
            logging.error("Input directory does not contain any excel files!")
            raise FileNotFoundError("Input directory does not contain any excel files!")

    # Check output directory and create when not existing
    if not os.path.isdir(output_directory):
        logging.error("Output is not a directory!")
        raise ValueError("Output is not a directory!")
    if not os.path.exists(output_directory):
        try:
            os.makedirs(output_directory)
        except OSError as e:
            logging.error(
                "Failed to create output directory '%s': %s", output_directory, str(e)
            )
            raise


def get_questions(input_directory: str) -> pd.DataFrame:
    """
    Extracts all the kahoot questions out of the Excel file(s)

    :param input_directory: The path to the input directory or Excel file
    :return: All the questions with the possible answers and the solution
    :rtype: pd.DataFrame
    """

    def get_excels(path: str) -> Iterator[str]:
        """
        Returns a list with all Excels in the given path
        :param path: the path to an Excel file or a directory with Excel files
        :return: a list with all excels
        """
        if os.path.isfile(path):
            yield path
        else:
            yield from glob.glob(os.path.join(input_directory, "*.xlsx"))
            return [f for f in glob.glob(os.path.join(path, "*.xlsx"))]

    def get_excel_data(excel_file: str) -> Optional[pd.DataFrame]:
        """
        Returns a pd.DataFrame with the kahoot raw data
        :param excel_file: an Excel file with Kahoot raw data
        :return: a DataFrame with the data
        """
        try:
            # read file
            return pd.read_excel(
                excel_file, sheet_name=KAHOOT_EXCEL_SHEET_NAME_RAW_DATA
            )
        except ValueError:
            logging.warning(
                "Skipping file '%s' as it is not a valid Excel file.", excel_file
            )
            return None
        except Exception as e:
            logging.error("Failed to read file '%s': %s", excel_file, str(e))
            return None

    def df_processing(data: pd.DataFrame) -> pd.DataFrame:
        """
        Processes the Kahoot question data.
        :param data: DataFrame with Kahoot question data
        :return: Processed DataFrame
        """
        # delete duplicated questions
        data = data.drop_duplicates(subset=["Question Number"])

        data = data.fillna("")

        data["Possible Answers"] = data[
            ["Answer 1", "Answer 2", "Answer 3", "Answer 4", "Answer 5", "Answer 6"]
        ].agg("<br>".join, axis=1)

        # keep only needed columns
        data = data[["Question", "Possible Answers", "Correct Answers"]]

        return data

    out = pd.DataFrame(columns=["Question", "Possible Answers", "Correct Answers"])

    questions_cnt = 0
    files_cnt = 0

    for file in get_excels(input_directory):
        df = get_excel_data(file)
        if df is None:
            continue
        files_cnt += 1

        df = df_processing(df)

        # add to out dataframe
        out = pd.concat([out, df], axis=0, ignore_index=True)

        questions_cnt += len(df)

    logging.info("Read input files: %d", files_cnt)
    logging.info("Read questions: %d", questions_cnt)
    out = out.drop_duplicates(subset=["Question"])
    return out


def make_anki(df: pd.DataFrame, out: str, title: str) -> None:
    """
    Creates an Anki deck from the given Kahoot questions

    :param df: The kahoot questions in a pd.DataFrame
    :param out: The path to the output directory
    :param title: The title of the Anki deck
    :return: None
    """
    my_model = genanki.Model(
        1607392319,
        "Simple Model",
        fields=[
            {"name": "Question"},
            {"name": "Answer"},
            {"name": "selects"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": "{{Question}}<br><br>{{selects}}",
                "afmt": '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ],
    )

    my_deck = genanki.Deck(2059400110, title)

    for index, row in df.iterrows():
        my_note = genanki.Note(
            model=my_model,
            fields=[row["Question"], row["Correct Answers"], row["Possible Answers"]],
        )
        my_deck.add_note(my_note)

    try:
        genanki.Package(my_deck).write_to_file(
            os.path.join(out, "anki.apkg"),
        )
    except Exception as e:
        logging.error("Failed to write Anki package file: %s", str(e))


if __name__ == "__main__":
    main()
