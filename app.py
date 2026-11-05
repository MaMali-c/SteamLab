"""Run with: python -m streamlit run app.py"""

from pathlib import Path

from steamlab.ui.app import main

main(Path(__file__).resolve().parent)
