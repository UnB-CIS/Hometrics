import pandas as pd
import os
from openpyxl import load_workbook
import glob

class DataCleaner:

    def __init__(self):
        pass

    def clean_duplicates(self, input_dir, output_dir):
        """
        Limpa duplicatas de todos os arquivos TSV no diretório especificado.
        """

        tsv_files = glob.glob(os.path.join(input_dir, "*.tsv"))
    
        if not tsv_files:
            print(f"No TSV files found in {input_dir}")
            return
    
        print(f"Found {len(tsv_files)} TSV files to process")
        
        for file_path in tsv_files:
            file_name = os.path.basename(file_path)
            print(f"\nProcessing {file_name}...")
            
            try:
                df = pd.read_csv(file_path, sep='\t')

                initial_count = len(df)
                print(f"Initial row count: {initial_count}")

                df.drop_duplicates(subset=df.columns[0], keep='first', inplace=True)

                final_count = len(df)
                print(f"Final row count: {final_count}")
                print(f"Removed {initial_count - final_count} duplicate entries")
                
                output_path = os.path.join(output_dir, file_name)
                df.to_csv(output_path, sep='\t', index=False)
                print(f"Cleaned file saved to {output_path}")
                
            except Exception as e:
                print(f"Error processing {file_name}: {str(e)}")
    
        print("\nLimpeza de duplicatas concluída!")