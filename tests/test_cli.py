import sys
from pathlib import Path

import pytest

from kahoot_to_anki.cli import get_commandline_arguments, validation


# --- get_commandline_arguments ---
def test_get_commandline_arguments(monkeypatch):
    """Test that CLI arguments are correctly parsed."""

    test_args = [
        "kahoot-to-anki",
        "-i", "tests/data",
        "-o", "output_dir",
        "--csv",
        "--sheet", "CustomSheet",
        "--title", "My Deck"
    ]

    monkeypatch.setattr(sys, "argv", test_args)

    args = get_commandline_arguments()

    assert Path(args.input_path).name == "data"
    assert Path(args.output_path).name == "output_dir"
    assert args.export_csv is True
    assert args.sheet == "CustomSheet"
    assert args.deck_title == "My Deck"
  
    
def test_get_commandline_arguments_no_csv(monkeypatch):
    """Test that --no-csv CLI argument is correctly parsed."""

    test_args = [
        "kahoot-to-anki",
        "--no-csv",
    ]

    monkeypatch.setattr(sys, "argv", test_args)
    args = get_commandline_arguments()

    assert args.export_csv is False
    
    
# --- validation ---
def test_validation_valid_excel_file(tmp_path):
    # Create dummy Excel file
    excel_file = tmp_path / "valid.xlsx"
    excel_file.write_text("Excel content")

    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Should not raise
    validation(str(excel_file), str(output_dir)) 
    
    
def test_validation_valid_input_directory_with_excel(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "file1.xlsx").write_text("Excel content")

    output_dir = tmp_path / "output"
    output_dir.mkdir()

     # Should not raise
    validation(str(input_dir), str(output_dir)) 
    
    
def test_validation_input_path_does_not_exist(tmp_path):
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    with pytest.raises(FileNotFoundError):
        validation(str(tmp_path / "missing.xlsx"), str(output_dir))
        
        
def test_validation_input_not_excel_file(tmp_path):
    file = tmp_path / "file.txt"
    file.write_text("Not Excel")
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    with pytest.raises(ValueError, match="Input file is not an excel file"):
        validation(str(file), str(output_dir))
        
        
def test_validation_input_directory_no_excel_files(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "file.txt").write_text("Just text")

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    with pytest.raises(FileNotFoundError, match="does not contain any excel files"):
        validation(str(input_dir), str(output_dir))
        
        
def test_validation_output_not_a_directory(tmp_path):
    excel_file = tmp_path / "valid.xlsx"
    excel_file.write_text("Excel content")

    output_path = tmp_path / "output.txt"
    output_path.write_text("Not a directory")

    with pytest.raises(ValueError, match="Output is not a directory"):
        validation(str(excel_file), str(output_path))
