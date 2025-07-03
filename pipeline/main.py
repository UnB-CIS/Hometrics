import argparse
import os
import sys
import time

import pandas as pd
from dotenv import load_dotenv
from utils.data_handler import DataHandler

from pipeline.data_cleaning import DataCleaner
from pipeline.data_scraping import ScraperOrchestrator
from pipeline.data_transform import DataTransformer

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":

    orchestrator = ScraperOrchestrator()
    results = orchestrator.run_pipeline("pipeline/dataset/raw_final_output")

    

    main()
