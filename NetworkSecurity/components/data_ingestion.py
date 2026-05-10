import os
import sys
import pymongo
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

from NetworkSecurity.logging.logger import logging
from NetworkSecurity.exception.exception import NetworkSecurityException
from NetworkSecurity.entity.config_entity import DataIngestionConfig
from NetworkSecurity.entity.artifact_entity import DataIngestionArtifact

from dotenv import load_dotenv
load_dotenv()

MongoDB_URL = os.getenv("MONGODB_URL")  


class DataIngestion:
    def __init__(self, data_ingestion_config : DataIngestionConfig):

        try: 
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException (e, sys)
            
    def export_colllection_as_dataframe(self):  

        '''
        Method Name : export_colllection_as_dataframe
        Description : This method exports the collection as a dataframe
        Output      : DataFrame
        On Failure  : Raise Exception
        '''

        logging.info("Entered export_colllection_as_dataframe method of DataIngestion class")
        try:  
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name
            
            logging.info(f"Connecting to database: {database_name}, collection: {collection_name}")
            
            self.mongodb_client = pymongo.MongoClient(MongoDB_URL)
            
            # Test connection and list databases/collections
            databases = self.mongodb_client.list_database_names()
            logging.info(f"Available databases: {databases}")
            print(f"Available databases: {databases}")  # Also print to console
            
            if database_name in databases:
                db = self.mongodb_client[database_name]
                collections = db.list_collection_names()
                logging.info(f"Collections in {database_name}: {collections}")
                
                if collection_name in collections:
                    collection = db[collection_name]
                    count = collection.count_documents({})
                    logging.info(f"Document count in {collection_name}: {count}")
                    
                    df = pd.DataFrame(list(collection.find()))
                    logging.info(f"Dataframe shape after query: {df.shape}")
                    
                    if "_id" in df.columns.to_list():
                        df = df.drop(columns=["_id"])
                    df.replace({"na":np.nan}, inplace=True)    
                    return df
                else:
                    logging.error(f"Collection {collection_name} not found in database {database_name}")
                    raise ValueError(f"Collection {collection_name} not found")
            else:
                logging.error(f"Database {database_name} not found")
                raise ValueError(f"Database {database_name} not found")
        except Exception as e:
            raise NetworkSecurityException (e, sys) 
        logging.info("Exited export_colllection_as_dataframe method of DataIngestion class")


  

    def export_data_to_feature_store(self, dataframe :pd.DataFrame):       
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            # Save dataframe to csv file
            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            logging.info(f"Saved data to {feature_store_file_path}")
            return dataframe

        except Exception as e:
            raise NetworkSecurityException (e, sys)    

        logging.info("Exited export_data_to_feature_store method of DataIngestion class")

    def split_data_as_train_test(self,dataframe: pd.DataFrame):
        try:
            logging.info("Performed train test split on the dataframe.")
            train_set, test_set = train_test_split(
                dataframe, test_size=self.data_ingestion_config.train_test_split_ratio
            )
            logging.info("Exited split_data_as_train_test method of Data_Ingestion class.")
            
            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            
            os.makedirs(dir_path, exist_ok=True)
            
            logging.info(f"Exporting train and test file path.")
            
            train_set.to_csv(
                self.data_ingestion_config.training_file_path, index=False, header=True
            )

            test_set.to_csv(
                self.data_ingestion_config.testing_file_path, index=False, header=True
            )
            logging.info("Exported train and test file path.")

            
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def initiate_data_ingestion(self):
        try:
            dataframe=self.export_colllection_as_dataframe()
            dataframe=self.export_data_to_feature_store(dataframe)
            self.split_data_as_train_test(dataframe)
            dataingestionartifact=DataIngestionArtifact(train_file_path=self.data_ingestion_config.training_file_path,
                                                        test_file_path=self.data_ingestion_config.testing_file_path)
            return dataingestionartifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)        




