"""
Document Upload API endpoints
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from loguru import logger
from typing import Optional
import time

from app.models.schemas import TextVerificationResult, VerificationOptions
from app.services.document_service import document_processor
from app.services.verification_service import VerificationService
from app.services.hallucination_models import hallucination_detector, claim_extractor

router = APIRouter()
verification_service = VerificationService()


@router.post("/upload-document", response_model=TextVerificationResult)
async def upload_document(
    file: UploadFile = File(...),
    enable_ocr: Optional[str] = Form("true"),
    enable_ai_analysis: Optional[str] = Form("true")
):
    """
    Upload PDF, DOCX, or image and verify citations
    
    Supports:
    - PDF (with OCR for scanned documents)
    - DOCX/DOC
    - Images (JPG, PNG, TIFF) with OCR
    - Plain text files
    
    Automatically extracts text, finds citations, and verifies them.
    """
    try:
        start_time = time.time()
        logger.info(f"📄 Processing uploaded file: {file.filename}")
        
        # Convert string form values to boolean
        enable_ocr_bool = enable_ocr.lower() == "true" if isinstance(enable_ocr, str) else True
        enable_ai_bool = enable_ai_analysis.lower() == "true" if isinstance(enable_ai_analysis, str) else True
        
        # Read file content
        file_content = await file.read()
        logger.info(f"📊 File size: {len(file_content)} bytes")
        
        # Process document and extract text
        doc_result = await document_processor.process_document(
            file_content=file_content,
            filename=file.filename,
            enable_ocr=enable_ocr_bool
        )
        
        if not doc_result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract text from document: {doc_result.get('error', 'Unknown error')}"
            )
        
        extracted_text = doc_result["text"]
        logger.info(f"✅ Extracted {len(extracted_text)} characters from {file.filename}")
        
        # Create verification options
        options = VerificationOptions(
            enable_ai_scoring=enable_ai_bool,
            check_metadata=True,
            check_content=True
        )
        
        # Verify citations in extracted text
        result = await verification_service.verify_text(
            text=extracted_text,
            format="plain",
            options=options
        )
        
        # Add document metadata
        result.metadata = {
            "filename": file.filename,
            "extraction_method": doc_result["method"],
            "pages": doc_result.get("pages"),
            "text_length": len(extracted_text)
        }
        
        processing_time = int((time.time() - start_time) * 1000)
        logger.info(f"✅ Document processed in {processing_time}ms")
        
        return result
        
    except ValueError as e:
        logger.error(f"Document processing error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error processing document: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/detect-hallucinations")
async def detect_hallucinations(
    text: str = Form(...),
    context: Optional[str] = Form(None)
):
    """
    Advanced hallucination detection endpoint
    
    Uses multiple detection strategies:
    1. Pattern-based detection (fake DOIs, impossible years, etc.)
    2. Structure analysis (missing authors, sources)
    3. Claim extraction and verification
    4. Overconfident language detection
    """
    try:
        logger.info(f"🔍 Running hallucination detection on {len(text)} chars")
        
        # Detect hallucinations
        result = hallucination_detector.detect_hallucinations(text, context)
        
        # Extract claims if context provided
        claims = None
        if context:
            claims = claim_extractor.extract_claims(text)
        
        return {
            "detection_result": result,
            "claims": claims,
            "text_length": len(text),
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Hallucination detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-claims")
async def extract_claims(text: str = Form(...)):
    """
    Extract verifiable claims from text
    
    Breaks down text into individual factual claims that can be verified.
    Useful for detailed fact-checking.
    """
    try:
        logger.info(f"📝 Extracting claims from {len(text)} chars")
        
        claims = claim_extractor.extract_claims(text)
        
        return {
            "claims": claims,
            "total_claims": len(claims),
            "factual_claims": len([c for c in claims if c["needs_verification"]]),
            "text_length": len(text)
        }
        
    except Exception as e:
        logger.error(f"Claim extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
