from typing import List, Dict, Any

class DataCleaner:
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data

    def remove_duplicates(self) -> None:
        seen = set()
        new_data = []
        for d in self.data:
            t = tuple(d.items())
            if t not in seen:
                seen.add(t)
                new_data.append(d)
        self.data = new_data

    def remove_empty_values(self) -> None:
        self.data = [d for d in self.data if all(d.values())]

    def clean_data(self, standard_keys: List[str]) -> List[Dict[str, Any]]:
        self.remove_duplicates()
        self.remove_empty_values()

        return self.data


# data = [
#     {"name": "Alice", "age": "30", "height": "5.5"},
#     {"name": "Bob", "age": "25", "height": "6.0"},
#     {"name": "Alice", "age": "30", "height": "5.5"},
#     {"name": "Charlie", "age": "", "height": "5.8"}
# ]

# cleaner = DataCleaner(data)
# standard_keys = ["name", "age", "height"]
# cleaned_data = cleaner.clean_data(standard_keys)

# print(cleaned_data)