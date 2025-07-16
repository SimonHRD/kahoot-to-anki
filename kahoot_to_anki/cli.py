# Standard library imports
import argparse
from dataclasses import dataclass
import logging
import os
import glob

from kahoot_to_anki import __version__


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
    sheet: str
    export_csv: bool
    deck_title: str
    

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
        "--sheet",
        default=KAHOOT_EXCEL_SHEET_NAME_RAW_DATA,
        help=f"The Excel Sheet Name with the Kahoot Raw Data. Default {KAHOOT_EXCEL_SHEET_NAME_RAW_DATA}",
        type=str,
    )
    parser.add_argument(
        "--csv",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Enable or disable CSV export of question data (default: disabled).",
    )
    parser.add_argument(
        "-t",
        "--title",
        default=DEFAULT_DECK_TITLE,
        help="Name of the Anki deck to be created. "
        f"If not specified, the default deck name '{DEFAULT_DECK_TITLE}' will be used.",
        type=str,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the version number and exit.",
    )
    args = parser.parse_args()

    return CLIArgs(
        input_path=os.path.abspath(args.inp),
        output_path=os.path.abspath(args.out),
        sheet=args.sheet,
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