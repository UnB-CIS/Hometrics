import csv
import os

import pandas as pd


class DataHandler:
    def __init__(self, data):
        self.data = data

    def create_dataframe(self, contract_type):
        """Creates a Pandas DataFrame from the property data and adds a 'contract_type' column."""
        df = pd.DataFrame(self.data)
        df["contract_type"] = contract_type
        return df

    def save_to_excel(self, df, filename, output_dir=None, append=False):
        """Saves the DataFrame to an Excel file."""
        # Create full path
        filepath = os.path.join(output_dir, filename) if output_dir else filename

        # Create directory if it doesn't exist
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # If append and file exists, append to it
        if append and os.path.exists(filepath):
            try:
                # This is a more reliable way to append to Excel
                existing_df = pd.read_excel(filepath)
                combined_df = pd.concat([existing_df, df], ignore_index=True)
                combined_df.to_excel(filepath, index=False)
            except Exception as e:
                print(f"Error when appending to Excel file: {e}")
                # Fallback: just save the current data
                df.to_excel(filepath, index=False)
        else:
            # Create a new file or overwrite existing
            df.to_excel(filepath, index=False)

        print(f"Excel data saved to {filepath}")

    def save_to_csv(
        self,
        df,
        filename,
        output_dir=None,
        append=False,
        separator=",",
        encoding="utf-8",
    ):
        """Saves the DataFrame to a delimited text file (CSV by default, TSV if separator='\t')."""

        # Create full path
        filepath = os.path.join(output_dir, filename) if output_dir else filename

        # Create directory if it doesn't exist
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Determine write mode and header
        file_exists = os.path.exists(filepath)
        mode = "a" if append and file_exists else "w"
        header = not (append and file_exists)

        # Make a copy to avoid modifying the original DataFrame
        df_to_save = df.copy()

        # Clean text fields: remove newlines, tabs that are not separators, etc.
        for col in df_to_save.select_dtypes(include="object").columns:
            # Ensure column is string type and fill NaNs with empty string
            s_series = df_to_save[col].astype(str).fillna("")

            # Replace carriage returns and newlines with a space
            s_series = s_series.str.replace("\r\n", " ", regex=False)
            s_series = s_series.str.replace("\n", " ", regex=False)
            s_series = s_series.str.replace("\r", " ", regex=False)

            # If the separator is a tab, replace literal tab characters within fields with spaces.
            if separator == "\t":
                s_series = s_series.str.replace("\t", " ", regex=False)

            # Consolidate multiple whitespace characters into a single space
            s_series = s_series.str.replace(r"\s+", " ", regex=True)

            # Strip leading/trailing whitespace
            df_to_save[col] = s_series.str.strip()

        try:
            df_to_save.to_csv(
                filepath,
                sep=separator,
                index=False,
                encoding=encoding,
                mode=mode,
                header=header,
                quoting=csv.QUOTE_MINIMAL,  # Escapa só se necessário
            )
            print(f"Data saved to {filepath}")
        except Exception as e:
            print(f"Error saving file {filepath}: {e}")

    def save_to_tsv(
        self, df, filename, output_dir=None, append=False, encoding="utf-8"
    ):
        """Saves the DataFrame to a TSV file (tab-separated values)."""
        # Make sure filename has .tsv extension
        if not filename.lower().endswith(".tsv"):
            if "." in filename:
                filename = filename.split(".")[0] + ".tsv"
            else:
                filename = filename + ".tsv"

        # Call save_to_csv with tab separator
        self.save_to_csv(
            df, filename, output_dir, append, separator="\t", encoding=encoding
        )
