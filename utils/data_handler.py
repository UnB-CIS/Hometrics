import pandas as pd
import os
from openpyxl import load_workbook

class DataHandler:
    def __init__(self, data):
        self.data = data

    def create_dataframe(self, contract_type):
        """
        Creates a Pandas DataFrame from the property data and adds a 'contract_type' column.
        """

        df = pd.DataFrame(self.data)
        df['contract_type'] = contract_type  
        return df

    def save_to_excel(self, df, filename, output_dir=None, append=False):
        """
        Saves the DataFrame to an Excel file.
        """
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
        
    def save_to_csv(self, df, filename, output_dir=None, append=False, separator=',', encoding='utf-8'):
        """
        Saves the DataFrame to a CSV file.
        """
        # Create full path
        filepath = os.path.join(output_dir, filename) if output_dir else filename
        
        # Create directory if it doesn't exist
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Check if we should append and file exists
        mode = 'a' if append and os.path.exists(filepath) else 'w'
        header = not (append and os.path.exists(filepath))  # Only write header if not appending or file doesn't exist
        
        # Write the CSV file
        df.to_csv(filepath, sep=separator, index=False, encoding=encoding, mode=mode, header=header)
        
        print(f"CSV data saved to {filepath}")