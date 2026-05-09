import sys
import os
import json
import certifi
import pymongo
import pandas as pd
import numpy as np
from dotenv import load_dotenv

from NetworkSecurity.exception.exception import NetworkSecurityException
from NetworkSecurity.logging.logger  import logging


load_dotenv()
URL = os.getenv("MONGODB_URL")  
print(URL)

ca = certifi.where()

class NetworkDataExctract:
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def csv_to_json_converter(self, csv_file_path):
        try:
            data = pd.read_csv(csv_file_path)
            data.reset_index(drop=True, inplace=True)
            records = list(json.loads(data.T.to_json()).values())
            return records

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def insert_data_to_mongoDB(self, records, database_name, collection_name):
        try:
            # Force local MongoDB connection to avoid DNS issues
            self.client = pymongo.MongoClient("mongodb://localhost:27017", ssl=False)
            
            self.db = self.client[database_name]
            self.collection = self.db[collection_name]
            self.collection.insert_many(records)
            return f"Data inserted successfully and No. of records inserted: {len(records)}"

        except Exception as e:

            raise NetworkSecurityException(e, sys)         


if __name__ == "__main__":
    try:
        FILE_NAME = "Network_Data/phisingData.csv"
        DATABASE_NAME = "NetworkSecurity"
        COLLECTION_NAME = "PhishingData"

        networkObj = NetworkDataExctract()
        records = networkObj.csv_to_json_converter(FILE_NAME)
        print(f"Records: {records}")
        no_of_records = networkObj.insert_data_to_mongoDB(records, DATABASE_NAME, COLLECTION_NAME)
        print(no_of_records)
        
    except Exception as e:
        raise NetworkSecurityException(e, sys)         
