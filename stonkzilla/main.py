"""Main entry point."""
import sys
from stonkzilla.cli.run_handler import run_command

def main():
    """
    Main function for the stonkzilla CLI.
    Handles the primary execution flow.
    """
    run_command()
    sys.exit(0)
if __name__ == "__main__":
    main()
