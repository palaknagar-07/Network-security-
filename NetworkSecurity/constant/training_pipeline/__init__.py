import os
import sys
import pandas as pd
import numpy as np


'''
Some common constants are defined here

'''
TARGET_COLUMN: str = "Result"
PIPELINE_NAME: str = "NetworkSecurity"
FILE_NAME: str = "phisingData.csv"
ARTIFACTS_DIR: str = "artifacts"   
 
TRAIN_FILE_NAME: str = "train.csv"
TEST_FILE_NAME: str = "test.csv"

"""
This is the constant file for the project
data ingestion constant start from "DATA_INGESTION" variable name: 
    - collection name
    - database name
    - directory name
    - feature store directory
    - ingested directory
    - train test split ratio
"""

DATA_INGESTION_COLLECTION_NAME: str = "PhishingData"
DATA_INGESTION_DATABASE_NAME: str = "NetworkSecurity"
DATA_INGESTION_DIR_NAME: str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR: str = "feature_store"
DATA_INGESTION_INGESTED_DIR: str = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO: float = 0.2