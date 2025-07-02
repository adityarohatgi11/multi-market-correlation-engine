#!/usr/bin/env python3
"""
Direct LLM Model Test
Test the downloaded Llama model without complex dependencies
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_llama_model():
    """Test the Llama model directly."""
    print("🤖 Testing Llama Model Direct Load...")
    
    # Check if model file exists
    model_path = "data/models/llama-2-7b-chat.Q4_0.gguf"
    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        return False
    
    print(f"✅ Model file found: {model_path}")
    print(f"📁 Model size: {os.path.getsize(model_path) / (1024**3):.1f} GB")
    
    try:
        from llama_cpp import Llama
        print("✅ llama-cpp-python is available")
        
        print("🔄 Loading Llama model (this may take a minute)...")
        model = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=4,
            verbose=False
        )
        
        print("✅ Model loaded successfully!")
        
        # Test a simple query
        print("💬 Testing chat functionality...")
        prompt = "What are the key principles of portfolio diversification? Be concise."
        
        response = model(
            prompt,
            max_tokens=150,
            temperature=0.7,
            stop=["###", "\n\n\n"],
            echo=False
        )
        
        print("🎯 AI Response:")
        print("-" * 50)
        print(response['choices'][0]['text'].strip())
        print("-" * 50)
        
        return True
        
    except ImportError:
        print("❌ llama-cpp-python not available")
        return False
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False

if __name__ == "__main__":
    success = test_llama_model()
    if success:
        print("\n🎉 LLM model test successful!")
        print("💡 The model is ready for integration with your application!")
    else:
        print("\n❌ LLM model test failed")
        print("🔧 Please check the error messages above") 