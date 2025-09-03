# Quick usage script for dog aggression detection
import os
from dog_aggression_detector import DogAggressionDetector  # Import the main class

def main():
    # Your YOLO model path
    yolo_model_path = r"/Users/aditya/Documents/AIBSS/dog-behavior-dashboard/models/best.pt"
    
    print("🐕 Dog Aggression Detection System")
    print("=" * 40)
    
    # Initialize detector
    detector = DogAggressionDetector(yolo_model_path)
    
    # Step 1: Prepare your training data
    print("\n📋 STEP 1: Prepare Training Data")
    print("Create folders like this:")
    print("training_data/")
    print("├── aggressive/        # Put aggressive dog images here")
    print("└── non_aggressive/    # Put calm dog images here")
    
    training_data_path = input("\nEnter path to your training_data folder (or press Enter to skip): ").strip()
    
    if training_data_path and os.path.exists(training_data_path):
        print("\n🔄 Training model...")
        
        # Prepare training data
        X, y = detector.prepare_training_data(training_data_path)
        
        if len(X) > 0:
            # Train model
            accuracy = detector.train_model(X, y)
            
            # Save model
            detector.save_model("dog_aggression_model.pkl")
            print(f"✅ Model trained and saved! Accuracy: {accuracy:.3f}")
        else:
            print("❌ No training data found!")
            return
    else:
        print("⏭️ Skipping training - will try to load existing model")
        
        # Try to load existing model
        model_file = "dog_aggression_model.pkl"
        if os.path.exists(model_file):
            detector.load_model(model_file)
            print("✅ Existing model loaded!")
        else:
            print("❌ No trained model found. Please train first.")
            return
    
    # Step 2: Test on images
    print("\n🔮 STEP 2: Test Dog Aggression Detection")
    
    while True:
        test_image_path = input("\nEnter path to test image (or 'quit' to exit): ").strip()
        
        if test_image_path.lower() == 'quit':
            break
            
        if os.path.exists(test_image_path):
            print(f"\n🔍 Analyzing: {test_image_path}")
            
            result, confidence = detector.predict_aggression(test_image_path)
            
            # Display result with emoji
            emoji = "🔥" if "Aggressive" in result else "😊"
            print(f"{emoji} Result: {result}")
            print(f"📊 Confidence: {confidence:.3f}")
            
            if confidence < 0.6:
                print("⚠️  Low confidence - consider retaking photo or checking image quality")
                
        else:
            print("❌ Image file not found!")

if __name__ == "__main__":
    main()