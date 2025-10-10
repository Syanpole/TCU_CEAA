"""
🚀 Production AI Detector Training and Deployment System
Complete production-ready system for training, evaluating, and deploying AI detection models
Part of the TCU-CEAA AI Document Verification System
"""

import os
import sys
import json
import pickle
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import (
    train_test_split, cross_val_score, GridSearchCV, 
    RandomizedSearchCV, StratifiedKFold
)
from sklearn.ensemble import (
    RandomForestClassifier, VotingClassifier, 
    BaggingClassifier, AdaBoostClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    roc_curve, precision_recall_curve, accuracy_score,
    precision_score, recall_score, f1_score, average_precision_score
)
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TrainingConfig:
    """Configuration for training pipeline"""
    models_to_train: List[str]
    hyperparameter_tuning: bool = True
    cross_validation_folds: int = 5
    test_size: float = 0.2
    validation_size: float = 0.15
    random_state: int = 42
    n_jobs: int = -1
    scoring_metric: str = 'roc_auc'
    early_stopping: bool = True
    ensemble_methods: List[str] = None
    
    def __post_init__(self):
        if self.ensemble_methods is None:
            self.ensemble_methods = ['voting', 'stacking']

@dataclass
class ModelEvaluation:
    """Comprehensive model evaluation results"""
    model_name: str
    training_time: float
    prediction_time: float
    
    # Performance metrics
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    average_precision: float
    
    # Detailed results
    confusion_matrix: List[List[int]]
    classification_report: Dict
    cross_val_scores: List[float]
    roc_curve_data: Tuple[np.ndarray, np.ndarray, np.ndarray]
    pr_curve_data: Tuple[np.ndarray, np.ndarray, np.ndarray]
    
    # Feature analysis
    feature_importance: Dict[str, float] = None
    feature_selection: List[str] = None
    
    # Model complexity
    model_size: int = 0
    inference_memory: float = 0.0
    
    # Stability metrics
    prediction_stability: float = 0.0
    cross_val_std: float = 0.0

