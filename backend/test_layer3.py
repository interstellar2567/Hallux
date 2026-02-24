"""
Quick test for Layer 3 (Content Verification) with real web scraping
"""

import asyncio
from app.services.advanced_verification import advanced_verifier

async def test_layer3():
    """Test web scraping + semantic similarity"""
    
    print("=" * 80)
    print("TESTING LAYER 3: Content Verification with Playwright")
    print("=" * 80)
    
    # Test Case 1: Real research paper URL
    print("\n✅ Test 1: Real arXiv paper")
    print("-" * 80)
    url1 = "https://arxiv.org/abs/2005.14165"
    context1 = """
    This paper presents GPT-3, a large language model with 175 billion parameters.
    We show that GPT-3 can perform few-shot learning without gradient updates.
    The model demonstrates strong performance on many NLP benchmarks.
    """
    
    result1 = await advanced_verifier.scrape_and_compare_content(url1, context1)
    print(f"URL: {url1}")
    print(f"Aligned: {result1['aligned']}")
    print(f"Confidence: {result1['confidence']:.2f}")
    print(f"Similarity Score: {result1['similarity_score']:.3f}")
    print(f"Content Length: {result1['content_length']} chars")
    print(f"Reason: {result1['reason']}")
    print(f"Flags: {result1['flags']}")
    
    # Test Case 2: Mismatched content
    print("\n\n❌ Test 2: Mismatched content")
    print("-" * 80)
    url2 = "https://arxiv.org/abs/2005.14165"
    context2 = """
    This paper discusses quantum computing algorithms for protein folding.
    We use superconducting qubits to simulate molecular dynamics.
    Results show 100x speedup over classical methods.
    """
    
    result2 = await advanced_verifier.scrape_and_compare_content(url2, context2)
    print(f"URL: {url2}")
    print(f"Aligned: {result2['aligned']}")
    print(f"Confidence: {result2['confidence']:.2f}")
    print(f"Similarity Score: {result2['similarity_score']:.3f}")
    print(f"Content Length: {result2['content_length']} chars")
    print(f"Reason: {result2['reason']}")
    print(f"Flags: {result2['flags']}")
    
    # Test Case 3: Nature article (paywall test)
    print("\n\n🔒 Test 3: Paywalled article (Nature)")
    print("-" * 80)
    url3 = "https://www.nature.com/articles/s41586-020-03051-4"
    context3 = """
    AlphaFold2 achieves unprecedented accuracy in protein structure prediction.
    The model uses attention mechanisms to predict 3D structures from sequences.
    This represents a major breakthrough in computational biology.
    """
    
    result3 = await advanced_verifier.scrape_and_compare_content(url3, context3)
    print(f"URL: {url3}")
    print(f"Aligned: {result3['aligned']}")
    print(f"Confidence: {result3['confidence']:.2f}")
    print(f"Similarity Score: {result3['similarity_score']:.3f}")
    print(f"Content Length: {result3['content_length']} chars")
    print(f"Reason: {result3['reason']}")
    print(f"Flags: {result3['flags']}")
    
    print("\n" + "=" * 80)
    print("LAYER 3 TESTING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_layer3())
