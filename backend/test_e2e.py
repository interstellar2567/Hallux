"""
End-to-End Testing for All 5 Verification Layers
Tests the complete pipeline with real-world examples
"""

import asyncio
import httpx
from loguru import logger

# Backend API URL
API_URL = "http://localhost:8000"

async def test_verification_pipeline():
    """Test complete 5-layer verification system"""
    
    logger.info("=" * 80)
    logger.info("END-TO-END TESTING: Complete 5-Layer Verification Pipeline")
    logger.info("=" * 80)
    
    test_cases = [
        {
            "name": "✅ Valid Citation (Should PASS)",
            "citation": "Brown et al. (2020), 'Language Models are Few-Shot Learners', arXiv:2005.14165",
            "context": "This paper presents GPT-3, a large language model with 175 billion parameters that demonstrates few-shot learning capabilities without gradient updates.",
            "expected": "PASSED"
        },
        {
            "name": "❌ Fake DOI (Should FAIL Layer 2)",
            "citation": "Smith (2023), 'Quantum AI Revolution', DOI: 10.9999/fake.citation.12345",
            "context": "This paper proposes a quantum computing approach to artificial general intelligence using novel algorithms.",
            "expected": "FAILED"
        },
        {
            "name": "⚠️ Time Travel Citation (Should WARN Layer 4)",
            "citation": "Johnson (2030), 'Future of AI', DOI: 10.1234/future.2030",
            "context": "In this groundbreaking 2030 paper, Johnson predicts the AI singularity will occur by 2035.",
            "expected": "WARNING"
        },
        {
            "name": "⚠️ Partial Hallucination (Should WARN Layer 2)",
            "citation": "Einstein (2023), 'General Relativity', DOI: 10.1002/andp.19163540702",
            "context": "Einstein's famous 2023 paper on general relativity revolutionized physics.",
            "expected": "WARNING"
        },
        {
            "name": "✅ Real Nature Paper (Should PASS)",
            "citation": "Jumper et al. (2021), 'Highly accurate protein structure prediction with AlphaFold', Nature, DOI: 10.1038/s41586-021-03819-2",
            "context": "This paper describes AlphaFold2, which achieved unprecedented accuracy in protein structure prediction at CASP14.",
            "expected": "PASSED"
        }
    ]
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for i, test in enumerate(test_cases, 1):
            logger.info(f"\n{'=' * 80}")
            logger.info(f"TEST {i}/{len(test_cases)}: {test['name']}")
            logger.info(f"{'=' * 80}")
            
            try:
                # Call verification API
                response = await client.post(
                    f"{API_URL}/api/verify",
                    json={
                        "citation": test["citation"],
                        "context": test["context"]
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display results
                    logger.info(f"\n📋 Citation: {test['citation']}")
                    logger.info(f"🎯 Context: {test['context'][:100]}...")
                    logger.info(f"\n📊 RESULTS:")
                    logger.info(f"   Overall Status: {result.get('overall_status', 'N/A')}")
                    logger.info(f"   Confidence: {result.get('confidence_score', 0) * 100:.1f}%")
                    logger.info(f"   Expected: {test['expected']}")
                    
                    # Layer-by-layer breakdown
                    logger.info(f"\n🔍 Layer-by-Layer:")
                    layers = result.get('layers', {})
                    for layer_name, layer_data in layers.items():
                        status_emoji = {
                            'passed': '✅',
                            'warning': '⚠️',
                            'failed': '❌',
                            'skipped': '⏭️'
                        }.get(layer_data.get('status', 'unknown'), '❓')
                        
                        logger.info(f"   {status_emoji} {layer_name}: {layer_data.get('status', 'N/A').upper()}")
                        logger.info(f"      Details: {layer_data.get('details', 'No details')[:80]}")
                        
                        # Show metadata for interesting findings
                        if layer_data.get('metadata'):
                            metadata = layer_data['metadata']
                            if 'partial_hallucination' in metadata:
                                logger.warning(f"      🚨 PARTIAL HALLUCINATION DETECTED!")
                            if 'temporal_flags' in metadata and metadata['temporal_flags']:
                                logger.warning(f"      ⏰ Temporal Issues: {', '.join(metadata['temporal_flags'])}")
                            if 'similarity_score' in metadata:
                                logger.info(f"      📈 Similarity: {metadata['similarity_score']:.2f}")
                            if 'cited_by_count' in metadata:
                                logger.info(f"      📚 Citations: {metadata['cited_by_count']}")
                    
                    # Flags and warnings
                    if result.get('flags'):
                        logger.warning(f"\n🚩 FLAGS: {', '.join(result['flags'])}")
                    
                    # Verdict
                    actual = result.get('overall_status', '').upper()
                    expected = test['expected'].upper()
                    
                    if actual == expected:
                        logger.success(f"\n✅ TEST PASSED: Expected {expected}, got {actual}")
                    else:
                        logger.warning(f"\n⚠️ TEST RESULT: Expected {expected}, got {actual}")
                
                else:
                    logger.error(f"API Error: {response.status_code}")
                    logger.error(f"Response: {response.text}")
            
            except Exception as e:
                logger.error(f"❌ Test failed with exception: {e}")
            
            # Wait between tests
            if i < len(test_cases):
                logger.info(f"\n⏳ Waiting 2 seconds before next test...")
                await asyncio.sleep(2)
    
    logger.info(f"\n{'=' * 80}")
    logger.info("🎉 END-TO-END TESTING COMPLETE")
    logger.info(f"{'=' * 80}")

if __name__ == "__main__":
    # Make sure backend is running on http://localhost:8000
    logger.info("🚀 Starting end-to-end tests...")
    logger.info("⚠️ Make sure backend is running: uvicorn app.main:app --reload")
    asyncio.run(test_verification_pipeline())
