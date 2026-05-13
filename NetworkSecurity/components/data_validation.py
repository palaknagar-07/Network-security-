from NetworkSecurity.entity.config_entity import DataValidationConfig
from NetworkSecurity.exception.exception import NetworkSecurityException
from NetworkSecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from NetworkSecurity.logging.logger import logging
from NetworkSecurity.constant.training_pipeline import SCHEMA_FILE_PATH
from NetworkSecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file
import sys
import pandas as pd
from typing import Optional

from scipy.stats import ks_2samp
import os, sys

class DataValidation:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,
                 data_validation_config:DataValidationConfig):
        
        try:
            self.data_ingestion_artifact=data_ingestion_artifact
            self.data_validation_config=data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e,sys)


    def validate_number_of_columns(self,df: pd.DataFrame) -> bool:
        try:
            number_of_columns = len(self._schema_config["columns"])
            logging.info(f"Required number of columns: {number_of_columns}")
            logging.info(f"Number of columns in dataframe: {len(df.columns)}")
            return len(df.columns) == number_of_columns
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def validate_numeric_columns_exist(self, df: pd.DataFrame) -> bool:
        try:
            numeric_columns = self._schema_config.get("numeric_columns", [])
            logging.info(f"Required numeric columns: {numeric_columns}")
            
            for col in numeric_columns:
                if col not in df.columns:
                    logging.error(f"Numeric column '{col}' not found in dataframe")
                    return False
                
                if not pd.api.types.is_numeric_dtype(df[col]):
                    logging.error(f"Column '{col}' exists but is not numeric. Found dtype: {df[col].dtype}")
                    return False
                    
            logging.info("All required numeric columns exist and are numeric")
            return True
        except Exception as e:
            raise NetworkSecurityException(e,sys)



            


    def detect_dataset_drift(self,base_df,current_df,threshold=0.05)->bool:
        try:
            status=True
            report={}
            for column in base_df.columns:
                d1=base_df[column]
                d2=current_df[column]
                is_same_dist=ks_2samp(d1,d2)
                if threshold<=is_same_dist.pvalue:
                    is_found=False
                else:
                    is_found=True
                    status=False
                report.update({column:{
                    "p_value":float(is_same_dist.pvalue),
                    "drift_status":is_found
                    
                    }})
            drift_report_file_path = self.data_validation_config.drift_report_file_path

            #Create directory
            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path,exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path,content=report)
            
            return status

        except Exception as e:
            raise NetworkSecurityException(e,sys)     




    def initiate_data_validation(self)->DataValidationArtifact:
        try:
            train_file_path=self.data_ingestion_artifact.train_file_path
            test_file_path=self.data_ingestion_artifact.test_file_path

            ## read the data from train and test
            train_dataframe=DataValidation.read_data(train_file_path)
            test_dataframe=DataValidation.read_data(test_file_path)
            
            ## validate number of columns
            validation_status = True
            error_message = ""

            status=self.validate_number_of_columns(df=train_dataframe)
            logging.info(f"Train dataframe column validation status: {status}")
            if not status:
                validation_status = False
                error_message += "Train dataframe does not contain all columns.\n"
                
            status = self.validate_number_of_columns(df=test_dataframe)
            logging.info(f"Test dataframe column validation status: {status}")
            if not status:
                validation_status = False
                error_message += "Test dataframe does not contain all columns.\n"

            ## validate numeric columns
            status=self.validate_numeric_columns_exist(df=train_dataframe)
            logging.info(f"Train dataframe numeric column validation status: {status}")
            if not status:
                validation_status = False
                error_message += "Train dataframe missing required numeric columns.\n"

            status=self.validate_numeric_columns_exist(df=test_dataframe)
            logging.info(f"Test dataframe numeric column validation status: {status}")
            if not status:
                validation_status = False
                error_message += "Test dataframe missing required numeric columns.\n"

            ## lets check datadrift
            drift_status=self.detect_dataset_drift(base_df=train_dataframe,current_df=test_dataframe)
            logging.info(f"Dataset drift detection status: {drift_status}")
            if not drift_status:
                validation_status = False
                error_message += "Dataset drift detected between train and test data.\n"

            logging.info(f"Final validation status: {validation_status}")
            if error_message:
                logging.error(f"Validation errors: {error_message}")

            dir_path=os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path,exist_ok=True)

            train_dataframe.to_csv(
                self.data_validation_config.valid_train_file_path, index=False, header=True
            )

            test_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path, index=False, header=True
            )
            
            data_validation_artifact = DataValidationArtifact(
                validation_status=validation_status,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=optional(str),
                invalid_test_file_path=optional(str),
                drift_report_file_path=self.data_validation_config.drift_report_file_path,
            )
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)



        