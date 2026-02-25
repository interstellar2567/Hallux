"""
Advanced Verification Features - Deep Technical Differentiators
Implements the "winning" features suggested by competition analysis
"""

import re
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from loguru import logger
import httpx
from sentence_transformers import SentenceTransformer, util
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from app.core.cache import cached

class AdvancedVerificationService:
    """
    Advanced verification methods that separate Hallux from competitors
    """
    
    def __init__(self):
        self.crossref_api = "https://api.crossref.org/works/"
        self.arxiv_api = "http://export.arxiv.org/api/query?id_list="
        self.openalex_api = "https://api.openalex.org/works/"
        
        # Initialize sentence-transformers model for semantic similarity
        try:
            self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Loaded sentence-transformers model for semantic similarity")
        except Exception as e:
            logger.error(f"Failed to load embeddings model: {e}")
            self.embeddings_model = None
        
    # ========== GEMINI SUGGESTION 1: Real Crossref API Integration ==========
    

    async def scrape_and_compare_content(self, url: str, context: str) -> Dict[str, Any]:
        """
        ✨ LAYER 3 IMPLEMENTATION: Real web scraping + semantic similarity
        
        Scrapes the source URL using Playwright (handles dynamic content),
        extracts main text/abstract, calculates semantic similarity with context.
        
        Args:
            url: Source URL to scrape
            context: The claim/text from the research paper
            
        Returns:
            {
                "aligned": bool,  # True if content matches context
                "confidence": float,  # 0.0-1.0 similarity score
                "reason": str,
                "similarity_score": float,
                "content_length": int,
                "flags": List[str]
            }
        """
        flags = []
        
        try:
            # Step 1: Scrape the URL with Playwright (handles JavaScript)
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Set timeout and user agent
                await page.set_extra_http_headers({
                    "User-Agent": "HalluxBot/1.0 (Academic Citation Verification; +https://hallux.ai)"
                })
                
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                    await asyncio.sleep(2)  # Wait for dynamic content
                    
                    html_content = await page.content()
                    await browser.close()
                    
                except Exception as e:
                    await browser.close()
                    logger.warning(f"Failed to load URL {url}: {e}")
                    return {
                        "aligned": False,
                        "confidence": 0.0,
                        "reason": f"❌ Unable to access source: {str(e)[:100]}",
                        "similarity_score": 0.0,
                        "content_length": 0,
                        "flags": ["inaccessible_url"]
                    }
            
            # Step 2: Extract main content with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove scripts, styles, navigation
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                tag.decompose()
            
            # Extract abstract/main text (prioritize academic article structures)
            abstract_text = ""
            main_text = ""
            
            # Try common academic article selectors
            abstract_selectors = [
                'section.abstract',
                'div.abstract',
                'div[class*="abstract"]',
                'p[class*="abstract"]',
                'section[id*="abstract"]'
            ]
            
            for selector in abstract_selectors:
                abstract_elem = soup.select_one(selector)
                if abstract_elem:
                    abstract_text = abstract_elem.get_text(separator=' ', strip=True)
                    break
            
            # Extract main content
            main_selectors = [
                'article',
                'main',
                'div[class*="content"]',
                'div[class*="article"]',
                'section[class*="body"]'
            ]
            
            for selector in main_selectors:
                main_elem = soup.select_one(selector)
                if main_elem:
                    main_text = main_elem.get_text(separator=' ', strip=True)
                    break
            
            # Fallback: use all paragraph text
            if not main_text:
                paragraphs = soup.find_all('p')
                main_text = ' '.join([p.get_text(strip=True) for p in paragraphs])
            
            # Combine abstract + main (prioritize abstract)
            scraped_content = f"{abstract_text} {main_text}".strip()
            content_length = len(scraped_content)
            
            if content_length < 100:
                flags.append("⚠️ Very short content extracted (<100 chars)")
                return {
                    "aligned": False,
                    "confidence": 0.2,
                    "reason": "⚠️ Insufficient content extracted from source",
                    "similarity_score": 0.0,
                    "content_length": content_length,
                    "flags": flags
                }
            
            # Step 3: Calculate semantic similarity using embeddings
            if not self.embeddings_model:
                logger.error("Embeddings model not loaded, cannot calculate similarity")
                return {
                    "aligned": False,
                    "confidence": 0.0,
                    "reason": "⚠️ Similarity model unavailable",
                    "similarity_score": 0.0,
                    "content_length": content_length,
                    "flags": ["model_error"]
                }
            
            # Truncate to avoid token limits (models handle ~512 tokens)
            context_truncated = context[:2000]
            scraped_truncated = scraped_content[:2000]
            
            # Generate embeddings
            context_embedding = self.embeddings_model.encode(context_truncated, convert_to_tensor=True)
            scraped_embedding = self.embeddings_model.encode(scraped_truncated, convert_to_tensor=True)
            
            # Cosine similarity
            similarity_score = float(util.cos_sim(context_embedding, scraped_embedding)[0][0])
            
            # Step 4: Determine alignment based on thresholds
            if similarity_score >= 0.7:
                status = "✅ High similarity - Content aligns well"
                aligned = True
                confidence = similarity_score
            elif similarity_score >= 0.5:
                status = "⚠️ Moderate similarity - Partial alignment"
                aligned = False
                confidence = similarity_score * 0.8  # Penalize moderate matches
                flags.append("moderate_similarity")
            else:
                status = "❌ Low similarity - Content mismatch"
                aligned = False
                confidence = similarity_score * 0.5
                flags.append("low_similarity")
            
            # Additional checks
            if content_length < 500:
                flags.append("short_content")
            if similarity_score < 0.3:
                flags.append("possible_fabrication")
            
            return {
                "aligned": aligned,
                "confidence": confidence,
                "reason": status,
                "similarity_score": similarity_score,
                "content_length": content_length,
                "flags": flags
            }
            
        except Exception as e:
            logger.error(f"Content scraping error for {url}: {e}")
            return {
                "aligned": False,
                "confidence": 0.0,
                "reason": f"⚠️ Scraping error: {str(e)[:100]}",
                "similarity_score": 0.0,
                "content_length": 0,
                "flags": ["scraping_error"]
            }

    @cached("crossref", ttl=3600)  # Cache for 1 hour
    async def verify_doi_with_crossref(self, doi: str, citation_text: str) -> Dict[str, Any]:
        """
        DEEP ADDITION: Compare authors and year in citation vs Crossref database
        Detects "Partial Hallucination" where DOI is real but details are wrong
        """
        logger.info(f"Verifying DOI with Crossref: {doi}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.crossref_api}{doi}",
                    headers={"User-Agent": "Hallux/1.0 (mailto:hallux@example.com)"}
                )
                
                if response.status_code != 200:
                    return {
                        "verified": False,
                        "confidence": 0.0,
                        "reason": f"DOI not found in Crossref (Status: {response.status_code})"
                    }
                
                data = response.json()
                message = data.get("message", {})
                
                # Extract metadata
                actual_authors = [author.get("family", "") for author in message.get("author", [])]
                actual_year = message.get("published-print", {}).get("date-parts", [[None]])[0][0]
                actual_title = message.get("title", [""])[0]
                
                # Extract expected year from citation
                year_match = re.search(r'\((\d{4})\)', citation_text)
                expected_year = int(year_match.group(1)) if year_match else None
                
                # Extract expected authors from citation
                author_match = re.search(r'([A-Z][a-z]+)', citation_text)
                expected_author = author_match.group(1) if author_match else None
                
                # CRITICAL: Check for mismatches (Partial Hallucination Detection)
                mismatches = []
                confidence = 1.0
                
                if expected_year and actual_year and expected_year != actual_year:
                    mismatches.append(f"Year mismatch: Citation says {expected_year}, DOI says {actual_year}")
                    confidence -= 0.4
                
                if expected_author and expected_author not in actual_authors:
                    mismatches.append(f"Author mismatch: '{expected_author}' not in {actual_authors}")
                    confidence -= 0.3
                
                result = {
                    "verified": len(mismatches) == 0,
                    "confidence": max(confidence, 0.1),
                    "actual_title": actual_title,
                    "actual_authors": actual_authors,
                    "actual_year": actual_year,
                    "mismatches": mismatches,
                    "doi": doi
                }
                
                if mismatches:
                    result["reason"] = "⚠️ PARTIAL HALLUCINATION: DOI exists but details don't match"
                else:
                    result["reason"] = "✅ DOI verified with matching metadata"
                
                return result
                
        except Exception as e:
            logger.error(f"Crossref API error: {e}")
            return {
                "verified": False,
                "confidence": 0.3,
                "reason": f"Could not verify DOI: {str(e)}"
            }
    
    # ========== GEMINI SUGGESTION 2: arXiv API Integration ==========
    
    @cached("arxiv", ttl=3600)
    async def verify_arxiv_id(self, arxiv_id: str) -> Dict[str, Any]:
        """
        Verify arXiv preprints against official arXiv API
        """
        logger.info(f"Verifying arXiv ID: {arxiv_id}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.arxiv_api}{arxiv_id}")
                
                if response.status_code != 200:
                    return {
                        "verified": False,
                        "confidence": 0.0,
                        "reason": f"arXiv ID not found (Status: {response.status_code})"
                    }
                
                # Parse XML response
                content = response.text
                
                if "<title>" not in content or "entry" not in content:
                    return {
                        "verified": False,
                        "confidence": 0.1,
                        "reason": "arXiv ID format invalid or paper not found"
                    }
                
                # Extract title (simple XML parsing)
                title_match = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
                title = title_match.group(1).strip() if title_match else "Unknown"
                
                return {
                    "verified": True,
                    "confidence": 0.9,
                    "reason": "✅ arXiv preprint found",
                    "title": title,
                    "arxiv_id": arxiv_id
                }
                
        except Exception as e:
            logger.error(f"arXiv API error: {e}")
            return {
                "verified": False,
                "confidence": 0.3,
                "reason": f"Could not verify arXiv ID: {str(e)}"
            }
    
    # ========== GEMINI SUGGESTION 3: Temporal Consistency Check ==========
    
    def check_temporal_consistency(self, citation: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        DEEP THINKING FEATURE: Detect time-travel citations
        Example: A 2018 paper citing a 2022 study
        """
        logger.info("Checking temporal consistency")
        
        # Extract years from citation
        year_matches = re.findall(r'\b(19|20)\d{2}\b', citation)
        years = [int(y) for y in year_matches]
        
        if not years:
            return {
                "passed": True,
                "confidence": 0.5,
                "reason": "No publication year found"
            }
        
        current_year = datetime.now().year
        flags = []
        
        # Check 1: Future dates
        future_years = [y for y in years if y > current_year]
        if future_years:
            flags.append(f"🚩 IMPOSSIBLE: Future publication year {future_years[0]}")
        
        # Check 2: Anachronistic citations (if context has year)
        if context:
            context_years = re.findall(r'\b(19|20)\d{2}\b', context)
            if context_years:
                paper_year = int(context_years[0])
                cited_years = [y for y in years if y > paper_year]
                if cited_years:
                    flags.append(f"🚩 TIME TRAVEL: Paper from {paper_year} cites work from {cited_years[0]}")
        
        # Check 3: Unreasonably old papers for modern claims
        old_years = [y for y in years if y < 1950]
        if old_years and any(term in citation.lower() for term in ["ai", "deep learning", "neural network", "gpt"]):
            flags.append(f"🚩 ANACHRONISM: AI/ML paper allegedly from {old_years[0]}")
        
        return {
            "passed": len(flags) == 0,
            "confidence": 0.0 if flags else 0.9,
            "flags": flags,
            "reason": " | ".join(flags) if flags else "✅ Temporal consistency verified"
        }
    
    # ========== GEMINI SUGGESTION 4: Semantic Claim Matching ==========
    
    async def check_claim_source_alignment(
        self, 
        claim: str, 
        source_abstract: str,
        use_embeddings: bool = False
    ) -> Dict[str, Any]:
        """
        ADVANCED: Check if the abstract actually supports the numerical claim
        Example: Claim says "95% accuracy" but paper says "85% accuracy"
        """
        logger.info("Checking claim-source alignment")
        
        # Extract numbers from claim
        claim_numbers = re.findall(r'\b\d+(?:\.\d+)?%?\b', claim)
        source_numbers = re.findall(r'\b\d+(?:\.\d+)?%?\b', source_abstract)
        
        # Simple keyword matching
        claim_keywords = set(re.findall(r'\b[a-z]{4,}\b', claim.lower()))
        source_keywords = set(re.findall(r'\b[a-z]{4,}\b', source_abstract.lower()))
        
        keyword_overlap = len(claim_keywords & source_keywords) / len(claim_keywords) if claim_keywords else 0
        
        flags = []
        
        # Check for numerical mismatches
        if claim_numbers and source_numbers:
            if not any(cn in source_numbers for cn in claim_numbers):
                flags.append(f"🚩 STAT MISMATCH: Claim mentions {claim_numbers} but source has {source_numbers}")
        
        # Check keyword alignment
        if keyword_overlap < 0.3:
            flags.append(f"⚠️ LOW SEMANTIC OVERLAP: Only {keyword_overlap*100:.0f}% keyword match")
        
        similarity_score = keyword_overlap
        
        return {
            "aligned": len(flags) == 0,
            "confidence": similarity_score,
            "similarity_score": round(similarity_score * 100, 1),
            "flags": flags,
            "reason": " | ".join(flags) if flags else f"✅ {similarity_score*100:.0f}% semantic alignment"
        }
    
    # ========== GEMINI SUGGESTION 5: Citation Graph Reputation ==========
    
    @cached("openalex", ttl=86400)
    async def check_citation_network(self, doi: str) -> Dict[str, Any]:
        """
        Check paper reputation via OpenAlex citation count
        Detects "citation mills" and fake papers
        """
        logger.info(f"Checking citation network for DOI: {doi}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # OpenAlex requires DOI format: https://doi.org/10.xxxx/xxxxx
                doi_url = f"https://doi.org/{doi}"
                response = await client.get(
                    f"{self.openalex_api}doi:{doi}",
                    headers={"User-Agent": "Hallux/1.0 (mailto:hallux@example.com)"}
                )
                
                if response.status_code != 200:
                    return {
                        "verified": False,
                        "confidence": 0.3,
                        "reason": "Paper not found in OpenAlex"
                    }
                
                data = response.json()
                
                cited_by_count = data.get("cited_by_count", 0)
                publication_year = data.get("publication_year")
                authorships = len(data.get("authorships", []))
                
                # Calculate reputation score
                reputation_flags = []
                confidence = 0.5
                
                if cited_by_count > 50:
                    reputation_flags.append(f"✅ Well-cited ({cited_by_count} citations)")
                    confidence += 0.3
                elif cited_by_count == 0 and publication_year and (datetime.now().year - publication_year) > 2:
                    reputation_flags.append(f"⚠️ No citations after {datetime.now().year - publication_year} years")
                    confidence -= 0.2
                
                if authorships == 0:
                    reputation_flags.append("🚩 No authors listed (potential fake)")
                    confidence -= 0.4
                
                return {
                    "verified": confidence > 0.5,
                    "confidence": max(confidence, 0.1),
                    "cited_by_count": cited_by_count,
                    "reputation_flags": reputation_flags,
                    "reason": " | ".join(reputation_flags)
                }
                
        except Exception as e:
            logger.error(f"OpenAlex API error: {e}")
            return {
                "verified": False,
                "confidence": 0.3,
                "reason": f"Could not check citation network: {str(e)}"
            }
    
    # ========== GEMINI SUGGESTION 6: Circular Citation Detection ==========
    
    async def detect_circular_citations(self, doi1: str, doi2: str) -> Dict[str, Any]:
        """
        Detect if Paper A cites Paper B and Paper B cites Paper A
        without actual research backing either (citation mills)
        """
        logger.info(f"Checking for circular citations: {doi1} <-> {doi2}")
        
        # This requires more complex graph analysis
        # For hackathon, return framework
        return {
            "circular": False,
            "confidence": 0.5,
            "reason": "Circular citation detection not yet implemented"
        }


# Global instance
advanced_verifier = AdvancedVerificationService()
