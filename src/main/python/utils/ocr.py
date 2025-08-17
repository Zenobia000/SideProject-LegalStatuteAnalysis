"""
OCR (Optical Character Recognition) utility for document text extraction
"""
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..core.config import settings

logger = logging.getLogger(__name__)


class OCRProcessor:
    """OCR processor for extracting text from documents"""
    
    def __init__(self):
        self.engine = settings.ocr_engine
        self.language = settings.ocr_language
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Initialize OCR engine
        self._init_ocr_engine()
    
    def _init_ocr_engine(self):
        """Initialize the selected OCR engine"""
        self._ocr_available = False
        
        try:
            if self.engine == "paddleocr":
                self._init_paddleocr()
            elif self.engine == "tesseract":
                self._init_tesseract()
            else:
                logger.warning(f"Unsupported OCR engine: {self.engine}, using fallback mode")
                return
                
            logger.info(f"OCR engine initialized: {self.engine}")
            
        except ImportError as e:
            logger.warning(f"OCR engine {self.engine} not available: {e}")
            logger.info("OCR functionality will be limited to basic text extraction")
        except Exception as e:
            logger.warning(f"Error initializing OCR engine: {e}")
            logger.info("OCR functionality will work in fallback mode")
    
    def _init_paddleocr(self):
        """Initialize PaddleOCR engine"""
        try:
            from paddleocr import PaddleOCR
            
            # PaddleOCR supports Chinese Traditional
            lang_code = 'chinese_cht' if self.language == 'ch_tra' else 'ch'
            
            self.ocr_engine = PaddleOCR(
                use_angle_cls=True,
                lang=lang_code,
                use_gpu=False,  # Set to True if GPU available
                show_log=False
            )
            self._ocr_available = True
            
        except ImportError:
            logger.warning("PaddleOCR not installed. Install with: pip install paddlepaddle paddleocr")
            raise
    
    def _init_tesseract(self):
        """Initialize Tesseract OCR engine"""
        try:
            import pytesseract
            from PIL import Image
            
            # Test if Tesseract is available
            pytesseract.get_tesseract_version()
            
            self.pytesseract = pytesseract
            self.Image = Image
            self._ocr_available = True
            
        except ImportError:
            logger.warning("Tesseract dependencies not installed. Install with: pip install pytesseract pillow")
            raise
        except pytesseract.TesseractNotFoundError:
            logger.warning("Tesseract executable not found. Please install Tesseract OCR")
            raise
    
    def _extract_text_paddleocr(self, image_path: Path) -> str:
        """Extract text using PaddleOCR"""
        try:
            results = self.ocr_engine.ocr(str(image_path), cls=True)
            
            if not results or not results[0]:
                return ""
            
            # Extract text from results
            text_lines = []
            for line in results[0]:
                if len(line) >= 2:
                    text_lines.append(line[1][0])
            
            return "\n".join(text_lines)
            
        except Exception as e:
            logger.error(f"PaddleOCR extraction error: {e}")
            return ""
    
    def _extract_text_tesseract(self, image_path: Path) -> str:
        """Extract text using Tesseract"""
        try:
            # Configure Tesseract for Traditional Chinese
            config = '--psm 6'
            if self.language == 'ch_tra':
                config += ' -l chi_tra'
            elif self.language == 'ch_sim':
                config += ' -l chi_sim'
            
            image = self.Image.open(image_path)
            text = self.pytesseract.image_to_string(image, config=config)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Tesseract extraction error: {e}")
            return ""
    
    def _convert_pdf_to_images(self, pdf_path: Path) -> List[Path]:
        """Convert PDF pages to images for OCR processing"""
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(pdf_path)
            image_paths = []
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # Render page as image
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                pix = page.get_pixmap(matrix=mat)
                
                # Save as PNG
                image_path = pdf_path.parent / f"{pdf_path.stem}_page_{page_num + 1}.png"
                pix.save(str(image_path))
                image_paths.append(image_path)
            
            doc.close()
            return image_paths
            
        except ImportError:
            logger.error("PyMuPDF not installed. Install with: pip install pymupdf")
            return []
        except Exception as e:
            logger.error(f"PDF conversion error: {e}")
            return []
    
    def extract_text_from_image(self, image_path: Path) -> str:
        """Extract text from single image file"""
        if not self._ocr_available:
            logger.warning("OCR engine not available, using fallback")
            return self._fallback_text_extraction(image_path)
        
        try:
            if self.engine == "paddleocr":
                return self._extract_text_paddleocr(image_path)
            elif self.engine == "tesseract":
                return self._extract_text_tesseract(image_path)
            else:
                return self._fallback_text_extraction(image_path)
                
        except Exception as e:
            logger.error(f"Text extraction error: {e}")
            return self._fallback_text_extraction(image_path)
    
    def _fallback_text_extraction(self, image_path: Path) -> str:
        """Fallback text extraction when OCR engines are not available"""
        try:
            # Try basic PDF text extraction if it's a PDF converted image
            if "pdf" in str(image_path).lower():
                return f"[OCR不可用] 圖片文件: {image_path.name}"
            else:
                return f"[OCR不可用] 無法提取文字內容，檔案: {image_path.name}"
        except Exception:
            return "[OCR不可用] 文字提取失敗"
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract text from PDF file
        
        Returns:
            Dict containing:
            - text: extracted text content
            - pages: list of text per page
            - metadata: extraction metadata
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        result = {
            "text": "",
            "pages": [],
            "metadata": {
                "total_pages": 0,
                "engine": self.engine,
                "language": self.language,
                "success": False
            }
        }
        
        try:
            # Convert PDF to images
            image_paths = self._convert_pdf_to_images(pdf_path)
            
            if not image_paths:
                logger.warning("No images generated from PDF")
                return result
            
            result["metadata"]["total_pages"] = len(image_paths)
            
            # Extract text from each page image
            all_text = []
            page_texts = []
            
            for i, image_path in enumerate(image_paths):
                page_text = self.extract_text_from_image(image_path)
                page_texts.append({
                    "page": i + 1,
                    "text": page_text
                })
                
                if page_text:
                    all_text.append(f"=== 第 {i + 1} 頁 ===\n{page_text}")
                
                # Clean up temporary image
                try:
                    image_path.unlink()
                except Exception:
                    pass
            
            # Combine all text
            result["text"] = "\n\n".join(all_text)
            result["pages"] = page_texts
            result["metadata"]["success"] = True
            
            logger.info(f"PDF text extraction completed: {len(all_text)} pages processed")
            
        except Exception as e:
            logger.error(f"PDF text extraction error: {e}")
            result["metadata"]["error"] = str(e)
        
        return result
    
    async def extract_text_async(self, file_path: Path) -> Dict[str, Any]:
        """Asynchronous text extraction"""
        loop = asyncio.get_event_loop()
        
        if file_path.suffix.lower() == '.pdf':
            return await loop.run_in_executor(
                self.executor,
                self.extract_text_from_pdf,
                file_path
            )
        else:
            # For image files
            text = await loop.run_in_executor(
                self.executor,
                self.extract_text_from_image,
                file_path
            )
            return {
                "text": text,
                "pages": [{"page": 1, "text": text}],
                "metadata": {
                    "total_pages": 1,
                    "engine": self.engine,
                    "language": self.language,
                    "success": bool(text)
                }
            }


# Global OCR processor instance
ocr_processor = OCRProcessor()