class ProductionAIDetectorTrainer:
    """Production-ready AI detector training system"""
    
    def __init__(self, config: TrainingConfig, output_dir: str = "production_models"):
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.models = {}
        self.evaluations = {}
        self.best_model = None
        self.ensemble_models = {}
        
        # Create subdirectories
        (self.output_dir / "trained_models").mkdir(exist_ok=True)
        (self.output_dir / "evaluations").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)
        (self.output_dir / "plots").mkdir(exist_ok=True)
        
        # Initialize tracking database
        self.init_tracking_database()
        
    def init_tracking_database(self):
        """Initialize model tracking database"""
        db_path = self.output_dir / "model_tracking.db"
        
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS training_runs (
                    run_id TEXT PRIMARY KEY,
                    start_time TEXT,
                    end_time TEXT,
                    config TEXT,
                    best_model TEXT,
                    best_score REAL,
                    total_models INTEGER,
                    status TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS model_performance (
                    model_id TEXT PRIMARY KEY,
                    run_id TEXT,
                    model_name TEXT,
                    training_time REAL,
                    accuracy REAL,
                    precision_score REAL,
                    recall_score REAL,
                    f1_score REAL,
                    roc_auc REAL,
                    cross_val_mean REAL,
                    cross_val_std REAL,
                    model_path TEXT,
                    evaluation_path TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS deployment_history (
                    deployment_id TEXT PRIMARY KEY,
                    model_id TEXT,
                    deployment_time TEXT,
                    environment TEXT,
                    version TEXT,
                    performance_baseline REAL,
                    status TEXT
                )
            """)
    
    def train_all_models(self, X: np.ndarray, y: np.ndarray) -> Dict[str, ModelEvaluation]:
        """Train all configured models with comprehensive evaluation"""
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        logger.info(f"Starting training run: {run_id}")
        logger.info(f"Dataset shape: {X.shape}")
        logger.info(f"Models to train: {self.config.models_to_train}")
        
        # Split data
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, 
            test_size=self.config.test_size + self.config.validation_size,
            stratify=y, 
            random_state=self.config.random_state
        )
        
        val_size_adjusted = self.config.validation_size / (self.config.test_size + self.config.validation_size)
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp,
            test_size=1 - val_size_adjusted,
            stratify=y_temp,
            random_state=self.config.random_state
        )
        
        logger.info(f"Train set: {X_train.shape}, Val set: {X_val.shape}, Test set: {X_test.shape}")
        
        # Train models in parallel
        model_definitions = self._get_model_definitions()
        evaluations = {}
        
        with ThreadPoolExecutor(max_workers=min(len(model_definitions), 4)) as executor:
            future_to_model = {
                executor.submit(
                    self._train_and_evaluate_model,
                    name, definition, X_train, y_train, X_val, y_val, X_test, y_test
                ): name for name, definition in model_definitions.items()
                if name in self.config.models_to_train
            }
            
            for future in as_completed(future_to_model):
                model_name = future_to_model[future]
                try:
                    evaluation = future.result()
                    evaluations[model_name] = evaluation
                    self.evaluations[model_name] = evaluation
                    logger.info(f"Completed training {model_name}: ROC-AUC = {evaluation.roc_auc:.4f}")
                except Exception as e:
                    logger.error(f"Training failed for {model_name}: {e}")
        
        # Train ensemble models if requested
        if len(evaluations) > 1:
            ensemble_evaluations = self._train_ensemble_models(
                X_train, y_train, X_val, y_val, X_test, y_test
            )
            evaluations.update(ensemble_evaluations)
        
        # Find best model
        best_score = 0
        best_model_name = None
        for name, evaluation in evaluations.items():
            if evaluation.roc_auc > best_score:
                best_score = evaluation.roc_auc
                best_model_name = name
        
        self.best_model = best_model_name
        
        # Save training run info
        end_time = datetime.now()
        self._save_training_run(run_id, start_time, end_time, evaluations, best_model_name, best_score)
        
        # Generate comprehensive report
        self._generate_training_report(run_id, evaluations)
        
        logger.info(f"Training completed. Best model: {best_model_name} (ROC-AUC: {best_score:.4f})")
        
        return evaluations
    
    def _get_model_definitions(self) -> Dict[str, Dict]:
        """Get model definitions with hyperparameter ranges"""
        definitions = {
            'random_forest': {
                'model': RandomForestClassifier(random_state=self.config.random_state, n_jobs=self.config.n_jobs),
                'param_grid': {
                    'n_estimators': [50, 100, 200, 300],
                    'max_depth': [10, 20, 30, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4],
                    'max_features': ['sqrt', 'log2', None]
                },
                'use_scaler': False
            },
            'logistic_regression': {
                'model': LogisticRegression(random_state=self.config.random_state, max_iter=1000),
                'param_grid': {
                    'C': [0.001, 0.01, 0.1, 1, 10, 100],
                    'penalty': ['l1', 'l2', 'elasticnet'],
                    'solver': ['liblinear', 'saga']
                },
                'use_scaler': True
            },
            'svm': {
                'model': SVC(probability=True, random_state=self.config.random_state),
                'param_grid': {
                    'C': [0.1, 1, 10, 100],
                    'gamma': ['scale', 'auto', 0.001, 0.01, 0.1, 1],
                    'kernel': ['rbf', 'poly', 'sigmoid']
                },
                'use_scaler': True
            }
        }
        
        # Add XGBoost if available
        if XGBOOST_AVAILABLE:
            definitions['xgboost'] = {
                'model': xgb.XGBClassifier(
                    random_state=self.config.random_state,
                    eval_metric='logloss',
                    n_jobs=self.config.n_jobs
                ),
                'param_grid': {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [3, 6, 9, 12],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'subsample': [0.8, 0.9, 1.0],
                    'colsample_bytree': [0.8, 0.9, 1.0]
                },
                'use_scaler': False
            }
        
        # Add LightGBM if available
        if LIGHTGBM_AVAILABLE:
            definitions['lightgbm'] = {
                'model': lgb.LGBMClassifier(
                    random_state=self.config.random_state,
                    n_jobs=self.config.n_jobs
                ),
                'param_grid': {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [3, 6, 9],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'num_leaves': [31, 50, 100],
                    'subsample': [0.8, 0.9, 1.0]
                },
                'use_scaler': False
            }
        
        # Add Neural Network if TensorFlow is available
        if TF_AVAILABLE:
            definitions['neural_network'] = {
                'model': self._create_neural_network,
                'param_grid': {
                    'hidden_layers': [1, 2, 3],
                    'neurons': [32, 64, 128],
                    'dropout_rate': [0.1, 0.3, 0.5],
                    'learning_rate': [0.001, 0.01, 0.1]
                },
                'use_scaler': True
            }
        
        return definitions
    
    def _train_and_evaluate_model(self, name: str, definition: Dict, 
                                X_train: np.ndarray, y_train: np.ndarray,
                                X_val: np.ndarray, y_val: np.ndarray,
                                X_test: np.ndarray, y_test: np.ndarray) -> ModelEvaluation:
        """Train and evaluate a single model"""
        logger.info(f"Training {name}...")
        
        start_time = datetime.now()
        
        # Prepare data
        if definition['use_scaler']:
            scaler = RobustScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_val_scaled = scaler.transform(X_val)
            X_test_scaled = scaler.transform(X_test)
        else:
            scaler = None
            X_train_scaled = X_train
            X_val_scaled = X_val
            X_test_scaled = X_test
        
        # Hyperparameter tuning
        if self.config.hyperparameter_tuning:
            if name == 'neural_network':
                # Special handling for neural networks
                best_model = self._tune_neural_network(
                    definition, X_train_scaled, y_train, X_val_scaled, y_val
                )
            else:
                # Use GridSearchCV for traditional ML models
                cv = StratifiedKFold(
                    n_splits=self.config.cross_validation_folds,
                    shuffle=True,
                    random_state=self.config.random_state
                )
                
                # Use RandomizedSearchCV for faster tuning with large param grids
                if len(definition['param_grid']) > 20:
                    search = RandomizedSearchCV(
                        definition['model'],
                        definition['param_grid'],
                        n_iter=50,
                        cv=cv,
                        scoring=self.config.scoring_metric,
                        random_state=self.config.random_state,
                        n_jobs=self.config.n_jobs
                    )
                else:
                    search = GridSearchCV(
                        definition['model'],
                        definition['param_grid'],
                        cv=cv,
                        scoring=self.config.scoring_metric,
                        n_jobs=self.config.n_jobs
                    )
                
                search.fit(X_train_scaled, y_train)
                best_model = search.best_estimator_
        else:
            # Use default parameters
            if name == 'neural_network':
                best_model = self._create_neural_network(X_train_scaled.shape[1])
                best_model.fit(
                    X_train_scaled, y_train,
                    validation_data=(X_val_scaled, y_val),
                    epochs=100,
                    batch_size=32,
                    verbose=0,
                    callbacks=[
                        keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True)
                    ]
                )
            else:
                best_model = definition['model']
                best_model.fit(X_train_scaled, y_train)
        
        training_time = (datetime.now() - start_time).total_seconds()
        
        # Evaluate model
        evaluation = self._evaluate_model(
            best_model, name, scaler,
            X_train_scaled, y_train, X_val_scaled, y_val, X_test_scaled, y_test
        )
        evaluation.training_time = training_time
        
        # Save model
        self._save_model(name, best_model, scaler, evaluation)
        
        return evaluation
    
    def _create_neural_network(self, input_dim: int, hidden_layers: int = 2, 
                              neurons: int = 64, dropout_rate: float = 0.3,
                              learning_rate: float = 0.001):
        """Create neural network model"""
        model = keras.Sequential([
            layers.Input(shape=(input_dim,)),
            layers.BatchNormalization()
        ])
        
        # Add hidden layers
        for i in range(hidden_layers):
            model.add(layers.Dense(neurons, activation='relu'))
            model.add(layers.Dropout(dropout_rate))
            model.add(layers.BatchNormalization())
            
            # Reduce neurons in subsequent layers
            neurons = max(16, neurons // 2)
        
        # Output layer
        model.add(layers.Dense(1, activation='sigmoid'))
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        return model
    
    def _tune_neural_network(self, definition: Dict, X_train: np.ndarray, y_train: np.ndarray,
                            X_val: np.ndarray, y_val: np.ndarray):
        """Tune neural network hyperparameters"""
        best_score = 0
        best_model = None
        
        param_grid = definition['param_grid']
        
        # Random search for neural network parameters
        for _ in range(20):  # Try 20 random combinations
            params = {}
            for param, values in param_grid.items():
                params[param] = np.random.choice(values)
            
            # Create and train model
            model = self._create_neural_network(X_train.shape[1], **params)
            
            history = model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=50,
                batch_size=32,
                verbose=0,
                callbacks=[
                    keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True)
                ]
            )
            
            # Evaluate on validation set
            val_pred = model.predict(X_val, verbose=0)
            val_score = roc_auc_score(y_val, val_pred)
            
            if val_score > best_score:
                best_score = val_score
                best_model = model
        
        return best_model
    
    def _evaluate_model(self, model, model_name: str, scaler,
                       X_train: np.ndarray, y_train: np.ndarray,
                       X_val: np.ndarray, y_val: np.ndarray,
                       X_test: np.ndarray, y_test: np.ndarray) -> ModelEvaluation:
        """Comprehensive model evaluation"""
        
        # Prediction timing
        pred_start = datetime.now()
        if hasattr(model, 'predict_proba'):
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            y_pred = (y_pred_proba >= 0.5).astype(int)
        else:  # Neural network
            y_pred_proba = model.predict(X_test, verbose=0).flatten()
            y_pred = (y_pred_proba >= 0.5).astype(int)
        prediction_time = (datetime.now() - pred_start).total_seconds()
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        avg_precision = average_precision_score(y_test, y_pred_proba)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        
        # Classification report
        class_report = classification_report(y_test, y_pred, output_dict=True)
        
        # Cross-validation scores
        if hasattr(model, 'predict_proba') and scaler is not None:
            # For sklearn models with scaler
            pipeline = Pipeline([('scaler', scaler), ('model', model)])
            cv_scores = cross_val_score(
                pipeline, X_train, y_train,
                cv=self.config.cross_validation_folds,
                scoring=self.config.scoring_metric
            )
        elif hasattr(model, 'predict_proba'):
            # For sklearn models without scaler
            cv_scores = cross_val_score(
                model, X_train, y_train,
                cv=self.config.cross_validation_folds,
                scoring=self.config.scoring_metric
            )
        else:
            # For neural networks, use manual CV
            cv_scores = self._manual_cross_validation(model, X_train, y_train, scaler)
        
        # ROC and PR curves
        fpr, tpr, roc_thresholds = roc_curve(y_test, y_pred_proba)
        precision_curve, recall_curve, pr_thresholds = precision_recall_curve(y_test, y_pred_proba)
        
        # Feature importance (if available)
        feature_importance = {}
        if hasattr(model, 'feature_importances_'):
            # For tree-based models
            feature_names = [f'feature_{i}' for i in range(len(model.feature_importances_))]
            feature_importance = dict(zip(feature_names, model.feature_importances_))
        elif hasattr(model, 'coef_'):
            # For linear models
            feature_names = [f'feature_{i}' for i in range(len(model.coef_[0]))]
            feature_importance = dict(zip(feature_names, np.abs(model.coef_[0])))
        
        # Model complexity metrics
        model_size = self._calculate_model_size(model)
        
        # Create evaluation object
        evaluation = ModelEvaluation(
            model_name=model_name,
            training_time=0,  # Will be set by caller
            prediction_time=prediction_time,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            roc_auc=roc_auc,
            average_precision=avg_precision,
            confusion_matrix=cm.tolist(),
            classification_report=class_report,
            cross_val_scores=cv_scores.tolist(),
            roc_curve_data=(fpr, tpr, roc_thresholds),
            pr_curve_data=(precision_curve, recall_curve, pr_thresholds),
            feature_importance=feature_importance,
            model_size=model_size,
            cross_val_std=np.std(cv_scores)
        )
        
        return evaluation
    
    def _manual_cross_validation(self, model_template, X: np.ndarray, y: np.ndarray, scaler) -> np.ndarray:
        """Manual cross-validation for neural networks"""
        cv_scores = []
        kfold = StratifiedKFold(
            n_splits=self.config.cross_validation_folds,
            shuffle=True,
            random_state=self.config.random_state
        )
        
        for train_idx, val_idx in kfold.split(X, y):
            X_train_fold, X_val_fold = X[train_idx], X[val_idx]
            y_train_fold, y_val_fold = y[train_idx], y[val_idx]
            
            # Create new model instance
            model = self._create_neural_network(X.shape[1])
            
            # Train
            model.fit(
                X_train_fold, y_train_fold,
                validation_data=(X_val_fold, y_val_fold),
                epochs=30,
                batch_size=32,
                verbose=0,
                callbacks=[
                    keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True)
                ]
            )
            
            # Evaluate
            y_pred_proba = model.predict(X_val_fold, verbose=0).flatten()
            score = roc_auc_score(y_val_fold, y_pred_proba)
            cv_scores.append(score)
        
        return np.array(cv_scores)
    
    def _train_ensemble_models(self, X_train: np.ndarray, y_train: np.ndarray,
                              X_val: np.ndarray, y_val: np.ndarray,
                              X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, ModelEvaluation]:
        """Train ensemble models"""
        logger.info("Training ensemble models...")
        
        ensemble_evaluations = {}
        
        # Get base models (excluding neural networks for sklearn ensembles)
        base_models = []
        for name, model_data in self.models.items():
            if hasattr(model_data['model'], 'predict_proba'):
                base_models.append((name, model_data['model']))
        
        if len(base_models) < 2:
            logger.warning("Not enough base models for ensemble training")
            return ensemble_evaluations
        
        # Voting Classifier
        if 'voting' in self.config.ensemble_methods:
            voting_clf = VotingClassifier(
                estimators=base_models,
                voting='soft'
            )
            
            voting_clf.fit(X_train, y_train)
            
            evaluation = self._evaluate_model(
                voting_clf, 'voting_ensemble', None,
                X_train, y_train, X_val, y_val, X_test, y_test
            )
            
            ensemble_evaluations['voting_ensemble'] = evaluation
            self.ensemble_models['voting_ensemble'] = voting_clf
        
        # Bagging ensemble
        if len(base_models) > 0:
            # Use the best performing base model for bagging
            best_base = max(base_models, key=lambda x: self.evaluations[x[0]].roc_auc)
            
            bagging_clf = BaggingClassifier(
                base_estimator=best_base[1],
                n_estimators=10,
                random_state=self.config.random_state,
                n_jobs=self.config.n_jobs
            )
            
            bagging_clf.fit(X_train, y_train)
            
            evaluation = self._evaluate_model(
                bagging_clf, 'bagging_ensemble', None,
                X_train, y_train, X_val, y_val, X_test, y_test
            )
            
            ensemble_evaluations['bagging_ensemble'] = evaluation
            self.ensemble_models['bagging_ensemble'] = bagging_clf
        
        return ensemble_evaluations
    
    def _calculate_model_size(self, model) -> int:
        """Calculate approximate model size in bytes"""
        try:
            if hasattr(model, 'get_weights'):  # TensorFlow model
                total_params = sum(np.prod(w.shape) for w in model.get_weights())
                return total_params * 4  # Assume float32
            else:  # Sklearn model
                import pickle
                return len(pickle.dumps(model))
        except:
            return 0
    
    def _save_model(self, name: str, model, scaler, evaluation: ModelEvaluation):
        """Save trained model and metadata"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save model
        model_path = self.output_dir / "trained_models" / f"{name}_{timestamp}.pkl"
        
        if hasattr(model, 'save'):  # TensorFlow model
            model_dir = self.output_dir / "trained_models" / f"{name}_{timestamp}"
            model.save(model_dir)
            model_path = model_dir
        else:  # Sklearn model
            with open(model_path, 'wb') as f:
                pickle.dump({
                    'model': model,
                    'scaler': scaler,
                    'timestamp': timestamp,
                    'evaluation': evaluation
                }, f)
        
        # Save evaluation
        eval_path = self.output_dir / "evaluations" / f"{name}_evaluation_{timestamp}.json"
        with open(eval_path, 'w') as f:
            # Convert evaluation to dict, handling numpy arrays
            eval_dict = asdict(evaluation)
            # Convert numpy arrays to lists for JSON serialization
            for key, value in eval_dict.items():
                if isinstance(value, tuple) and len(value) == 3:  # ROC/PR curve data
                    eval_dict[key] = [arr.tolist() if hasattr(arr, 'tolist') else arr for arr in value]
        
            json.dump(eval_dict, f, indent=2, default=str)
        
        # Store in memory
        self.models[name] = {
            'model': model,
            'scaler': scaler,
            'evaluation': evaluation,
            'model_path': str(model_path),
            'eval_path': str(eval_path)
        }
        
        logger.info(f"Saved {name} model to {model_path}")
    
    def _save_training_run(self, run_id: str, start_time: datetime, end_time: datetime,
                          evaluations: Dict[str, ModelEvaluation], best_model: str, best_score: float):
        """Save training run information to database"""
        db_path = self.output_dir / "model_tracking.db"
        
        with sqlite3.connect(db_path) as conn:
            # Save training run
            conn.execute("""
                INSERT INTO training_runs VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                start_time.isoformat(),
                end_time.isoformat(),
                json.dumps(asdict(self.config)),
                best_model,
                best_score,
                len(evaluations),
                'completed'
            ))
            
            # Save individual model performances
            for name, evaluation in evaluations.items():
                model_id = f"{run_id}_{name}"
                conn.execute("""
                    INSERT INTO model_performance VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    model_id,
                    run_id,
                    name,
                    evaluation.training_time,
                    evaluation.accuracy,
                    evaluation.precision,
                    evaluation.recall,
                    evaluation.f1_score,
                    evaluation.roc_auc,
                    np.mean(evaluation.cross_val_scores),
                    evaluation.cross_val_std,
                    self.models.get(name, {}).get('model_path', ''),
                    self.models.get(name, {}).get('eval_path', '')
                ))
    
    def _generate_training_report(self, run_id: str, evaluations: Dict[str, ModelEvaluation]):
        """Generate comprehensive training report"""
        report_path = self.output_dir / "reports" / f"training_report_{run_id}.html"
        
        # Create visualizations
        self._create_performance_plots(evaluations, run_id)
        
        # Generate HTML report
        html_content = self._create_html_report(run_id, evaluations)
        
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        logger.info(f"Training report saved to {report_path}")
    
    def _create_performance_plots(self, evaluations: Dict[str, ModelEvaluation], run_id: str):
        """Create performance visualization plots"""
        plots_dir = self.output_dir / "plots" / run_id
        plots_dir.mkdir(exist_ok=True)
        
        # Model comparison bar chart
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        models = list(evaluations.keys())
        metrics = {
            'Accuracy': [evaluations[m].accuracy for m in models],
            'Precision': [evaluations[m].precision for m in models],
            'Recall': [evaluations[m].recall for m in models],
            'F1-Score': [evaluations[m].f1_score for m in models],
            'ROC-AUC': [evaluations[m].roc_auc for m in models]
        }
        
        # Bar plots for each metric
        for i, (metric, values) in enumerate(list(metrics.items())[:4]):
            ax = axes[i//2, i%2]
            bars = ax.bar(models, values)
            ax.set_title(f'{metric} Comparison')
            ax.set_ylabel(metric)
            ax.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                       f'{value:.3f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(plots_dir / 'model_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # ROC curves
        plt.figure(figsize=(10, 8))
        for name, evaluation in evaluations.items():
            fpr, tpr, _ = evaluation.roc_curve_data
            plt.plot(fpr, tpr, label=f'{name} (AUC = {evaluation.roc_auc:.3f})')
        
        plt.plot([0, 1], [0, 1], 'k--', label='Random')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curves Comparison')
        plt.legend()
        plt.grid(True)
        plt.savefig(plots_dir / 'roc_curves.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Precision-Recall curves
        plt.figure(figsize=(10, 8))
        for name, evaluation in evaluations.items():
            precision, recall, _ = evaluation.pr_curve_data
            plt.plot(recall, precision, label=f'{name} (AP = {evaluation.average_precision:.3f})')
        
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision-Recall Curves Comparison')
        plt.legend()
        plt.grid(True)
        plt.savefig(plots_dir / 'pr_curves.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Cross-validation scores
        fig, ax = plt.subplots(figsize=(12, 6))
        
        cv_data = []
        labels = []
        for name, evaluation in evaluations.items():
            cv_data.append(evaluation.cross_val_scores)
            labels.append(name)
        
        box_plot = ax.boxplot(cv_data, labels=labels, patch_artist=True)
        ax.set_title('Cross-Validation Scores Distribution')
        ax.set_ylabel('ROC-AUC Score')
        ax.tick_params(axis='x', rotation=45)
        
        # Color the boxes
        colors = plt.cm.Set3(np.linspace(0, 1, len(box_plot['boxes'])))
        for box, color in zip(box_plot['boxes'], colors):
            box.set_facecolor(color)
        
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(plots_dir / 'cv_scores.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_html_report(self, run_id: str, evaluations: Dict[str, ModelEvaluation]) -> str:
        """Create HTML training report"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI Detector Training Report - {run_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .metrics-table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                .metrics-table th, .metrics-table td {{ 
                    border: 1px solid #ddd; padding: 8px; text-align: center; 
                }}
                .metrics-table th {{ background-color: #4CAF50; color: white; }}
                .best-model {{ background-color: #e8f5e8; }}
                .plot {{ text-align: center; margin: 20px 0; }}
                .plot img {{ max-width: 100%; height: auto; }}
                .section {{ margin: 30px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>AI Generated Content Detector - Training Report</h1>
                <p><strong>Run ID:</strong> {run_id}</p>
                <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Best Model:</strong> {self.best_model}</p>
            </div>
            
            <div class="section">
                <h2>Model Performance Summary</h2>
                <table class="metrics-table">
                    <tr>
                        <th>Model</th>
                        <th>Accuracy</th>
                        <th>Precision</th>
                        <th>Recall</th>
                        <th>F1-Score</th>
                        <th>ROC-AUC</th>
                        <th>Training Time (s)</th>
                    </tr>
        """
        
        # Add model rows
        for name, evaluation in evaluations.items():
            row_class = "best-model" if name == self.best_model else ""
            html += f"""
                    <tr class="{row_class}">
                        <td><strong>{name}</strong></td>
                        <td>{evaluation.accuracy:.4f}</td>
                        <td>{evaluation.precision:.4f}</td>
                        <td>{evaluation.recall:.4f}</td>
                        <td>{evaluation.f1_score:.4f}</td>
                        <td>{evaluation.roc_auc:.4f}</td>
                        <td>{evaluation.training_time:.2f}</td>
                    </tr>
            """
        
        html += """
                </table>
            </div>
            
            <div class="section">
                <h2>Performance Visualizations</h2>
                
                <div class="plot">
                    <h3>Model Metrics Comparison</h3>
                    <img src="../plots/{}/model_comparison.png" alt="Model Comparison">
                </div>
                
                <div class="plot">
                    <h3>ROC Curves</h3>
                    <img src="../plots/{}/roc_curves.png" alt="ROC Curves">
                </div>
                
                <div class="plot">
                    <h3>Precision-Recall Curves</h3>
                    <img src="../plots/{}/pr_curves.png" alt="PR Curves">
                </div>
                
                <div class="plot">
                    <h3>Cross-Validation Scores</h3>
                    <img src="../plots/{}/cv_scores.png" alt="CV Scores">
                </div>
            </div>
            
        </body>
        </html>
        """.format(run_id, run_id, run_id, run_id)
        
        return html
    
    def deploy_best_model(self, environment: str = 'production') -> str:
        """Deploy the best performing model"""
        if not self.best_model:
            raise ValueError("No trained models available for deployment")
        
        deployment_id = f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Copy best model to deployment directory
        deploy_dir = self.output_dir / "deployed_models" / deployment_id
        deploy_dir.mkdir(parents=True, exist_ok=True)
        
        best_model_data = self.models[self.best_model]
        
        # Copy model files
        if best_model_data['model_path'].endswith('.pkl'):
            shutil.copy2(best_model_data['model_path'], deploy_dir / 'model.pkl')
        else:
            shutil.copytree(best_model_data['model_path'], deploy_dir / 'model')
        
        # Copy evaluation
        shutil.copy2(best_model_data['eval_path'], deploy_dir / 'evaluation.json')
        
        # Create deployment metadata
        deployment_metadata = {
            'deployment_id': deployment_id,
            'model_name': self.best_model,
            'deployment_time': datetime.now().isoformat(),
            'environment': environment,
            'performance': {
                'accuracy': best_model_data['evaluation'].accuracy,
                'roc_auc': best_model_data['evaluation'].roc_auc,
                'f1_score': best_model_data['evaluation'].f1_score
            },
            'model_path': str(deploy_dir),
            'version': '1.0.0'
        }
        
        with open(deploy_dir / 'deployment_metadata.json', 'w') as f:
            json.dump(deployment_metadata, f, indent=2)
        
        # Record deployment in database
        db_path = self.output_dir / "model_tracking.db"
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                INSERT INTO deployment_history VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                deployment_id,
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.best_model}",
                datetime.now().isoformat(),
                environment,
                '1.0.0',
                best_model_data['evaluation'].roc_auc,
                'active'
            ))
        
        logger.info(f"Model deployed successfully: {deployment_id}")
        logger.info(f"Deployment path: {deploy_dir}")
        
        return deployment_id

# Export main classes
__all__ = ['ProductionAIDetectorTrainer', 'TrainingConfig', 'ModelEvaluation']

if __name__ == "__main__":
    print("Production AI Detector Training System")
    print("Complete system for training and deploying AI detection models")
    print("\nExample usage:")
    print("config = TrainingConfig(models_to_train=['random_forest', 'xgboost', 'neural_network'])")
    print("trainer = ProductionAIDetectorTrainer(config)")
    print("evaluations = trainer.train_all_models(X, y)")
    print("deployment_id = trainer.deploy_best_model('production')")