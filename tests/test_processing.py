import logging
import zipfile

import pandas as pd

from kahoot_to_anki.processing import get_questions, get_excels, get_excel_data, df_processing, make_anki

logging.basicConfig(level=logging.DEBUG)

KAHOOT_SHEET_NAME = "RawReportData Data"

def write_excel(df: pd.DataFrame, tmp_path, filename="sample.xlsx", sheet_name=KAHOOT_SHEET_NAME):
    path = tmp_path / filename
    df.to_excel(path, sheet_name=sheet_name, index=False)
    return path

# --- get_questions ---
def test_get_questions_single_file(tmp_path):
    """Test processing a single valid Kahoot Excel file."""
    
    df = pd.DataFrame({
        "Question Number": [1],
        "Question": ["What is 2+2?"],
        "Answer 1": ["4"],
        "Answer 2": ["3"],
        "Answer 3": [""],
        "Answer 4": [""],
        "Answer 5": [""],
        "Answer 6": [""],
        "Correct Answers": ["4"]
    })

    excel_file = write_excel(df, tmp_path)
    result_df = get_questions(input_directory=str(excel_file), sheet_name=KAHOOT_SHEET_NAME)

    # Assertions
    assert not result_df.empty
    assert result_df.shape[0] == 1
    assert "Question" in result_df.columns
    assert result_df.iloc[0]["Question"] == "What is 2+2?"
    expected_columns = ["Question", "Possible Answers", "Correct Answers"]
    assert list(result_df.columns) == expected_columns
    
def test_get_questions_deduplicates_questions(tmp_path):
    """Test processing a single valid Kahoot Excel file with duplicated questions."""
    
    df1 = pd.DataFrame({
        "Question Number": [1],
        "Question": ["What is 2+2?"],
        "Answer 1": ["4"],
        "Answer 2": ["3"],
        "Answer 3": [""],
        "Answer 4": [""],
        "Answer 5": [""],
        "Answer 6": [""],
        "Correct Answers": ["4"]
    })

    df2 = df1.copy()
    df = pd.concat([df1, df2], ignore_index=True)

    write_excel(df, tmp_path)
    result_df = get_questions(input_directory=str(tmp_path), sheet_name=KAHOOT_SHEET_NAME)

    # Assertions
    assert result_df.shape[0] == 1
    
    
def test_get_questions_handles_numeric_answers(tmp_path):
    """Test processing a single valid Kahoot Excel file with mixed data types."""
    
    df = pd.DataFrame({
        "Question Number": [1],
        "Question": ["What is 2+2?"],
        "Answer 1": ["2"],
        "Answer 2": [4],
        "Answer 3": ["6"],
        "Answer 4": [""],
        "Answer 5": [""],
        "Answer 6": [""],
        "Correct Answers": ["4"]
    })

    write_excel(df, tmp_path)
    result_df = get_questions(input_directory=str(tmp_path), sheet_name=KAHOOT_SHEET_NAME)

    assert result_df.shape[0] == 1
    assert "4" in result_df.iloc[0]["Possible Answers"]
    
    
def test_get_questions_returns_empty_for_empty_file(tmp_path):
    """Test that an empty Excel file returns an empty DataFrame."""
    df = pd.DataFrame(columns=[
        "Question Number", "Question", "Answer 1", "Answer 2", "Answer 3",
        "Answer 4", "Answer 5", "Answer 6", "Correct Answers"
    ])
    write_excel(df, tmp_path)
    result_df = get_questions(input_directory=str(tmp_path), sheet_name=KAHOOT_SHEET_NAME)
    assert result_df.empty
    
    
