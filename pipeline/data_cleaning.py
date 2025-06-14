from typing import Any, Dict, List


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
