from abc import ABC, abstractmethod
from typing import Dict, Any, Iterator, List

import pandas as pd


class DataSource(ABC):
    """
    Abstract base class for data sources.
    
    This class defines the common interface that all data sources must implement.
    It follows the iteration pattern, allowing data sources to be iterated over
    to retrieve their data.
    """

    @abstractmethod
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_columns(self) -> List[str]:
        """
        Returns the list of column names available in this data source.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Returns the name of this data source.
        """
        pass

    def to_dataframe(self) -> pd.DataFrame:
        """
        Converts the data from this source to a pandas DataFrame.
        
        Returns:
            pd.DataFrame: A DataFrame containing all the data from this source.
        """
        data = list(self)

        if not data:
            # Return an empty DataFrame with the correct columns
            return pd.DataFrame(columns=self.get_columns())

        return pd.DataFrame(data)


def combine_data_sources(sources: List[DataSource]) -> pd.DataFrame:
    """
    Combines data from multiple data sources into a single pandas DataFrame.
    """
    if not sources:
        return pd.DataFrame()

    combined_df = pd.DataFrame()

    for source in sources:
        source_df = source.to_dataframe()

        if combined_df.empty:
            combined_df = source_df
        else:
            # Otherwise, append the new data, filling missing columns with NaN
            combined_df = pd.concat([combined_df, source_df], ignore_index=True)

    return combined_df


def save_to_csv(data: pd.DataFrame, filename: str) -> None:
    data.to_csv(filename, index=False)
