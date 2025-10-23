"""
🎯 Complete Production AI Detector Training Example
Step-by-step guide for training production-ready AI detection models
Part of the TCU-CEAA AI Document Verification System
"""

import os
import sys
import numpy as np
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from ai_detector_trainer import AIDetectorTrainer, FeatureExtractor, DatasetSample
from dataset_manager import DatasetManager, DatasetMetadata
from production_trainer import ProductionAIDetectorTrainer, TrainingConfig, ModelEvaluation

def main():
    """Complete production training pipeline example"""
    print("="*80)
    print("🚀 PRODUCTION AI DETECTOR TRAINING PIPELINE")
    print("="*80)
    
    # Step 1: Initialize Dataset Manager
    print("\n📊 Step 1: Initialize Dataset Manager")
    print("-" * 40)
    
    dataset_manager = DatasetManager("production_training_data")
    print(f"✅ Dataset manager initialized")
    print(f"   Dataset root: {dataset_manager.dataset_root}")
    
    # Step 2: Generate Training Data
    print("\n🏭 Step 2: Generate Training Data")
    print("-" * 40)
    
    # Generate synthetic samples for demonstration
    print("Generating synthetic training samples...")
    generated_count = dataset_manager.generate_synthetic_samples(
        count=500,  # Generate 500 samples
        sample_types=['natural_images', 'ai_like_images', 'mixed_documents']
    )
    print(f"✅ Generated {generated_count} synthetic samples")
    
    # Apply data augmentation
    print("Applying data augmentation...")
    augmented_count = dataset_manager.augment_dataset(augmentation_factor=1)
    print(f"✅ Created {augmented_count} augmented samples")
    
    # Get dataset statistics
    stats = dataset_manager.get_dataset_statistics()
    print(f"\n📈 Dataset Statistics:")
    print(f"   Total samples: {stats['total_samples']}")
    print(f"   Real samples: {stats['real_samples']}")
    print(f"   AI samples: {stats['ai_samples']}")
    print(f"   By content type: {stats['by_content_type']}")
    
    # Step 3: Prepare Training Data
    print("\n🔧 Step 3: Prepare Training Data")
    print("-" * 40)
    
    # Get all samples
    all_samples = dataset_manager.get_all_samples()
    
    if len(all_samples) == 0:
        print("❌ No samples found. Please add training data first.")
        return
    
    # Initialize feature extractor
    feature_extractor = FeatureExtractor()
    print(f"✅ Feature extractor initialized")
    print(f"   Feature dimensions: {len(feature_extractor.feature_names)}")
    
    # Extract features from samples
    print("Extracting features from samples...")
    
    X_list = []
    y_list = []
    
    for i, sample in enumerate(all_samples):
        if i % 50 == 0:
            print(f"   Processing sample {i+1}/{len(all_samples)}")
        
        try:
            if sample['content_type'] == 'image':
                features = feature_extractor.extract_image_features(sample['file_path'])
                X_list.append(features)
                y_list.append(1 if sample['is_ai_generated'] else 0)
        except Exception as e:
            print(f"   ⚠️ Failed to process {sample['file_id']}: {e}")
    
    if len(X_list) == 0:
        print("❌ No features extracted. Check your data.")
        return
    
    X = np.array(X_list)
    y = np.array(y_list)
    
    print(f"✅ Feature extraction completed")
    print(f"   Features shape: {X.shape}")
    print(f"   Labels shape: {y.shape}")
    print(f"   Real samples: {np.sum(y == 0)}")
    print(f"   AI samples: {np.sum(y == 1)}")
    
    # Step 4: Configure Training
    print("\n⚙️ Step 4: Configure Training Pipeline")
    print("-" * 40)
    
    config = TrainingConfig(
        models_to_train=[
            'random_forest',
            'logistic_regression', 
            'svm'
        ],
        hyperparameter_tuning=True,
        cross_validation_folds=3,  # Reduced for faster training
        test_size=0.2,
        validation_size=0.15,
        scoring_metric='roc_auc',
        ensemble_methods=['voting', 'bagging']
    )
    
    # Add XGBoost and Neural Network if available
    try:
        import xgboost
        config.models_to_train.append('xgboost')
        print("✅ XGBoost available - added to training")
    except ImportError:
        print("ℹ️ XGBoost not available")
    
    try:
        import tensorflow
        config.models_to_train.append('neural_network')
        print("✅ TensorFlow available - added to training")
    except ImportError:
        print("ℹ️ TensorFlow not available")
    
    print(f"\n🎯 Training Configuration:")
    print(f"   Models: {config.models_to_train}")
    print(f"   Hyperparameter tuning: {config.hyperparameter_tuning}")
    print(f"   Cross-validation folds: {config.cross_validation_folds}")
    print(f"   Ensemble methods: {config.ensemble_methods}")
    
    # Step 5: Train Models
    print("\n🤖 Step 5: Train Production Models")
    print("-" * 40)
    
    trainer = ProductionAIDetectorTrainer(config, "production_ai_models")
    
    print("Starting comprehensive model training...")
    print("This may take several minutes depending on dataset size and models...")
    
    try:
        evaluations = trainer.train_all_models(X, y)
        
        print(f"\n🎉 Training Completed Successfully!")
        print(f"   Models trained: {len(evaluations)}")
        print(f"   Best model: {trainer.best_model}")
        
        # Display results
        print(f"\n📊 Model Performance Summary:")
        print("-" * 60)
        print(f"{'Model':<20} {'Accuracy':<10} {'Precision':<10} {'Recall':<10} {'ROC-AUC':<10}")
        print("-" * 60)
        
        for name, evaluation in evaluations.items():
            print(f"{name:<20} {evaluation.accuracy:<10.4f} {evaluation.precision:<10.4f} "
                  f"{evaluation.recall:<10.4f} {evaluation.roc_auc:<10.4f}")
        
        print("-" * 60)
        
        # Best model details
        best_eval = evaluations[trainer.best_model]
        print(f"\n🏆 Best Model: {trainer.best_model}")
        print(f"   ROC-AUC: {best_eval.roc_auc:.4f}")
        print(f"   Accuracy: {best_eval.accuracy:.4f}")
        print(f"   F1-Score: {best_eval.f1_score:.4f}")
        print(f"   Training Time: {best_eval.training_time:.2f} seconds")
        
        # Feature importance
        if best_eval.feature_importance:
            print(f"\n🔍 Top 10 Most Important Features:")
            sorted_features = sorted(
                best_eval.feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            for i, (feature, importance) in enumerate(sorted_features, 1):
                print(f"   {i:2d}. {feature:<25} {importance:.4f}")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return
    
    # Step 6: Deploy Best Model
    print("\n🚀 Step 6: Deploy Production Model")
    print("-" * 40)
    
    try:
        deployment_id = trainer.deploy_best_model('production')
        print(f"✅ Model deployed successfully!")
        print(f"   Deployment ID: {deployment_id}")
        print(f"   Model: {trainer.best_model}")
        print(f"   Performance: {best_eval.roc_auc:.4f} ROC-AUC")
        
        # Deployment path
        deploy_path = trainer.output_dir / "deployed_models" / deployment_id
        print(f"   Deployment path: {deploy_path}")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
    
    # Step 7: Integration Instructions
    print("\n📋 Step 7: Integration Instructions")
    print("-" * 40)
    
    print("""
🔗 INTEGRATING THE TRAINED MODEL:

1. Update the AIGeneratedDetector class:
   - Replace the dummy ML classifier with your trained model
   - Load the best model from: production_ai_models/deployed_models/{deployment_id}/
   
2. Update advanced_algorithms.py:
   ```python
   # Load production model
   import pickle
   with open('production_ai_models/deployed_models/{deployment_id}/model.pkl', 'rb') as f:
       production_model = pickle.load(f)
   
   # Replace in AIGeneratedDetector.__init__()
   self.ml_classifier = production_model['model']
   self.scaler = production_model['scaler']
   ```

3. Performance Monitoring:
   - Set up monitoring for model performance drift
   - Implement A/B testing for model updates
   - Schedule periodic retraining with new data

4. Continuous Learning:
   - Collect new samples during production use
   - Label samples based on user feedback
   - Retrain models monthly/quarterly

5. Model Versioning:
   - Use the deployment_id for version tracking
   - Maintain model performance history
   - Enable rollback to previous versions if needed
    """.format(deployment_id=deployment_id if 'deployment_id' in locals() else 'DEPLOYMENT_ID'))
    
    print("\n" + "="*80)
    print("🎉 PRODUCTION AI DETECTOR TRAINING COMPLETE!")
    print("="*80)
    print(f"""
Summary:
- ✅ Dataset collected and organized: {stats['total_samples']} samples
- ✅ Features extracted: {X.shape[1]} features per sample  
- ✅ Models trained: {len(evaluations)} models
- ✅ Best model selected: {trainer.best_model}
- ✅ Model deployed: Ready for production use

Next Steps:
1. Integrate the trained model into your AI detection system
2. Set up production monitoring and logging
3. Implement user feedback collection for continuous learning
4. Schedule periodic model retraining

Your AI detection system is now production-ready! 🚀
    """)

def quick_training_example():
    """Quick training example with minimal dataset"""
    print("🚀 Quick AI Detector Training Example")
    print("=" * 50)
    
    try:
        # Initialize components
        dataset_manager = DatasetManager("quick_training_data")
        
        # Generate small dataset
        print("Generating quick training dataset...")
        generated = dataset_manager.generate_synthetic_samples(50)
        
        if generated < 10:
            print("❌ Not enough samples generated")
            return
        
        # Get samples and extract features  
        samples = dataset_manager.get_all_samples()
        feature_extractor = FeatureExtractor()
        
        X_list = []
        y_list = []
        
        for sample in samples:
            if sample['content_type'] == 'image':
                try:
                    features = feature_extractor.extract_image_features(sample['file_path'])
                    X_list.append(features)
                    y_list.append(1 if sample['is_ai_generated'] else 0)
                except:
                    continue
        
        if len(X_list) < 10:
            print("❌ Not enough features extracted")
            return
        
        X = np.array(X_list)
        y = np.array(y_list)
        
        print(f"Dataset ready: {X.shape[0]} samples, {X.shape[1]} features")
        
        # Quick training config
        config = TrainingConfig(
            models_to_train=['random_forest', 'logistic_regression'],
            hyperparameter_tuning=False,  # Skip for speed
            cross_validation_folds=3,
            ensemble_methods=[]
        )
        
        # Train
        trainer = ProductionAIDetectorTrainer(config, "quick_models")
        evaluations = trainer.train_all_models(X, y)
        
        # Results
        print("\n🎉 Quick Training Results:")
        for name, eval in evaluations.items():
            print(f"  {name}: {eval.roc_auc:.4f} ROC-AUC")
        
        print(f"\nBest model: {trainer.best_model}")
        
    except Exception as e:
        print(f"❌ Quick training failed: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Detector Production Training")
    parser.add_argument('--mode', choices=['full', 'quick'], default='full',
                       help='Training mode: full or quick')
    
    args = parser.parse_args()
    
    if args.mode == 'quick':
        quick_training_example()
    else:
        main()