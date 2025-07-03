import glob
import os
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


class ScraperOrchestrator:
    """
    Orchestrates the collection and merging of scraped data files from multiple scraper sources.
    Finds and processes TSV and XLSX files in the detailed_properties folders of each scraper.
    """

    def __init__(self, base_scripts_dir: str = None):
        """ Initialize the scraper orchestrator """

        if base_scripts_dir is None:
            self.scripts_dir = os.path.join(Path(__file__).parent.parent, "scripts")
        else:
            self.scripts_dir = base_scripts_dir

        self.tsv_files = []
        self.xlsx_files = []

    def discover_data_files(self) -> Dict[str, List[str]]:
        """ Discover all TSV and XLSX files in detailed_properties folders. """

        self.tsv_files = []
        self.xlsx_files = []

        scraper_dirs = [
            d
            for d in os.listdir(self.scripts_dir)
            if os.path.isdir(os.path.join(self.scripts_dir, d))
        ]

        for scraper in scraper_dirs:
            scraper_path = os.path.join(self.scripts_dir, scraper)
            dataset_path = os.path.join(scraper_path, "dataset")

            if not os.path.exists(dataset_path):
                continue

            detailed_props_path = os.path.join(dataset_path, "detailed_properties")

            if not os.path.exists(detailed_props_path):
                self._find_data_files(dataset_path, scraper)
            else:
                self._find_data_files(detailed_props_path, scraper)

        return {"tsv": self.tsv_files, "xlsx": self.xlsx_files}

    def _find_data_files(self, search_path: str, scraper_name: str) -> None:
        """ Find TSV and XLSX files in the given path. """

        # Find TSV files
        tsv_pattern = os.path.join(search_path, "*.tsv")
        found_tsv = glob.glob(tsv_pattern)
        if found_tsv:
            print(f"Found {len(found_tsv)} TSV files in {scraper_name}")
            self.tsv_files.extend(found_tsv)

        # Find XLSX files
        xlsx_pattern = os.path.join(search_path, "*.xlsx")
        found_xlsx = glob.glob(xlsx_pattern)
        if found_xlsx:
            print(f"Found {len(found_xlsx)} XLSX files in {scraper_name}")
            self.xlsx_files.extend(found_xlsx)

    def merge_tsv_files(self) -> pd.DataFrame:
        """ Merge all discovered TSV files into a single DataFrame. """

        if not self.tsv_files:
            print("No TSV files found to merge.")
            return pd.DataFrame()

        dfs = []
        for file_path in self.tsv_files:
            try:
                df = pd.read_csv(file_path, sep="\t")
                # Add source information
                df["data_source"] = os.path.basename(
                    os.path.dirname(os.path.dirname(file_path))
                )
                dfs.append(df)
                print(f"Loaded {len(df)} rows from {file_path}")
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")

        if not dfs:
            return pd.DataFrame()

        # Merge all dataframes
        merged_df = pd.concat(dfs, ignore_index=True)
        print(f"Merged {len(merged_df)} total rows from TSV files")
        return merged_df

    def merge_xlsx_files(self) -> pd.DataFrame:
        """ Merge all discovered XLSX files into a single DataFrame. """

        if not self.xlsx_files:
            print("No XLSX files found to merge.")
            return pd.DataFrame()

        dfs = []
        for file_path in self.xlsx_files:
            try:
                df = pd.read_excel(file_path)
                # Add source information
                df["data_source"] = os.path.basename(
                    os.path.dirname(os.path.dirname(file_path))
                )
                dfs.append(df)
                print(f"Loaded {len(df)} rows from {file_path}")
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")

        if not dfs:
            return pd.DataFrame()

        # Merge all dataframes
        merged_df = pd.concat(dfs, ignore_index=True)
        print(f"Merged {len(merged_df)} total rows from XLSX files")
        return merged_df

    def get_merged_data(self) -> pd.DataFrame:
        """
        Get all merged data from both TSV and XLSX files.
        This function automatically discovers and merges all available data.
        """
        # Discover all data files
        self.discover_data_files()

        # Merge TSV files
        tsv_data = self.merge_tsv_files()

        # Merge XLSX files
        xlsx_data = self.merge_xlsx_files()

        # Merge both sources if both exist
        if not tsv_data.empty and not xlsx_data.empty:
            try:
                merged_data = pd.concat([tsv_data, xlsx_data], ignore_index=True)
                print(
                    f"Successfully merged {len(tsv_data)} TSV rows and {len(xlsx_data)} XLSX rows"
                )
                return merged_data
            except Exception as e:
                print(f"Error merging TSV and XLSX data: {str(e)}")
                print("Returning TSV data only (preferred format)")
                return tsv_data
        elif not tsv_data.empty:
            return tsv_data
        elif not xlsx_data.empty:
            return xlsx_data
        else:
            print("No data files found.")
            return pd.DataFrame()

    def save_merged_data_to_files(self, output_dir: str) -> Dict[str, str]:
        """ Save merged data to TSV and XLSX files in the specified output folder. """
        # Get merged data
        tsv_data = self.merge_tsv_files()
        xlsx_data = self.merge_xlsx_files()

        os.makedirs(output_dir, exist_ok=True)

        output_files = {}

        # Save merged TSV data
        if not tsv_data.empty:
            tsv_output_path = os.path.join(output_dir, "merged_properties.tsv")
            tsv_data.to_csv(tsv_output_path, sep="\t", index=False)
            print(
                f"Saved merged TSV data with {len(tsv_data)} rows to {tsv_output_path}"
            )
            output_files["tsv"] = tsv_output_path

        # Save merged XLSX data
        if not xlsx_data.empty:
            xlsx_output_path = os.path.join(output_dir, "merged_properties.xlsx")
            xlsx_data.to_excel(xlsx_output_path, index=False)
            print(
                f"Saved merged XLSX data with {len(xlsx_data)} rows to {xlsx_output_path}"
            )
            output_files["xlsx"] = xlsx_output_path

        if not output_files:
            print("No data files were saved as no data was found.")

        return output_files

    def run_pipeline(self, output_dir: str) -> Dict[str, Any]:
        """
        Run the complete data scraping pipeline:
        1. Discover data files
        2. Merge the data
        3. Save to output files
        """

        discovered_files = self.discover_data_files()

        merged_data = self.get_merged_data()

        output_files = self.save_merged_data_to_files(output_dir)

        return {
            "discovered_files": discovered_files,
            "merged_row_count": len(merged_data) if not merged_data.empty else 0,
            "output_files": output_files,
        }


if __name__ == "__main__":
    orchestrator = ScraperOrchestrator()
    results = orchestrator.run_pipeline("pipeline/dataset/raw_final_output")