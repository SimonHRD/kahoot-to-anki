# Standard library imports
import shutil
import os

# Third-party library imports
import numpy as np
import pandas as pd
import pytest

# Local application/library imports
import converter


def generate_test_data():
    # Create multiple lists
    question_number = [
        "Question 1",
        "Question 1",
        "Question 1",
        "Question 2",
        "Question 2",
        "Question 2",
    ]
    question = [
        "How is a code block indicated in Python?",
        "How is a code block indicated in Python?",
        "How is a code block indicated in Python?",
        "Which of the following concepts is not a part of Python?",
        "Which of the following concepts is not a part of Python?",
        "Which of the following concepts is not a part of Python?",
    ]
    answer_1 = [
        "Brackets",
        "Brackets",
        "Brackets",
        "Pointers",
        "Pointers",
        "Pointers",
    ]
    answer_2 = [
        "Indentation",
        "Indentation",
        "Indentation",
        "Loops",
        "Loops",
        "Loops",
    ]
    answer_3 = [
        "Key",
        "Key",
        "Key",
        "Dynamic Typing",
        "Dynamic Typing",
        "Dynamic Typing",
    ]
    answer_4 = [
        np.nan,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
    ]
    answer_5 = [
        np.nan,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
    ]
    answer_6 = [
        np.nan,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
    ]
    correct_answers = [
        "Indentation",
        "Indentation",
        "Indentation",
        "Pointers",
        "Pointers",
        "Pointers",
    ]
    time_to_answer = [
        "10",
        "10",
        "10",
        "10",
        "10",
        "10",
    ]
    player = [
        "Harry",
        "Hermione ",
        "Ron",
        "Harry",
        "Hermione ",
        "Ron",
    ]
    answer = [
        "Indentation",
        "Indentation",
        "Brackets",
        "Dynamic Typing",
        "Pointers",
        "Dynamic Typing",
    ]
    correct_incorrect = [
        True,
        True,
        False,
        False,
        True,
        False,
    ]
    columns = [
        "Question Number",
        "Question",
        "Answer 1",
        "Answer 2",
        "Answer 3",
        "Answer 4",
        "Answer 5",
        "Answer 6",
        "Correct Answers",
        "Time Allotted to Answer (seconds)",
        "Player",
        "Answer",
        "Correct / Incorrect",
    ]

    # Create DataFrame from multiple lists
    df = pd.DataFrame(
        list(
            zip(
                question_number,
                question,
                answer_1,
                answer_2,
                answer_3,
                answer_4,
                answer_5,
                answer_6,
                correct_answers,
                time_to_answer,
                player,
                answer,
                correct_incorrect,
            )
        ),
        columns=columns,
    )
    return df


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown():
    test_data_dir = "test_data"
    test_data_dir_empty = "test_data_empty"
    input_file_name = "input.xlsx"
    empty_file_name = "empty.xlsx"

    input_file_path = os.path.join(test_data_dir, input_file_name)
    empty_file_path = os.path.join(test_data_dir, empty_file_name)

    df = generate_test_data()

    os.makedirs(test_data_dir, exist_ok=True)
    df.to_excel(input_file_path, sheet_name="RawReportData Data", index=False)

    os.makedirs(test_data_dir_empty, exist_ok=True)

    # create empty excel
    df_empty = pd.DataFrame()
    df_empty.to_excel(empty_file_path)

    # Yield to allow the test to run
    yield

    # Teardown: Cleanup the created files
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    if os.path.exists(test_data_dir_empty):
        shutil.rmtree(test_data_dir_empty)


def test_validation_wrong_output():
    with pytest.raises(ValueError):
        assert converter.validation("test_data/", "test_data/input.xlsx")


def test_validation_wrong_input_file():
    with pytest.raises(FileNotFoundError):
        assert converter.validation("test_data/in.txt", "test_data/")


def test_validation_empty_input_directory():
    with pytest.raises(FileNotFoundError):
        assert converter.validation("test_data_empty/", "./output")


def test_validation():
    assert converter.validation('./test_data/', "./test_data/") is None


def test_get_questions_wrong_excel():
    assert converter.get_questions("test_data/empty.xlsx").shape[0] == 0


def test_get_questions_file():
    assert converter.get_questions("test_data/input.xlsx").shape[0] == 2


def test_get_questions_directory():
    assert converter.get_questions("test_data/").shape[0] == 2


def test_make_anki():
    df = converter.get_questions("test_data/input.xlsx")
    converter.make_anki(df, "test_data/", "test")
    # Check if output file exists
    assert os.path.exists("test_data/anki.apkg") is True