def test_get_questions_merges_multiple_files(tmp_path):
    df1 = pd.DataFrame({
        "Question Number": [1],
        "Question": ["What is 2+2?"],
        "Answer 1": ["4"],
        "Answer 2": ["3"],
        "Answer 3": [""],
        "Answer 4": [""],
        "Answer 5": [""],
        "Answer 6": [""],
        "Correct Answers": ["4"]
    })

    df2 = pd.DataFrame({
        "Question Number": [2],
        "Question": ["What is the capital of France?"],
        "Answer 1": ["Berlin"],
        "Answer 2": ["Paris"],
        "Answer 3": ["Madrid"],
        "Answer 4": [""],
        "Answer 5": [""],
        "Answer 6": [""],
        "Correct Answers": ["Paris"]
    })

    # Write both files into the same temp directory
    write_excel(df1, tmp_path, filename="quiz1.xlsx")
    write_excel(df2, tmp_path, filename="quiz2.xlsx")

    result_df = get_questions(input_directory=str(tmp_path), sheet_name=KAHOOT_SHEET_NAME)

    assert result_df.shape[0] == 2
    assert "What is 2+2?" in result_df["Question"].values
    assert "What is the capital of France?" in result_df["Question"].values
    
    
def test_get_questions_skips_invalid_sheets(tmp_path):
    df1 = pd.DataFrame({
        "Question Number": [1],
        "Question": ["What is 2+2?"],
        "Answer 1": ["4"],
        "Answer 2": ["3"],
        "Answer 3": [""],
        "Answer 4": [""],
        "Answer 5": [""],
        "Answer 6": [""],
        "Correct Answers": ["4"]
    })

    df2 = pd.DataFrame({
        "Question Number": [2],
        "Question": ["What is the capital of France?"],
        "Answer 1": ["Berlin"],
        "Answer 2": ["Paris"],
        "Answer 3": ["Madrid"],
        "Answer 4": [""],
        "Answer 5": [""],
        "Answer 6": [""],
        "Correct Answers": ["Paris"]
    })
    
    df3 = pd.DataFrame({
        "Question Number": [2],
        "Question": ["What is the capital of Spain?"],
        "Answer 1": ["Berlin"],
        "Answer 2": ["Paris"],
        "Answer 3": ["Madrid"],
        "Answer 4": [""],
        "Answer 5": [""],
        "Answer 6": [""],
        "Correct Answers": ["Madrid"]
    })

    # Write both files into the same temp directory
    write_excel(df1, tmp_path, filename="quiz1.xlsx")
    write_excel(df2, tmp_path, filename="quiz2.xlsx")
    write_excel(df3, tmp_path, filename="quiz3.xlsx", sheet_name="TEST")

    result_df = get_questions(input_directory=str(tmp_path), sheet_name=KAHOOT_SHEET_NAME)

    assert result_df.shape[0] == 2
    assert "What is 2+2?" in result_df["Question"].values
    assert "What is the capital of France?" in result_df["Question"].values


# --- get_excels ---
def test_get_excels_single_file(tmp_path):
    """Test that get_excels yields a single file when given a single .xlsx file path."""
    file = tmp_path / "single.xlsx"
    file.write_text("dummy content")

    result = list(get_excels(str(file)))
    
    assert len(result) == 1
    assert result[0].endswith("single.xlsx")
    
    
def test_get_excels_multiple_files_in_directory(tmp_path):
    """Test that get_excels yields all .xlsx files in a directory."""
    file1 = tmp_path / "file1.xlsx"
    file2 = tmp_path / "file2.xlsx"
    file3 = tmp_path / "file3.csv"  # should be ignored

    for f in [file1, file2]:
        f.write_text("dummy content")
    file3.write_text("should be ignored")

    result = list(get_excels(str(tmp_path)))

    assert len(result) == 2
    assert all(f.endswith(".xlsx") for f in result)
    assert str(file3) not in result
    
    
# --- get_excel_data ---
def test_get_excel_data_valid(tmp_path):
    """Test reading a valid Excel file with correct sheet name."""
    df = pd.DataFrame({"Question": ["Q1"], "Correct Answers": ["A1"]})
    path = tmp_path / "valid.xlsx"
    df.to_excel(path, sheet_name=KAHOOT_SHEET_NAME, index=False)

    result = get_excel_data(str(path), sheet_name=KAHOOT_SHEET_NAME)

    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert "Question" in result.columns

