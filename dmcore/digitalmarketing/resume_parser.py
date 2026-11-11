import os
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
import re
import json
import logging

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from paddleocr import PaddleOCR
    import numpy as np
    import cv2
    PADDLE_OCR_AVAILABLE = True
except ImportError:
    PADDLE_OCR_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

logger = logging.getLogger(__name__)

class ResumeParserService:
    def __init__(self, user_creds=None):
        self.groq_api_key = user_creds.groq_api_key if user_creds else None
        
        # Local free NLP model using SpaCy
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            self.nlp = None

        # Init PaddleOCR safely
        self.ocr = None
        if PADDLE_OCR_AVAILABLE:
            try:
                # show_log=False prevents messy command line logs for each read, but is unsupported in this version
                self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
            except Exception as e:
                logger.error(f"Failed to init PaddleOCR: {e}")

    def preprocess_image_for_ocr(self, image_np):
        """
        OpenCV preprocessing to improve OCR accuracy on scanned/poor quality resumes.
        Enhances contrast, removes noise, and binarizes the image.
        """
        if not PADDLE_OCR_AVAILABLE:
            return image_np
            
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
            # Denoise to remove artifacts
            denoised = cv2.fastNlMeansDenoising(gray, h=30)
            # Thresholding (binarization) with Otsu's method
            _, thresh = cv2.threshold(denoised, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # Convert back to RGB format for PaddleOCR
            processed_img = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)
            return processed_img
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return image_np

    def extract_text_with_pymupdf(self, file_path):
        """
        Extract text using PyMuPDF (fitz) with layout preservation.
        Excellent for Canva resumes and multi-column formats.
        """
        text = ""
        if not PYMUPDF_AVAILABLE:
            return text
        try:
            doc = fitz.open(file_path)
            for page in doc:
                try:
                    page_text = page.get_text("layout")
                    if not page_text or len(page_text.strip()) < 50:
                        # Fallback to standard text if layout yields nothing
                        page_text = page.get_text()
                    text += page_text + "\n"
                except Exception as inner_e:
                    logger.warning(f"PyMuPDF layout extraction failed for a page, falling back to standard: {inner_e}")
                    text += page.get_text() + "\n"
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {e}")
        return text

    def extract_text_with_pdfplumber(self, file_path):
        """
        Extract text using pdfplumber as a secondary standard method.
        Good for standard layouts and some tables.
        """
        text = ""
        if not PDFPLUMBER_AVAILABLE:
            return text
        try:
            with pdfplumber.open(file_path, laparams={}) as pdf:
                for page in pdf.pages:
                    try:
                        page_text = page.extract_text(x_tolerance=2, y_tolerance=3)
                        if page_text:
                            text += page_text + "\n"
                    except Exception as inner_e:
                        logger.warning(f"PDFPlumber page extraction failed: {inner_e}")
        except Exception as e:
            logger.error(f"PDFPlumber extraction failed: {e}")
        return text

    def extract_text_from_pdf(self, file_path):
        """
        Multi-layer PDF extraction pipeline:
        1. PyMuPDF Layout Extraction
        2. PDFPlumber Fallback
        3. PaddleOCR + OpenCV Preprocessing (for scanned/image resumes)
        """
        text = ""
        
        # Layer 1. Try PyMuPDF Layout Extraction (best for Canva/complex layouts)
        text = self.extract_text_with_pymupdf(file_path)
        
        # Layer 2. Fallback to PDFPlumber if PyMuPDF yields little text
        if len(text.strip()) < 100:
            logger.info("PyMuPDF yielded little text, trying PDFPlumber.")
            text = self.extract_text_with_pdfplumber(file_path)

        # Layer 3. Fallback to OCR if still no text (likely scanned or image-based PDF)
        if len(text.strip()) < 100 and self.ocr and PDFPLUMBER_AVAILABLE:
            logger.info(f"Fallback to OCR reading for: {file_path}")
            text = ""
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        im = page.to_image(resolution=300).original
                        im_np = np.array(im.convert('RGB'))
                        im_processed = self.preprocess_image_for_ocr(im_np)
                        # Open CV format to Paddle OCR
                        result = self.ocr.ocr(im_processed[:, :, ::-1], cls=True)
                        if result and result[0]:
                            for line in result[0]:
                                text += line[1][0] + "\n"
            except Exception as e:
                logger.error(f"OCR Extraction failed: {e}")
                
        return text if len(text.strip()) > 0 else f"Error or empty PDF: {file_path}"

    def extract_text_from_docx(self, file_path):
        """
        Robust DOCX extraction handling paragraphs and tables.
        """
        text = ""
        if not DOCX_AVAILABLE:
            return text
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
            
            # Extract from tables as well for maximum compatibility
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text += cell.text + " "
                    text += "\n"
        except Exception as e:
            logger.error(f"Error extracting from DOCX: {e}")
        return text

    def read_document_text(self, file_path):
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return ""
            
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext in ['.doc', '.docx']:
            return self.extract_text_from_docx(file_path)
        else:
            logger.error(f"Unsupported file format: {ext}")
        return ""

    def process_with_llm(self, resume_text):
        """
        Highest Accuracy Parser: Uses the Groq LLM API.
        """
        api_key = self.groq_api_key
        if not api_key or not GROQ_AVAILABLE:
            logger.warning("Groq unavailable or API key missing.")
            return None
        
        try:
            client = Groq(api_key=api_key)
            prompt = f"""
            You are an expert HR resume parser system. Extract strictly the following fields from the given resume text.
            If a field is not found or ambiguous, set its value to exactly "Nil". Do not leave it blank or "". Give me the output strictly as a JSON object, with no backticks, markdown, or other text outside it.
            
            Fields To Extract:
            {{
                "Candidate Name": "",
                "Email ID": "",
                "Phone Number": "",
                "Location": "",
                "Qualification": "",
                "Year of Pass Out": "",
                "Job Role Applied For": "",
                "Internship Start Date": "",
                "Internship End Date": "",
                "Internship Topic": "",
                "Work Experience": ""
            }}
            
            Resume Text Start:
            {resume_text[:14000]}
            """
            
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that outputs ONLY JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            result_str = response.choices[0].message.content.strip()
            
            if result_str.startswith("```json"):
                result_str = result_str[7:-3]
            elif result_str.startswith("```"):
                result_str = result_str[3:-3]
                
            data = json.loads(result_str.strip())
            
            required_keys = ["Candidate Name", "Email ID", "Phone Number", "Location", "Qualification", "Year of Pass Out", "Job Role Applied For", "Internship Start Date", "Internship End Date", "Internship Topic", "Work Experience"]
            for k in required_keys:
                if k not in data or not data[k]:
                    data[k] = "Nil"
                    
            logger.info("Successfully extracted data via Generative AI!")
            return data
            
        except Exception as e:
            logger.error(f"LLM Parsing Failed: {e}")
            return None

    def process_locally(self, resume_text):
        """
        Standard accuracy parser using Local Regex and SpaCy NLP.
        """
        data = {
            "Candidate Name": "Nil", "Email ID": "Nil", "Phone Number": "Nil",
            "Location": "Nil", "Qualification": "Nil", "Year of Pass Out": "Nil",
            "Job Role Applied For": "Nil", "Internship Start Date": "Nil",
            "Internship End Date": "Nil", "Internship Topic": "Nil",
            "Work Experience": "Nil"
        }

        resume_text = re.sub(r'\r', '', resume_text)
        resume_text_clean = re.sub(r'[ \t]{2,}', ' ', resume_text)

        # Better Regex
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        emails = re.findall(email_pattern, resume_text_clean)
        if emails:
            data["Email ID"] = emails[0]

        phone_pattern = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
        phones = re.findall(phone_pattern, resume_text_clean)
        if phones:
            data["Phone Number"] = phones[0]

        year_pattern = r'\b(19|20)\d{2}\b'
        valid_years = [y for y in re.findall(year_pattern, resume_text_clean) if 1950 <= int(y) <= 2030]
        full_years = [y for y in re.findall(r'\b\d{4}\b', resume_text_clean) if 1950 <= int(y) <= 2030]
        if full_years:
            data["Year of Pass Out"] = max(full_years)

        # Qualifications
        qual_keywords = ['B.Tech', 'B.E', 'B.Sc', 'M.Tech', 'MBA', 'MCA', 'BBA', 'BCA', 'Bachelor', 'Master', 'Ph.D', 'Degree', 'Diploma']
        for word in qual_keywords:
            if re.search(r'\b' + re.escape(word) + r'\b', resume_text_clean, re.IGNORECASE):
                data["Qualification"] = word
                break

        # SpaCy NER for advanced entity extraction
        if self.nlp:
            doc = self.nlp(resume_text_clean[:3000])
            for ent in doc.ents:
                if ent.label_ == "PERSON" and data["Candidate Name"] == "Nil":
                    cleaned = ent.text.replace("\n", " ").strip()
                    if "@" not in cleaned and not any(char.isdigit() for char in cleaned) and len(cleaned.split()) > 1:
                        data["Candidate Name"] = cleaned
                elif ent.label_ in ["GPE", "LOC"] and data["Location"] == "Nil":
                    data["Location"] = ent.text.replace("\n", " ").strip()

        # Fallback Name Extractor from top lines
        if data["Candidate Name"] == "Nil":
            lines = [line.strip() for line in resume_text.split('\n') if len(line.strip()) > 3 and not re.match(r'^[\W\d]+$', line.strip())]
            if lines:
                data["Candidate Name"] = lines[0]

        return data

    def verify_and_correct_data(self, data):
        """
        AI Verification Step
        Validates the extracted JSON object to ensure high-quality data.
        """
        api_key = self.groq_api_key
        if not api_key or not GROQ_AVAILABLE:
            return data
            
        try:
            client = Groq(api_key=api_key)
            prompt = f"""
            You are an AI Data Verifier. Review the extracted resume data and correct inaccuracies.
            1. Clean meaningless text (e.g. OCR artifacts). Set them to "Nil".
            2. Validate format (Phone Number should be digits, Email should be valid).
            3. Fix typos based on context.
            Return ONLY a raw JSON object matching the input structure. Do not output anything else.

            Data:
            {json.dumps(data, indent=2)}
            """
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            result_str = response.choices[0].message.content.strip()
            if result_str.startswith("```json"):
                result_str = result_str[7:-3]
            elif result_str.startswith("```"):
                result_str = result_str[3:-3]
                
            verified_data = json.loads(result_str.strip())
            
            for k in data.keys():
                if k not in verified_data or not str(verified_data[k]).strip():
                    verified_data[k] = "Nil"
            return verified_data
        except Exception as e:
            logger.error(f"AI Verification Failed: {e}")
            return data

    def is_resume(self, text):
        """
        Determines if the extracted text is likely a resume by checking common resume keywords.
        """
        if not text or len(text.strip()) < 50:
            logger.warning(f"Resume check failed: Extracted text is too short ({len(text.strip()) if text else 0} chars).")
            return False
            
        # 1. AI Verification (Highest Accuracy)
        api_key = self.groq_api_key
        if api_key and GROQ_AVAILABLE:
            try:
                client = Groq(api_key=api_key)
                prompt = f"""
                Analyze the following text from a document.
                Is this document a professional Resume or Curriculum Vitae (CV) of an individual applying for a job/internship?
                Answer strictly with exactly "YES" or "NO". Do not provide any explanation.
                
                Document Text Start:
                {text[:4000]}
                """
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.0,
                    max_completion_tokens=5,
                )
                answer = response.choices[0].message.content.strip().upper()
                if "YES" in answer:
                    return True
                elif "NO" in answer:
                    return False
            except Exception as e:
                if "api_key" in str(e).lower() or "401" in str(e):
                    logger.warning(f"Groq API Key is invalid or expired. Falling back to regex. Error: {e}")
                else:
                    logger.error(f"AI is_resume check failed, falling back to regex: {e}")

        # 2. Regex Fallback Check
        text_lower = text.lower()
        keywords = [
            "experience", "education", "skills", "projects", "objective", 
            "summary", "university", "college", "degree", "bachelor", 
            "master", "achievements", "certifications", "technologies", 
            "resume", "curriculum vitae", "cv", "employment", "internship",
            "profile", "work history", "professional", "linkedin", "github",
            "contact", "address", "languages", "hobbies", "personal", "executive"
        ]
        
        # Count how many distinct keywords are present
        score = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', text_lower))
        
        # Lowered threshold to 4 distinct keywords to be more inclusive
        is_res = score >= 4
        if not is_res:
            logger.warning(f"Regex check failed: Only {score} resume keywords found. Needs at least 4. (File text length: {len(text)})")
        return is_res

    def parse_resume(self, file_path):
        """
        Main pipeline coordinating extraction, local/LLM parsing, and AI verification.
        """
        text = self.read_document_text(file_path)
        if not text:
            return None
            
        if not self.is_resume(text):
            logger.warning(f"File skipped: Does not match common resume format -> {file_path}")
            return None
            
        llm_data = self.process_with_llm(text)
        if llm_data:
            # Robust error handling and Regex fallback
            email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
            phone_pattern = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
            
            # Check Email format
            ai_email = llm_data.get("Email ID", "Nil")
            if ai_email == "Nil" or not re.search(email_pattern, ai_email):
                emails = re.findall(email_pattern, text)
                llm_data["Email ID"] = emails[0] if emails else "Nil"

            # Check Phone format (digits count check)
            ai_phone = llm_data.get("Phone Number", "Nil")
            if ai_phone == "Nil" or not re.search(r'\d{7,15}', re.sub(r'\D', '', str(ai_phone))):
                phones = re.findall(phone_pattern, text)
                llm_data["Phone Number"] = phones[0] if phones else "Nil"
                
            # Secondary Verification Pass
            final_data = self.verify_and_correct_data(llm_data)
            return final_data
            
        return self.process_locally(text)  

