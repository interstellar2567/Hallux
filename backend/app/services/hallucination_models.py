"""
Advanced Hallucination Detection Models
Integrates multiple detection strategies
"""

from typing import List, Dict, Any, Optional
from loguru import logger
import re
from difflib import SequenceMatcher


class HallucinationDetector:
    """
    Multi-model hallucination detection system
    Inspired by Citation-Hallucination-Detection and exa-labs approaches
    """
    
    def __init__(self):
        self.patterns = self._load_hallucination_patterns()
        
    def _load_hallucination_patterns(self) -> List[Dict[str, Any]]:
        """Common hallucination patterns in citations"""
        return [
            {
                "name": "impossible_year",
                "pattern": r'\b(20[3-9]\d|2[1-9]\d{2})\b',  # Years > 2029
                "severity": "high",
                "description": "Citation references future year"
            },
            {
                "name": "fake_doi_structure",
                "pattern": r'10\.(?![\d]{4})',  # Malformed DOI
                "severity": "medium",
                "description": "DOI doesn't follow standard format"
            },
            {
                "name": "nonexistent_journal",
                "pattern": r'\b(Nature|Science|Cell|Lancet)\s+\d{4}\b',
                "severity": "low",
                "description": "High-impact journal without proper citation"
            },
            {
                "name": "fake_arxiv",
                "pattern": r'arXiv:(?!\d{4}\.\d{4,5})',
                "severity": "high",
                "description": "Invalid arXiv format"
            },
            {
                "name": "suspicious_url",
                "pattern": r'https?://(?:example\.com|test\.org|fake)',
                "severity": "high",
                "description": "Placeholder or test URL detected"
            }
        ]
    
    def detect_hallucinations(
        self,
        citation: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detect potential hallucinations in citation
        
        Returns:
            Detection results with confidence and flags
        """
        logger.info(f"Running hallucination detection on: {citation[:100]}")
        
        flags = []
        severity_score = 0
        
        # Pattern-based detection
        for pattern_def in self.patterns:
            matches = re.finditer(pattern_def["pattern"], citation, re.IGNORECASE)
            for match in matches:
                flags.append({
                    "type": pattern_def["name"],
                    "matched": match.group(0),
                    "severity": pattern_def["severity"],
                    "description": pattern_def["description"]
                })
                
                # Add to severity score
                if pattern_def["severity"] == "high":
                    severity_score += 0.3
                elif pattern_def["severity"] == "medium":
                    severity_score += 0.15
                else:
                    severity_score += 0.05
        
        # Structure analysis
        structure_flags = self._analyze_structure(citation)
        flags.extend(structure_flags)
        severity_score += len(structure_flags) * 0.1
        
        # Claim extraction and verification
        if context:
            claim_flags = self._verify_claims(citation, context)
            flags.extend(claim_flags)
            severity_score += len(claim_flags) * 0.2
        
        # Calculate hallucination probability
        hallucination_probability = min(severity_score, 1.0)
        credibility_score = 1.0 - hallucination_probability
        
        return {
            "is_likely_hallucinated": hallucination_probability > 0.5,
            "hallucination_probability": hallucination_probability,
            "credibility_score": credibility_score,
            "flags": flags,
            "total_flags": len(flags),
            "recommendation": self._generate_recommendation(hallucination_probability, flags)
        }
    
    def _analyze_structure(self, citation: str) -> List[Dict[str, Any]]:
        """Analyze citation structure for anomalies"""
        flags = []
        
        # Check for proper citation format
        has_author = bool(re.search(r'\b[A-Z][a-z]+\s+(?:et\s+al\.?|and\s+[A-Z])', citation))
        has_year = bool(re.search(r'\b(19|20)\d{2}\b', citation))
        has_source = bool(re.search(r'https?://|doi:|arXiv:', citation, re.IGNORECASE))
        
        if not has_author:
            flags.append({
                "type": "missing_author",
                "severity": "medium",
                "description": "No clear author pattern found"
            })
        
        if not has_year:
            flags.append({
                "type": "missing_year",
                "severity": "medium",
                "description": "No publication year found"
            })
        
        if not has_source:
            flags.append({
                "type": "missing_source",
                "severity": "high",
                "description": "No verifiable source (URL/DOI/arXiv) found"
            })
        
        # Check for overly confident language (hallucination indicator)
        confident_phrases = [
            r'\bevery\b', r'\ball\b', r'\balways\b', r'\bnever\b',
            r'\bclearly\b', r'\bobviously\b', r'\bundoubtedly\b'
        ]
        
        for phrase_pattern in confident_phrases:
            if re.search(phrase_pattern, citation, re.IGNORECASE):
                flags.append({
                    "type": "overconfident_language",
                    "severity": "low",
                    "description": "Contains overly confident language (common in hallucinations)"
                })
                break
        
        return flags
    
    def _verify_claims(
        self,
        citation: str,
        context: str
    ) -> List[Dict[str, Any]]:
        """Verify claims in citation match context"""
        flags = []
        
        # Extract quoted text
        quoted_text = re.findall(r'"([^"]+)"', citation)
        
        for quote in quoted_text:
            # Check if quote appears in context
            similarity = self._calculate_similarity(quote.lower(), context.lower())
            
            if similarity < 0.3:
                flags.append({
                    "type": "unverified_quote",
                    "severity": "high",
                    "description": f"Quote not found in context: '{quote[:50]}...'"
                })
        
        return flags
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using sequence matching"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _generate_recommendation(
        self,
        probability: float,
        flags: List[Dict]
    ) -> str:
        """Generate human-readable recommendation"""
        
        if probability >= 0.8:
            return f"⚠️ LIKELY HALLUCINATED - Found {len(flags)} red flags. Do not trust this citation."
        elif probability >= 0.5:
            return f"⚠️ SUSPICIOUS - {len(flags)} issues detected. Verify manually before use."
        elif probability >= 0.3:
            return f"⚡ CAUTION - {len(flags)} minor issues. Cross-check recommended."
        else:
            return "✅ APPEARS CREDIBLE - No major hallucination indicators detected."
    
    def batch_detect(
        self,
        citations: List[str],
        contexts: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Detect hallucinations in multiple citations"""
        
        results = []
        for i, citation in enumerate(citations):
            context = contexts[i] if contexts and i < len(contexts) else None
            result = self.detect_hallucinations(citation, context)
            results.append(result)
        
        return results


class ClaimExtractor:
    """
    Extract and verify factual claims from text
    Inspired by exa-labs approach
    """
    
    def extract_claims(self, text: str) -> List[Dict[str, str]]:
        """Break down text into individual verifiable claims"""
        
        logger.info("Extracting claims from text...")
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        claims = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 10:
                continue
            
            # Identify factual claims (contain citations, data, or assertions)
            if self._is_factual_claim(sentence):
                claims.append({
                    "text": sentence,
                    "type": self._classify_claim(sentence),
                    "needs_verification": True
                })
        
        return claims
    
    def _is_factual_claim(self, sentence: str) -> bool:
        """Check if sentence contains factual claim"""
        
        # Contains citation reference
        if re.search(r'\([\d]{4}\)|\[\d+\]|et\s+al\.', sentence):
            return True
        
        # Contains statistical data
        if re.search(r'\d+%|\d+\s+(?:percent|cases|studies)', sentence):
            return True
        
        # Contains definitive statement
        definitive_verbs = ['is', 'are', 'was', 'demonstrates', 'shows', 'proves']
        if any(verb in sentence.lower() for verb in definitive_verbs):
            return True
        
        return False
    
    def _classify_claim(self, sentence: str) -> str:
        """Classify type of claim"""
        
        if re.search(r'\d+%|\d+\s+percent', sentence):
            return "statistical"
        elif re.search(r'according to|cited in|\([\d]{4}\)', sentence):
            return "cited"
        elif re.search(r'study|research|paper|article', sentence, re.IGNORECASE):
            return "research"
        else:
            return "general"


# Global instances
hallucination_detector = HallucinationDetector()
claim_extractor = ClaimExtractor()
