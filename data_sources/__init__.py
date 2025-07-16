"""
Data sources module for retrieving user data from various sources.

This module provides a unified interface for accessing user data from different sources,
such as Higyrus API, BeClever database, and mock data for testing.
"""

# Export the abstract base class
from data_sources.abstract import DataSource
from data_sources.abstract import combine_data_sources, save_to_csv
from data_sources.beclever import BeCleverDataSource
# Export the concrete implementations
from data_sources.higyrus import HigyrusDataSource
from data_sources.mock import MockDataSource

# Define what's available when using "from data_sources import *"
__all__ = [
    'DataSource',
    'HigyrusDataSource',
    'MockDataSource',
    'BeCleverDataSource',
    'combine_data_sources',
    'save_to_csv'
]
