import os
import sys

from NetworkSecurity.exception.exception import NetworkSecurityException
from NetworkSecurity.logging.logger import logging

from NetworkSecurity.components.data_ingestion import DataIngestion
from NetworkSecurity.components.data_validation import DataValidation
from NetworkSecurity.components.data_transformation import DataTransformation
from NetworkSecurity.components.model_trainer import ModelTrainer

from NetworkSecurity.entity.config_entity import(
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
)

from NetworkSecurity.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
    DataTransformationArtifact,
    ModelTrainerArtifact,
)


import sys

class TrainingPipeline:
    def __init__(self):
        logging.info("TRAINING PIPELINE INITIALIZATION")
        self.training_pipeline_config = TrainingPipelineConfig()
        logging.info(f"Pipeline config initialized with timestamp: {self.training_pipeline_config.timestamp}")
        logging.info(f"Artifact directory: {self.training_pipeline_config.artifact_dir}")
        
    def start_data_ingestion(self) -> DataIngestionArtifact:
        logging.info("STAGE 1: DATA INGESTION")
        try:
            data_ingestion_config = DataIngestionConfig(self.training_pipeline_config)
            logging.info(f"Data ingestion config created")
            logging.info(f"Database: {data_ingestion_config.database_name}")
            logging.info(f"Collection: {data_ingestion_config.collection_name}")
            
            data_ingestion = DataIngestion(data_ingestion_config)
            logging.info("Data ingestion component initialized")
            
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            logging.info("Data ingestion completed successfully")
            logging.info(f"Training data: {data_ingestion_artifact.train_file_path}")
            logging.info(f"Test data: {data_ingestion_artifact.test_file_path}")
            return data_ingestion_artifact
        except Exception as e:
            logging.error("Data ingestion failed")
            raise NetworkSecurityException(e, sys)

    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact) -> DataValidationArtifact:
        logging.info("STAGE 2: DATA VALIDATION")
        try:
            data_validation_config = DataValidationConfig(self.training_pipeline_config)
            logging.info("Data validation config created")
            logging.info(f"Validation directory: {data_validation_config.data_validation_dir}")
            
            data_validation = DataValidation(
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_config=data_validation_config,
            )
            logging.info("Data validation component initialized")
            
            data_validation_artifact = data_validation.initiate_data_validation()
            logging.info("Data validation completed successfully")
            logging.info(f"Validation status: {data_validation_artifact.validation_status}")
            logging.info(f"Drift report: {data_validation_artifact.drift_report_file_path}")
            return data_validation_artifact
        except Exception as e:
            logging.error("Data validation failed")
            raise NetworkSecurityException(e, sys)

    def start_data_transformation(self, data_validation_artifact: DataValidationArtifact):
        logging.info("STAGE 3: DATA TRANSFORMATION")
        try:
            data_transformation_config = DataTransformationConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Data transformation config created")
            logging.info(f"Transformation directory: {data_transformation_config.data_transformation_dir}")
            
            data_transformation = DataTransformation(
                data_validation_artifact=data_validation_artifact,
                data_transformation_config=data_transformation_config
            )
            logging.info("Data transformation component initialized")
            
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            logging.info("Data transformation completed successfully")
            logging.info(f"Transformed train data: {data_transformation_artifact.transformed_train_file_path}")
            logging.info(f"Transformed test data: {data_transformation_artifact.transformed_test_file_path}")
            logging.info(f"Preprocessor object: {data_transformation_artifact.transformed_object_file_path}")
            return data_transformation_artifact
        except Exception as e:
            logging.error("Data transformation failed")
            raise NetworkSecurityException(e, sys)
        
    def start_model_trainer(self, data_transformation_artifact: DataTransformationArtifact) -> ModelTrainerArtifact:
        logging.info("STAGE 4: MODEL TRAINING")
        try:
            self.model_trainer_config: ModelTrainerConfig = ModelTrainerConfig(
                training_pipeline_config=self.training_pipeline_config
            )
            logging.info("Model trainer config created")
            logging.info(f"Model trainer directory: {self.model_trainer_config.model_trainer_dir}")

            model_trainer = ModelTrainer(
                data_transformation_artifact=data_transformation_artifact,
                model_trainer_config=self.model_trainer_config,
            )
            logging.info("Model trainer component initialized")

            model_trainer_artifact = model_trainer.initiate_model_trainer()
            logging.info("Model training completed successfully")
            logging.info(f"Trained model: {model_trainer_artifact.trained_model_file_path}")
            logging.info(f"Train F1 score: {model_trainer_artifact.train_metric_artifact.f1_score:.4f}")
            logging.info(f"Test F1 score: {model_trainer_artifact.test_metric_artifact.f1_score:.4f}")

            return model_trainer_artifact

        except Exception as e:
            logging.error("Model training failed")
            raise NetworkSecurityException(e, sys)

    def run_pipeline(self):
        logging.info("="*80)
        logging.info("TRAINING PIPELINE EXECUTION STARTED")
        logging.info("="*80)
        try:
            logging.info("Starting pipeline execution...")
            
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact = self.start_data_transformation(data_validation_artifact=data_validation_artifact)
            model_trainer_artifact = self.start_model_trainer(data_transformation_artifact=data_transformation_artifact)
            
            logging.info("="*80)
            logging.info("TRAINING PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
            logging.info("="*80)
            logging.info("PIPELINE SUMMARY:")
            logging.info(f"  1. Data Ingestion: {data_ingestion_artifact.train_file_path}")
            logging.info(f"  2. Data Validation: Status = {data_validation_artifact.validation_status}")
            logging.info(f"  3. Data Transformation: {data_transformation_artifact.transformed_train_file_path}")
            logging.info(f"  4. Model Training: {model_trainer_artifact.trained_model_file_path}")
            logging.info(f"  5. Best Model F1 Score: {model_trainer_artifact.test_metric_artifact.f1_score:.4f}")
            logging.info("="*80)
            
            return model_trainer_artifact
        except Exception as e:
            logging.error("="*80)
            logging.error("TRAINING PIPELINE EXECUTION FAILED")
            logging.error("="*80)
            logging.error(f"Pipeline error: {str(e)}")
            logging.error("Please check the error details above")
            logging.error("="*80)
            raise NetworkSecurityException(e, sys)                
