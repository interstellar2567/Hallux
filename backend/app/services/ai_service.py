"""
AI Service for Citation Verification
Integrates OpenAI GPT-4 and Google Gemini
"""

from typing import Optional, Dict, Any
from loguru import logger
import os

from app.core.config import Settings
from app.models.schemas import LayerResult, LayerStatus

# Initialize settings
settings = Settings()


class AIService:
    """AI-powered citation analysis service"""
    
    def __init__(self):
        self.openai_key = settings.OPENAI_API_KEY
        self.google_key = settings.GOOGLE_API_KEY or settings.GEMINI_API_KEY
        self.openai_client = None
        self.gemini_model = None
        
        # Initialize OpenAI if key is available
        if self.openai_key:
            try:
                from openai import AsyncOpenAI
                self.openai_client = AsyncOpenAI(api_key=self.openai_key)
                logger.info("✅ OpenAI client initialized")
            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {e}")
        
        # Initialize Gemini if key is available
        if self.google_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.google_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                logger.info("✅ Gemini client initialized")
            except Exception as e:
                logger.warning(f"Gemini initialization failed: {e}")
    
    async def analyze_citation_confidence(
        self,
        citation: str,
        context: Optional[str] = None,
        verification_data: Optional[Dict[str, Any]] = None
    ) -> LayerResult:
        """
        Use AI to analyze citation credibility and provide confidence score
        
        Args:
            citation: The citation text to analyze
            context: Optional context where citation appears
            verification_data: Results from other verification layers
        
        Returns:
            LayerResult with AI confidence score and reasoning
        """
        
        # Try OpenAI first, fallback to Gemini
        if self.openai_client:
            return await self._analyze_with_openai(citation, context, verification_data)
        elif self.gemini_model:
            return await self._analyze_with_gemini(citation, context, verification_data)
        else:
            return LayerResult(
                status=LayerStatus.SKIPPED,
                details="AI analysis unavailable - no API keys configured",
                confidence=None,
                metadata={"reason": "No AI API keys found"}
            )
    
    async def _analyze_with_openai(
        self,
        citation: str,
        context: Optional[str],
        verification_data: Optional[Dict[str, Any]]
    ) -> LayerResult:
        """Analyze citation using OpenAI GPT-4"""
        
        try:
            # Build prompt with verification context
            prompt = self._build_analysis_prompt(citation, context, verification_data)
            
            logger.info("🤖 Analyzing citation with OpenAI GPT-4...")
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert academic citation verification system. Analyze citations for credibility, validity, and potential hallucinations. Provide confidence scores between 0 and 1."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.3,
            )
            
            analysis = response.choices[0].message.content
            
            # Parse confidence score from response
            confidence = self._extract_confidence_score(analysis)
            
            # Determine status based on confidence
            if confidence >= 0.8:
                status = LayerStatus.PASSED
            elif confidence >= 0.5:
                status = LayerStatus.WARNING
            else:
                status = LayerStatus.FAILED
            
            logger.info(f"✅ OpenAI analysis complete - Confidence: {confidence:.2f}")
            
            return LayerResult(
                status=status,
                details=analysis,
                confidence=confidence,
                metadata={
                    "model": "gpt-4",
                    "provider": "openai",
                    "tokens": response.usage.total_tokens
                }
            )
            
        except Exception as e:
            logger.error(f"OpenAI analysis error: {e}")
            return LayerResult(
                status=LayerStatus.WARNING,
                details=f"AI analysis error: {str(e)}",
                confidence=0.5,
                metadata={"error": str(e)}
            )
    
    async def _analyze_with_gemini(
        self,
        citation: str,
        context: Optional[str],
        verification_data: Optional[Dict[str, Any]]
    ) -> LayerResult:
        """Analyze citation using Google Gemini"""
        
        try:
            # Build prompt with verification context
            prompt = self._build_analysis_prompt(citation, context, verification_data)
            
            logger.info("🤖 Analyzing citation with Google Gemini...")
            
            response = self.gemini_model.generate_content(prompt)
            analysis = response.text
            
            # Parse confidence score from response
            confidence = self._extract_confidence_score(analysis)
            
            # Determine status based on confidence
            if confidence >= 0.8:
                status = LayerStatus.PASSED
            elif confidence >= 0.5:
                status = LayerStatus.WARNING
            else:
                status = LayerStatus.FAILED
            
            logger.info(f"✅ Gemini analysis complete - Confidence: {confidence:.2f}")
            
            return LayerResult(
                status=status,
                details=analysis,
                confidence=confidence,
                metadata={
                    "model": "gemini-pro",
                    "provider": "google"
                }
            )
            
        except Exception as e:
            logger.error(f"Gemini analysis error: {e}")
            return LayerResult(
                status=LayerStatus.WARNING,
                details=f"AI analysis error: {str(e)}",
                confidence=0.5,
                metadata={"error": str(e)}
            )
    
    def _build_analysis_prompt(
        self,
        citation: str,
        context: Optional[str],
        verification_data: Optional[Dict[str, Any]]
    ) -> str:
        """Build detailed prompt for AI analysis"""
        
        prompt = f"""Analyze this citation for credibility and potential AI hallucination:

**Citation:**
{citation}
"""
        
        if context:
            prompt += f"""
**Context:**
{context}
"""
        
        if verification_data:
            prompt += f"""
**Technical Verification Results:**
- URL Status: {verification_data.get('url_status', 'N/A')}
- Metadata Check: {verification_data.get('metadata_status', 'N/A')}
- Content Match: {verification_data.get('content_confidence', 'N/A')}
"""
        
        prompt += """
**Analysis Required:**
1. Evaluate if this citation appears legitimate or potentially fabricated
2. Check for red flags (fake URLs, impossible dates, non-existent authors)
3. Assess consistency between citation format and content
4. Provide a confidence score (0.0 to 1.0) where:
   - 0.9-1.0: Highly credible, verified citation
   - 0.7-0.8: Likely valid, minor concerns
   - 0.5-0.6: Suspicious, requires verification
   - 0.0-0.4: Likely hallucinated or fabricated

**Response Format:**
Confidence Score: [0.0-1.0]

Reasoning: [Your detailed analysis explaining the confidence score, red flags, and verification status]
"""
        
        return prompt
    
    def _extract_confidence_score(self, analysis: str) -> float:
        """Extract confidence score from AI response"""
        
        import re
        
        # Look for "Confidence Score: 0.85" pattern
        score_match = re.search(r'[Cc]onfidence\s+[Ss]core:\s*(\d+\.?\d*)', analysis)
        
        if score_match:
            try:
                score = float(score_match.group(1))
                # Ensure score is between 0 and 1
                if score > 1.0:
                    score = score / 100.0  # Handle percentage format
                return max(0.0, min(1.0, score))
            except ValueError:
                pass
        
        # Fallback: analyze sentiment of response
        if any(word in analysis.lower() for word in ['highly credible', 'verified', 'legitimate']):
            return 0.85
        elif any(word in analysis.lower() for word in ['likely valid', 'probably accurate']):
            return 0.70
        elif any(word in analysis.lower() for word in ['suspicious', 'questionable']):
            return 0.45
        elif any(word in analysis.lower() for word in ['fabricated', 'fake', 'hallucinated']):
            return 0.20
        
        # Default to moderate confidence
        return 0.60


# Global AI service instance
ai_service = AIService()
