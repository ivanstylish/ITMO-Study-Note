import pandas as pd
import numpy as np


class DataLoader:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data = None
        self.columns = ['X1', 'X2', 'X3', 'X4']

    def load(self) -> pd.DataFrame:
        try:
            self.data = pd.read_csv(self.filepath)
            if len(self.data) != 200:
                raise ValueError(f"Ожидалось 200 строк, найдено {len(self.data)}")
            if list(self.data.columns) != self.columns:
                raise ValueError("Ожидаемые столбцы: X1, X2, X3, X4")
            print(f"Данные успешно загружены: {self.data.shape}")
            return self.data
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            return None

    def get_column(self, col_name: str) -> np.ndarray:
        if col_name not in self.data.columns:
            raise KeyError(f"Столбец {col_name} отсутствует")
        return self.data[col_name].values