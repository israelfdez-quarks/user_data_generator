"""
Data sources module for retrieving user data from various sources.

This module provides a unified interface for accessing user data from different sources,
such as Higyrus API, BeClever database, AL2Sync database, and mock data for testing.
"""

# Export the abstract base class
from data_sources.abstract import DataSource
from data_sources.abstract import combine_data_sources, save_to_csv
from data_sources.al2sync import AL2SyncDataSource
from data_sources.beclever import BeCleverDataSource
# Export the concrete implementations
from data_sources.higyrus import HigyrusDataSource

# Define what's available when using "from data_sources import *"
__all__ = [
    'DataSource',
    'HigyrusDataSource',
    'BeCleverDataSource',
    'AL2SyncDataSource',
    'combine_data_sources',
    'save_to_csv'
]
