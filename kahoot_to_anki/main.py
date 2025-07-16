import os
import logging

from kahoot_to_anki.cli import get_commandline_arguments, validation
from kahoot_to_anki.processing import get_questions, make_anki

# Configure logging settings
logging.basicConfig(level=logging.INFO)


def main() -> None:
    # Check command line arguments
    args = get_commandline_arguments()

    validation(args.input_path, args.output_path)

    df = get_questions(input_directory=args.input_path, sheet_name=args.sheet)

    if args.export_csv:
        df.to_csv(
            os.path.join(args.output_path, "kahoot.csv"),
            sep=";",
            index=False,
            encoding="utf-8-sig",
        )
        
    make_anki(df, args.output_path, args.deck_title)


if __name__ == "__main__":
    main()
    
    
    
    
