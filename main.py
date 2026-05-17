from NetworkSecurity.components.data_ingestion import DataIngestion
from NetworkSecurity.logging.logger import logging
from NetworkSecurity.exception.exception import NetworkSecurityException
from NetworkSecurity.entity.config_entity import DataIngestionConfig, TrainingPipelineConfig, DataValidationConfig, DataTransformationConfig, ModelTrainerConfig
from NetworkSecurity.components.data_validation import DataValidation
from NetworkSecurity.components.data_transformation import DataTransformation
from NetworkSecurity.components.model_trainer import ModelTrainer
from NetworkSecurity.entity.artifact_entity import DataIngestionArtifact, ModelTrainerArtifact
 
import sys



if __name__ == "__main__":
    try:
        logging.info("="*80)
        logging.info("NETWORK SECURITY ML PIPELINE - STARTING EXECUTION")
        logging.info("="*80)
        
        # Stage 1: Configuration Setup
        logging.info("STAGE 1: INITIALIZING PIPELINE CONFIGURATION")
        trainingpipelineconfig=TrainingPipelineConfig()
        logging.info(f"Pipeline timestamp: {trainingpipelineconfig.timestamp}")
        logging.info(f"Artifact directory: {trainingpipelineconfig.artifact_dir}")
        logging.info(f"Pipeline name: {trainingpipelineconfig.pipeline_name}")
        
        # Stage 2: Data Ingestion
        logging.info("-"*60)
        logging.info("STAGE 2: DATA INGESTION FROM MONGODB ATLAS")
        logging.info("-"*60)
        dataingestionconfig=DataIngestionConfig(trainingpipelineconfig)
        logging.info(f"Database: {dataingestionconfig.database_name}")
        logging.info(f"Collection: {dataingestionconfig.collection_name}")
        logging.info(f"Train-test split ratio: {dataingestionconfig.train_test_split_ratio}")
        
        data_ingestion=DataIngestion(dataingestionconfig)
        logging.info("Starting data ingestion process...")
        dataingestionartifact: DataIngestionArtifact = data_ingestion.initiate_data_ingestion()
        logging.info("Data ingestion completed successfully")
        logging.info(f"Training data path: {dataingestionartifact.train_file_path}")
        logging.info(f"Testing data path: {dataingestionartifact.test_file_path}")
        
        
        # Stage 3: Data Validation
        logging.info("-"*60)
        logging.info("STAGE 3: DATA VALIDATION AND DRIFT DETECTION")
        logging.info("-"*60)
        data_validation_config=DataValidationConfig(trainingpipelineconfig)
        from NetworkSecurity.constant.training_pipeline import SCHEMA_FILE_PATH
        logging.info(f"Schema file path: {SCHEMA_FILE_PATH}")
        logging.info(f"Drift report directory: {data_validation_config.drift_report_file_path}")
        
        data_validation=DataValidation(dataingestionartifact,data_validation_config)
        logging.info("Starting data validation process...")
        data_validation_artifact=data_validation.initiate_data_validation()
        logging.info("Data validation completed")
        logging.info(f"Validation status: {data_validation_artifact.validation_status}")
        logging.info(f"Drift report path: {data_validation_artifact.drift_report_file_path}")
        if not data_validation_artifact.validation_status:
            raise ValueError(
                "Data validation failed. Stopping pipeline before data transformation."
            )

        
        
        # Stage 4: Data Transformation
        logging.info("-"*60)
        logging.info("STAGE 4: DATA TRANSFORMATION AND PREPROCESSING")
        logging.info("-"*60)
        data_transformation_config=DataTransformationConfig(trainingpipelineconfig)
        logging.info(f"Transformation directory: {data_transformation_config.data_transformation_dir}")
        logging.info(f"Transformed train path: {data_transformation_config.transformed_train_file_path}")
        logging.info(f"Transformed test path: {data_transformation_config.transformed_test_file_path}")
        
        data_transformation=DataTransformation(data_validation_artifact,data_transformation_config)
        logging.info("Starting data transformation process...")
        data_transformation_artifact=data_transformation.initiate_data_transformation()
        logging.info("Data transformation completed successfully")
        logging.info(f"Preprocessor object path: {data_transformation_artifact.transformed_object_file_path}")
        
        
        # Stage 5: Model Training
        logging.info("-"*60)
        logging.info("STAGE 5: MODEL TRAINING AND EVALUATION")
        logging.info("-"*60)
        model_trainer_config = ModelTrainerConfig(trainingpipelineconfig)
        logging.info(f"Model directory: {model_trainer_config.model_trainer_dir}")
        logging.info(f"Trained model path: {model_trainer_config.trained_model_file_path}")
        
        model_trainer = ModelTrainer(model_trainer_config=model_trainer_config, data_transformation_artifact=data_transformation_artifact)
        logging.info("Starting model training process...")
        model_trainer_artifact: ModelTrainerArtifact = model_trainer.initiate_model_trainer()
        logging.info("Model training completed successfully")
        logging.info(f"Trained model path: {model_trainer_artifact.trained_model_file_path}")
        logging.info(f"Train metrics - F1: {model_trainer_artifact.train_metric_artifact.f1_score:.4f}")
        logging.info(f"Test metrics - F1: {model_trainer_artifact.test_metric_artifact.f1_score:.4f}")
        
        # Pipeline Completion Summary
        logging.info("="*80)
        logging.info("NETWORK SECURITY ML PIPELINE - EXECUTION COMPLETED")
        logging.info("="*80)
        logging.info("PIPELINE SUMMARY:")
        logging.info(f"  1. Data Ingestion: {dataingestionartifact.train_file_path}")
        logging.info(f"  2. Data Validation: Status = {data_validation_artifact.validation_status}")
        logging.info(f"  3. Data Transformation: {data_transformation_artifact.transformed_train_file_path}")
        logging.info(f"  4. Model Training: {model_trainer_artifact.trained_model_file_path}")
        logging.info(f"  5. Best Model F1 Score: {model_trainer_artifact.test_metric_artifact.f1_score:.4f}")
        logging.info("All pipeline stages completed successfully")
        logging.info("Model is ready for deployment")
        logging.info("="*80)

        
    except Exception as e:
        logging.error("="*80)
        logging.error("PIPELINE EXECUTION FAILED")
        logging.error("="*80)
        logging.error(f"Error occurred: {str(e)}")
        logging.error("Please check the error details above")
        logging.error("="*80)
        raise NetworkSecurityException(e, sys)
