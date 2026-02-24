"""
Quick API test to verify verification endpoint works
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_verification():
    """Test single verification"""
    
    print("=" * 80)
    print("TESTING VERIFICATION API")
    print("=" * 80)
    
    # Test case: Valid arXiv paper
    payload = {
        "citation": "Brown et al. (2020), 'Language Models are Few-Shot Learners', arXiv:2005.14165",
        "context": "This paper presents GPT-3, a large language model with 175 billion parameters."
    }
    
    print(f"\n📋 Citation: {payload['citation']}")
    print(f"🎯 Context: {payload['context']}")
    print(f"\n⏳ Sending request...")
    
    try:
        response = requests.post(
            f"{API_URL}/api/verify-citation",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ SUCCESS! Status Code: {response.status_code}")
            print(f"\n📊 RESULTS:")
            print(f"   Overall Status: {result.get('overall_status', 'N/A')}")
            print(f"   Confidence: {result.get('confidence_score', 0) * 100:.1f}%")
            
            print(f"\n🔍 Layer Results:")
            for layer_name, layer_data in result.get('layers', {}).items():
                status = layer_data.get('status', 'N/A')
                emoji = {'passed': '✅', 'warning': '⚠️', 'failed': '❌', 'skipped': '⏭️'}.get(status, '❓')
                print(f"   {emoji} {layer_name}: {status.upper()}")
            
            if result.get('flags'):
                print(f"\n🚩 Flags: {', '.join(result['flags'])}")
            
            # Save result for frontend testing
            with open('test_result.json', 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Result saved to test_result.json")
            
        else:
            print(f"\n❌ ERROR: Status {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"\n❌ Exception: {e}")

if __name__ == "__main__":
    test_verification()
