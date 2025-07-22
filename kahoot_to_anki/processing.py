# Standard library imports
import logging
import os
import glob
from typing import Iterator, Optional
import html

# Third-party library imports
import genanki
import pandas as pd


def get_questions(input_directory: str, sheet_name: str) -> pd.DataFrame:
    """
    Extracts all the kahoot questions out of the Excel file(s)

    :param input_directory: The path to the input directory or Excel file
    :param sheet_name: The Excel sheet name with the Kahoot Answers
    :return: All the questions with the possible answers and the solution
    :rtype: pd.DataFrame
    """

    out = pd.DataFrame(columns=["Question", "Possible Answers", "Correct Answers"])

    questions_cnt = 0
    files_cnt = 0

    for file in get_excels(input_directory):
        df = get_excel_data(excel_file=file, sheet_name=sheet_name)
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


def get_excels(path: str) -> Iterator[str]:
    """
    Returns a generator with all Excel files in the given path.
    :param path: the path to an Excel file or a directory with Excel files
    :return: a generator of Excel file paths
    """
    if os.path.isfile(path):
        yield path
    else:
        yield from glob.glob(os.path.join(path, "*.xlsx"))


def get_excel_data(excel_file: str, sheet_name:str) -> Optional[pd.DataFrame]:
    """
    Returns a pd.DataFrame with the kahoot raw data
    :param excel_file: an Excel file with Kahoot raw data
    :param sheet_name: the Excel sheet name with the Kahoot answers
    :return: a DataFrame with the data
    """
    try:
        # read file
        return pd.read_excel(
            excel_file, sheet_name=sheet_name
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
    if data.empty:
        return pd.DataFrame(columns=["Question", "Possible Answers", "Correct Answers"])
    
    # delete duplicated questions
    data = data.drop_duplicates(subset=["Question Number"])
    data = data.fillna("")
    
    # HTML-encode special chars
    data = data.apply(lambda col: col.map(lambda x: html.escape(x) if isinstance(x, str) else x))

    data["Possible Answers"] = data[
        ["Answer 1", "Answer 2", "Answer 3", "Answer 4", "Answer 5", "Answer 6"]
    ].astype(str).agg("<br>".join, axis=1)

    # keep only needed columns
    data = data[["Question", "Possible Answers", "Correct Answers"]]
    
    return data


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