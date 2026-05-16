import sys
import os
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

from NetworkSecurity.constant.training_pipeline import TARGET_COLUMN, DATA_TRANSFORMATION_IMPUTER_PARAMS
from NetworkSecurity.entity.config_entity import DataTransformationConfig
from NetworkSecurity.entity.artifact_entity import DataTransformationArtifact, DataValidationArtifact
from NetworkSecurity.exception.exception import NetworkSecurityException
from NetworkSecurity.logging.logger import logging
from NetworkSecurity.utils.main_utils.utils import save_object, save_numpy_array_data, load_object  


class DataTransformation:
    def __init__(self, data_validation_artifact: DataValidationArtifact,
                 data_transformation_config: DataTransformationConfig):
        try:
            self.data_validation_artifact = data_validation_artifact
            self.data_transformation_config = data_transformation_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    @staticmethod
    def get_data_transformer_object() -> Pipeline:
        """
        It initialises a KNNImputer object with the parameters specified in the training_pipeline.py file
        and returns a Pipeline object with the KNNImputer object as the first step.

        Returns:
          A Pipeline object
        """
        logging.info(
            "Entered get_data_transformer_object method of Transformation class"
        )
        try:
            imputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            logging.info(
                f"Initialise KNNImputer with {DATA_TRANSFORMATION_IMPUTER_PARAMS}"
            )
            processor = Pipeline([("imputer", imputer)])
            return processor
        except Exception as e:
            raise NetworkSecurityException(e, sys)

        
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        logging.info("ENTERED DATA TRANSFORMATION MODULE")
        try:
            logging.info("STEP 1: Loading validated datasets")
            logging.info(f"Loading training data from: {self.data_validation_artifact.valid_train_file_path}")
            logging.info(f"Loading test data from: {self.data_validation_artifact.valid_test_file_path}")
            
            train_df = DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)
            
            logging.info(f"Training data loaded successfully - Shape: {train_df.shape}")
            logging.info(f"Test data loaded successfully - Shape: {test_df.shape}")
            logging.info(f"Target column: {TARGET_COLUMN}")

            logging.info("STEP 2: Separating features and target variables")
            ## training dataframe
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN])
            target_feature_train_df = train_df[TARGET_COLUMN]
            target_feature_train_df = target_feature_train_df.replace(-1, 0)
            logging.info(f"Train features separated - Shape: {input_feature_train_df.shape}")
            logging.info(f"Train target prepared - Shape: {target_feature_train_df.shape}")
            logging.info("Target values mapped: -1 -> 0 (Legitimate), 1 -> 1 (Phishing)")

            # testing dataframe
            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN])
            target_feature_test_df = test_df[TARGET_COLUMN]
            target_feature_test_df = target_feature_test_df.replace(-1, 0)
            logging.info(f"Test features separated - Shape: {input_feature_test_df.shape}")
            logging.info(f"Test target prepared - Shape: {target_feature_test_df.shape}")

            logging.info("STEP 3: Initializing KNN imputer preprocessor")
            preprocessor = self.get_data_transformer_object()
            logging.info("KNN imputer preprocessor initialized successfully")

            logging.info("STEP 4: Fitting preprocessor on training data")
            preprocessor_object = preprocessor.fit(input_feature_train_df)
            logging.info("Preprocessor fitted on training data successfully")

            logging.info("STEP 5: Transforming training and test features")
            transformed_input_train_feature = preprocessor_object.transform(input_feature_train_df)
            transformed_input_test_feature = preprocessor_object.transform(input_feature_test_df)
            logging.info(f"Training features transformed - Shape: {transformed_input_train_feature.shape}")
            logging.info(f"Test features transformed - Shape: {transformed_input_test_feature.shape}")

            logging.info("STEP 6: Combining transformed features with target variables")
            train_arr = np.c_[transformed_input_train_feature, np.array(target_feature_train_df)]
            test_arr = np.c_[transformed_input_test_feature, np.array(target_feature_test_df)]
            logging.info(f"Final train array created - Shape: {train_arr.shape}")
            logging.info(f"Final test array created - Shape: {test_arr.shape}")

            logging.info("STEP 7: Saving transformed data and preprocessor objects")
            logging.info(f"Saving transformed train data to: {self.data_transformation_config.transformed_train_file_path}")
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, array=train_arr)
            
            logging.info(f"Saving transformed test data to: {self.data_transformation_config.transformed_test_file_path}")
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array=test_arr)
            
            logging.info(f"Saving preprocessor object to: {self.data_transformation_config.transformed_object_file_path}")
            save_object(self.data_transformation_config.transformed_object_file_path, preprocessor_object)


            save_object("final_model/preprocessor.pkl", preprocessor_object)
            
            logging.info("STEP 8: Creating data transformation artifact")
            data_transformation_artifact = DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )
            
            logging.info("DATA TRANSFORMATION COMPLETED SUCCESSFULLY")
            logging.info(f"Transformation summary:")
            logging.info(f"  - Input features: {input_feature_train_df.shape[1]} columns")
            logging.info(f"  - Training samples: {train_arr.shape[0]}")
            logging.info(f"  - Test samples: {test_arr.shape[0]}")
            logging.info(f"  - Preprocessor saved: {data_transformation_artifact.transformed_object_file_path}")
            
            return data_transformation_artifact

        except Exception as e:
            logging.error(f"DATA TRANSFORMATION FAILED: {str(e)}")
            logging.error("Please check the error details above")
            raise NetworkSecurityException(e, sys)
