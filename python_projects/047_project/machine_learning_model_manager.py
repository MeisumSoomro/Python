import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
from pathlib import Path
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import matplotlib.pyplot as plt
import seaborn as sns

class ModelType:
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"

class ModelManager:
    def __init__(self):
        self.models_dir = Path("models")
        self.data_dir = Path("datasets")
        self.config_file = Path("model_config.json")
        self.log_file = Path("model_training.log")
        self.setup_directories()
        self.setup_logging()
        self.load_config()
        self.current_model = None
        self.current_data = None
        self.current_scaler = None
        self.label_encoders = {}

    def setup_directories(self):
        """Create necessary directories"""
        self.models_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def load_config(self):
        """Load model configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "models": {},
                "datasets": {},
                "hyperparameters": {},
                "metrics": {}
            }
            self.save_config()

    def save_config(self):
        """Save model configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def load_data(self, file_path: str, target_column: str) -> bool:
        """Load dataset from file"""
        try:
            file_path = Path(file_path)
            if file_path.suffix.lower() == '.csv':
                data = pd.read_csv(file_path)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                data = pd.read_excel(file_path)
            else:
                logging.error("Unsupported file format")
                return False

            if target_column not in data.columns:
                logging.error(f"Target column '{target_column}' not found")
                return False

            self.current_data = {
                'X': data.drop(columns=[target_column]),
                'y': data[target_column],
                'file_name': file_path.name
            }

            # Save dataset info
            self.config["datasets"][file_path.name] = {
                "features": list(self.current_data['X'].columns),
                "target": target_column,
                "rows": len(data),
                "columns": len(data.columns),
                "loaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.save_config()

            logging.info(f"Loaded dataset: {file_path.name}")
            return True

        except Exception as e:
            logging.error(f"Error loading data: {e}")
            return False

    def preprocess_data(self, test_size: float = 0.2, random_state: int = 42) -> bool:
        """Preprocess the loaded data"""
        try:
            if self.current_data is None:
                logging.error("No data loaded")
                return False

            X = self.current_data['X']
            y = self.current_data['y']

            # Handle categorical features
            for column in X.select_dtypes(include=['object']).columns:
                le = LabelEncoder()
                X[column] = le.fit_transform(X[column])
                self.label_encoders[column] = le

            # Scale features
            self.current_scaler = StandardScaler()
            X_scaled = self.current_scaler.fit_transform(X)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=test_size, random_state=random_state
            )

            self.current_data.update({
                'X_train': X_train,
                'X_test': X_test,
                'y_train': y_train,
                'y_test': y_test
            })

            logging.info("Data preprocessing completed")
            return True

        except Exception as e:
            logging.error(f"Error preprocessing data: {e}")
            return False

    def train_model(self, model_type: str, model_name: str, model_instance: Any,
                   hyperparameters: Dict = None) -> bool:
        """Train a machine learning model"""
        try:
            if self.current_data is None:
                logging.error("No data loaded")
                return False

            if 'X_train' not in self.current_data:
                logging.error("Data not preprocessed")
                return False

            # Train model
            model_instance.fit(self.current_data['X_train'], self.current_data['y_train'])
            self.current_model = model_instance

            # Save model info
            model_info = {
                "type": model_type,
                "name": model_name,
                "hyperparameters": hyperparameters or model_instance.get_params(),
                "features": list(self.current_data['X'].columns),
                "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "dataset": self.current_data['file_name']
            }

            self.config["models"][model_name] = model_info
            self.save_config()

            # Save model file
            model_path = self.models_dir / f"{model_name}.joblib"
            joblib.dump(model_instance, model_path)

            logging.info(f"Model {model_name} trained and saved")
            return True

        except Exception as e:
            logging.error(f"Error training model: {e}")
            return False

    def evaluate_model(self, model_name: str) -> Dict:
        """Evaluate model performance"""
        try:
            if self.current_model is None:
                logging.error("No model loaded")
                return {}

            if 'X_test' not in self.current_data:
                logging.error("Test data not available")
                return {}

            y_pred = self.current_model.predict(self.current_data['X_test'])
            
            metrics = {
                "accuracy": accuracy_score(self.current_data['y_test'], y_pred),
                "precision": precision_score(self.current_data['y_test'], y_pred, average='weighted'),
                "recall": recall_score(self.current_data['y_test'], y_pred, average='weighted'),
                "f1": f1_score(self.current_data['y_test'], y_pred, average='weighted')
            }

            self.config["metrics"][model_name] = {
                "metrics": metrics,
                "evaluated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.save_config()

            logging.info(f"Model {model_name} evaluated")
            return metrics

        except Exception as e:
            logging.error(f"Error evaluating model: {e}")
            return {}

    def load_model(self, model_name: str) -> bool:
        """Load a saved model"""
        try:
            model_path = self.models_dir / f"{model_name}.joblib"
            if not model_path.exists():
                logging.error(f"Model {model_name} not found")
                return False

            self.current_model = joblib.load(model_path)
            logging.info(f"Model {model_name} loaded")
            return True

        except Exception as e:
            logging.error(f"Error loading model: {e}")
            return False

    def predict(self, data: pd.DataFrame) -> Optional[np.ndarray]:
        """Make predictions using current model"""
        try:
            if self.current_model is None:
                logging.error("No model loaded")
                return None

            # Preprocess input data
            for column in data.select_dtypes(include=['object']).columns:
                if column in self.label_encoders:
                    data[column] = self.label_encoders[column].transform(data[column])

            if self.current_scaler is not None:
                data = self.current_scaler.transform(data)

            predictions = self.current_model.predict(data)
            return predictions

        except Exception as e:
            logging.error(f"Error making predictions: {e}")
            return None

    def plot_feature_importance(self, model_name: str, output_path: Optional[str] = None):
        """Plot feature importance"""
        try:
            if self.current_model is None or self.current_data is None:
                logging.error("Model or data not loaded")
                return

            if not hasattr(self.current_model, 'feature_importances_'):
                logging.error("Model doesn't support feature importance")
                return

            plt.figure(figsize=(10, 6))
            features = self.current_data['X'].columns
            importances = self.current_model.feature_importances_
            indices = np.argsort(importances)[::-1]

            plt.title(f"Feature Importances ({model_name})")
            plt.bar(range(len(importances)), importances[indices])
            plt.xticks(range(len(importances)), [features[i] for i in indices], rotation=45)
            plt.tight_layout()

            if output_path:
                plt.savefig(output_path)
                logging.info(f"Feature importance plot saved to {output_path}")
            else:
                plt.show()
            plt.close()

        except Exception as e:
            logging.error(f"Error plotting feature importance: {e}")

    def plot_confusion_matrix(self, model_name: str, output_path: Optional[str] = None):
        """Plot confusion matrix"""
        try:
            if self.current_model is None or self.current_data is None:
                logging.error("Model or data not loaded")
                return

            y_pred = self.current_model.predict(self.current_data['X_test'])
            cm = pd.crosstab(self.current_data['y_test'], y_pred)

            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
            plt.title(f"Confusion Matrix ({model_name})")
            plt.ylabel('True Label')
            plt.xlabel('Predicted Label')
            plt.tight_layout()

            if output_path:
                plt.savefig(output_path)
                logging.info(f"Confusion matrix plot saved to {output_path}")
            else:
                plt.show()
            plt.close()

        except Exception as e:
            logging.error(f"Error plotting confusion matrix: {e}")

def main():
    manager = ModelManager()
    
    while True:
        print("\nMachine Learning Model Manager")
        print("1. Load Dataset")
        print("2. Preprocess Data")
        print("3. Train Model")
        print("4. Evaluate Model")
        print("5. Load Model")
        print("6. Make Predictions")
        print("7. Plot Feature Importance")
        print("8. Plot Confusion Matrix")
        print("9. Exit")
        
        choice = input("\nEnter your choice (1-9): ")
        
        if choice == "1":
            file_path = input("Enter dataset path: ")
            target = input("Enter target column name: ")
            if manager.load_data(file_path, target):
                print("Dataset loaded successfully!")
            else:
                print("Failed to load dataset!")
        
        elif choice == "2":
            test_size = float(input("Enter test size (0-1): "))
            if manager.preprocess_data(test_size=test_size):
                print("Data preprocessing completed!")
            else:
                print("Failed to preprocess data!")
        
        elif choice == "3":
            print("\nModel Types:")
            print("1. Classification")
            print("2. Regression")
            print("3. Clustering")
            
            model_type = input("Choose model type (1-3): ")
            model_name = input("Enter model name: ")
            
            # This is a simplified version - in practice, you'd have more model options
            from sklearn.ensemble import RandomForestClassifier
            model = RandomForestClassifier()
            
            if manager.train_model(ModelType.CLASSIFICATION, model_name, model):
                print("Model trained successfully!")
            else:
                print("Failed to train model!")
        
        elif choice == "4":
            model_name = input("Enter model name: ")
            metrics = manager.evaluate_model(model_name)
            if metrics:
                print("\nModel Metrics:")
                for metric, value in metrics.items():
                    print(f"{metric}: {value:.4f}")
            else:
                print("Failed to evaluate model!")
        
        elif choice == "5":
            model_name = input("Enter model name: ")
            if manager.load_model(model_name):
                print("Model loaded successfully!")
            else:
                print("Failed to load model!")
        
        elif choice == "6":
            if manager.current_model is None:
                print("Please load a model first!")
                continue
            
            # This is a simplified version - in practice, you'd need proper data input
            print("Feature input not implemented in this demo")
        
        elif choice == "7":
            model_name = input("Enter model name: ")
            save = input("Save plot to file? (y/n): ").lower() == 'y'
            if save:
                output_path = input("Enter output file path: ")
                manager.plot_feature_importance(model_name, output_path)
            else:
                manager.plot_feature_importance(model_name)
        
        elif choice == "8":
            model_name = input("Enter model name: ")
            save = input("Save plot to file? (y/n): ").lower() == 'y'
            if save:
                output_path = input("Enter output file path: ")
                manager.plot_confusion_matrix(model_name, output_path)
            else:
                manager.plot_confusion_matrix(model_name)
        
        elif choice == "9":
            print("Thank you for using Machine Learning Model Manager!")
            break
        
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 