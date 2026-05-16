import sys
import os
import mlflow
from NetworkSecurity.entity.config_entity import ModelTrainerConfig
from NetworkSecurity.exception.exception import NetworkSecurityException
from NetworkSecurity.logging.logger import logging
from NetworkSecurity.constant.training_pipeline import MLFLOW_EXPERIMENT_NAME, MLFLOW_TRACKING_URI
from NetworkSecurity.entity.artifact_entity import ModelTrainerArtifact, DataTransformationArtifact
from NetworkSecurity.utils.ml_utils.model.estimator import NetworkModel
from NetworkSecurity.utils.main_utils.utils import save_object, load_object
from NetworkSecurity.utils.main_utils.utils import load_numpy_array_data, evaluate_models
from NetworkSecurity.utils.ml_utils.metric.classification_metric import get_classification_score

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)

class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def track_mlflow(self, best_model, train_metric, test_metric, best_model_name: str):
        # mlflow.set_registry_uri("https://dagshub.com/krishnaik06/networksecurity.mlflow")
        # tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
        with mlflow.start_run():
            mlflow.log_param("best_model", best_model_name)
            mlflow.log_metric("train_f1_score", train_metric.f1_score)
            mlflow.log_metric("train_precision", train_metric.precision_score)
            mlflow.log_metric("train_recall_score", train_metric.recall_score)
            mlflow.log_metric("test_f1_score", test_metric.f1_score)
            mlflow.log_metric("test_precision", test_metric.precision_score)
            mlflow.log_metric("test_recall_score", test_metric.recall_score)
            mlflow.sklearn.log_model(best_model, "model")
            

    def train_model(self, X_train, y_train, x_test, y_test):
        logging.info("ENTERED MODEL TRAINING MODULE")
        try:
            logging.info("STEP 1: Initializing machine learning models")
            models = {
                "Random Forest": RandomForestClassifier(verbose=1),
                "Decision Tree": DecisionTreeClassifier(),
                "Gradient Boosting": GradientBoostingClassifier(verbose=1),
                "Logistic Regression": LogisticRegression(verbose=1),
                "AdaBoost": AdaBoostClassifier(),
            }
            logging.info(f"Models initialized: {list(models.keys())}")
            
            logging.info("STEP 2: Setting up hyperparameter grids for model tuning")
            params = {
                "Decision Tree": {
                    'criterion': ['gini', 'entropy', 'log_loss'],
                },
                "Random Forest": {
                    'n_estimators': [8, 16, 32, 256]
                },
                "Gradient Boosting": {
                    'learning_rate': [.1, .01, .001],
                    'subsample': [0.6, 0.75, 0.85, 0.9],
                    'n_estimators': [8, 16, 32, 64, 256]
                },
                "Logistic Regression": {},
                "AdaBoost": {
                    'learning_rate': [.1, .01, .001],
                    'n_estimators': [ 32, 64, 256]
                }
            }
            logging.info("Hyperparameter grids configured for all models")
            
            logging.info("STEP 3: Starting model evaluation with GridSearchCV")
            logging.info(f"Training data shape: {X_train.shape}")
            logging.info(f"Test data shape: {x_test.shape}")
            
            model_report: dict = evaluate_models(X_train=X_train, y_train=y_train, X_test=x_test, y_test=y_test,
                                          models=models, param=params)
            
            logging.info("STEP 4: Selecting best model based on F1 score")
            logging.info(f"Model evaluation report: {model_report}")
            
            # To get best model score from dict
            best_model_score = max(sorted(model_report.values()))
            logging.info(f"Best model F1 score: {best_model_score:.4f}")

            # To get best model name from dict
            best_model_name = list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]
            logging.info(f"Best model selected: {best_model_name}")
            
            best_model = models[best_model_name]
            logging.info("STEP 5: Generating predictions with best model")
            
            y_train_pred = best_model.predict(X_train)
            classification_train_metric = get_classification_score(y_true=y_train, y_pred=y_train_pred)
            logging.info(f"Training metrics - F1: {classification_train_metric.f1_score:.4f}, "
                       f"Precision: {classification_train_metric.precision_score:.4f}, "
                       f"Recall: {classification_train_metric.recall_score:.4f}")

            y_test_pred = best_model.predict(x_test)
            classification_test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred)
            logging.info(f"Test metrics - F1: {classification_test_metric.f1_score:.4f}, "
                       f"Precision: {classification_test_metric.precision_score:.4f}, "
                       f"Recall: {classification_test_metric.recall_score:.4f}")

            self.track_mlflow(
                best_model=best_model,
                train_metric=classification_train_metric,
                test_metric=classification_test_metric,
                best_model_name=best_model_name,
            )

            logging.info("STEP 6: Loading preprocessor object")
            preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
            logging.info("Preprocessor loaded successfully")
            
            logging.info("STEP 7: Creating model directory and saving trained model")
            model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
            os.makedirs(model_dir_path, exist_ok=True)
            logging.info(f"Model directory created: {model_dir_path}")

            Network_Model = NetworkModel(preprocessor=preprocessor, model=best_model)
            save_object(self.model_trainer_config.trained_model_file_path, obj=Network_Model)
            logging.info(f"Trained model saved to: {self.model_trainer_config.trained_model_file_path}")

            # Model Trainer Artifact
            logging.info("STEP 8: Creating model trainer artifact")
            model_trainer_artifact = ModelTrainerArtifact(trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                             train_metric_artifact=classification_train_metric,
                             test_metric_artifact=classification_test_metric
                             )
            
            logging.info("MODEL TRAINING COMPLETED SUCCESSFULLY")
            logging.info(f"Training summary:")
            logging.info(f"  - Best model: {best_model_name}")
            logging.info(f"  - Test F1 score: {best_model_score:.4f}")
            logging.info(f"  - Model saved: {self.model_trainer_config.trained_model_file_path}")
            logging.info(f"  - Train F1: {classification_train_metric.f1_score:.4f}")
            logging.info(f"  - Test F1: {classification_test_metric.f1_score:.4f}")
            
            return model_trainer_artifact

        except Exception as e:
            logging.error(f"MODEL TRAINING FAILED: {str(e)}")
            logging.error("Please check the error details above")
            raise NetworkSecurityException(e, sys)

  


             

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        logging.info("ENTERED INITIATE MODEL TRAINER METHOD")
        try:
            logging.info("STEP 1: Loading transformed training and test data")
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path
            
            logging.info(f"Loading training data from: {train_file_path}")
            logging.info(f"Loading test data from: {test_file_path}")

            # Loading training array and testing array
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)
            
            logging.info(f"Training array loaded successfully - Shape: {train_arr.shape}")
            logging.info(f"Test array loaded successfully - Shape: {test_arr.shape}")

            logging.info("STEP 2: Separating features and target variables")
            x_train, y_train, x_test, y_test = (
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1],
            )
            
            logging.info(f"Training features shape: {x_train.shape}")
            logging.info(f"Training target shape: {y_train.shape}")
            logging.info(f"Test features shape: {x_test.shape}")
            logging.info(f"Test target shape: {y_test.shape}")

            logging.info("STEP 3: Starting model training process")
            model_trainer_artifact = self.train_model(x_train, y_train, x_test, y_test)
            
            logging.info("MODEL TRAINER INITIATION COMPLETED SUCCESSFULLY")
            return model_trainer_artifact

        except Exception as e:
            logging.error(f"MODEL TRAINER INITIATION FAILED: {str(e)}")
            logging.error("Please check the error details above")
            raise NetworkSecurityException(e, sys)        