def test_get_excel_data_missing_sheet(tmp_path, caplog):
    """Test behavior when the specified sheet name does not exist."""
    df = pd.DataFrame({"Question": ["Q1"]})
    path = tmp_path / "missing_sheet.xlsx"
    df.to_excel(path, sheet_name="WrongSheet", index=False)

    with caplog.at_level(logging.WARNING):
        result = get_excel_data(str(path), sheet_name=KAHOOT_SHEET_NAME)

    assert result is None
    assert "Skipping file" in caplog.text

def test_get_excel_data_invalid_file(tmp_path, caplog):
    """Test behavior when trying to read a corrupted Excel file."""
    path = tmp_path / "fake.xlsx"
    path.write_text("This is not a real Excel file.")

    with caplog.at_level(logging.WARNING):
        result = get_excel_data(str(path), sheet_name=KAHOOT_SHEET_NAME)

    assert result is None
    assert "Skipping file" in caplog.text
    
    
# --- df_processing ---
def test_df_processing_empty():
    df = pd.DataFrame(columns=[
        "Question Number", "Question", "Answer 1", "Answer 2", "Answer 3",
        "Answer 4", "Answer 5", "Answer 6", "Correct Answers"
    ])
    result = df_processing(df)
    
    assert result.empty
    assert list(result.columns) == ["Question", "Possible Answers", "Correct Answers"]


def test_df_processing_normal_case():
    df = pd.DataFrame({
        "Question Number": [1],
        "Question": ["What is 2+2?"],
        "Answer 1": ["2"],
        "Answer 2": ["4"],
        "Answer 3": ["3"],
        "Answer 4": [""],
        "Answer 5": [""],
        "Answer 6": [""],
        "Correct Answers": ["4"]
    })
    result = df_processing(df)

    assert result.shape[0] == 1
    assert "What is 2+2?" in result["Question"].values
    assert "4" in result["Possible Answers"].iloc[0]


def test_df_processing_duplicate_question_number():
    df = pd.DataFrame({
        "Question Number": [1, 1],
        "Question": ["What is 2+2?", "What is 2+2?"],
        "Answer 1": ["2", "2"],
        "Answer 2": ["4", "4"],
        "Answer 3": ["3", "3"],
        "Answer 4": ["", ""],
        "Answer 5": ["", ""],
        "Answer 6": ["", ""],
        "Correct Answers": ["4", "4"]
    })
    result = df_processing(df)

    assert result.shape[0] == 1


def test_df_processing_mixed_types():
    df = pd.DataFrame({
        "Question Number": [1],
        "Question": ["How many continents?"],
        "Answer 1": ["7"],
        "Answer 2": [6],  # int type
        "Answer 3": [""],
        "Answer 4": [None],
        "Answer 5": ["Five"],
        "Answer 6": [""],
        "Correct Answers": ["7"]
    })
    result = df_processing(df)

    assert result.shape[0] == 1
    assert "6" in result["Possible Answers"].iloc[0]  # check that int was converted
    assert "None" not in result["Possible Answers"].iloc[0]  # check fillna
    
    
# --- make_anki ---
def test_make_anki_creates_apkg(tmp_path):
    """Test that make_anki creates a valid .apkg file."""

    # Prepare test data
    df = pd.DataFrame({
        "Question": ["What is 2+2?"],
        "Possible Answers": ["2<br>3<br>4"],
        "Correct Answers": ["4"]
    })

    # Run the function
    make_anki(df=df, out=str(tmp_path), title="Test Deck")

    # Check output file exists
    output_file = tmp_path / "anki.apkg"
    assert output_file.exists()
    assert output_file.stat().st_size > 0

    # Check that it's a valid ZIP file (as .apkg is zip format internally)
    assert zipfile.is_zipfile(output_file)