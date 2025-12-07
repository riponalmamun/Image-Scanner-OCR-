# 📄 OCR Application - Image & PDF Text Extractor

একটি powerful OCR (Optical Character Recognition) application যা image এবং PDF থেকে text এবং table extract করতে পারে।

A powerful OCR application that can extract text and tables from images and PDFs with a beautiful modern interface.

---
<img width="1310" height="647" alt="image" src="https://github.com/user-attachments/assets/01a63b5e-50f0-499b-bc24-6527a9e15fb7" />

## ✨ Features

- ✅ **Image OCR** - JPG, PNG, TIFF, BMP support
- ✅ **PDF OCR** - Multi-page PDF processing
- ✅ **Table Detection** - Automatically detects and extracts tables
- ✅ **Drag & Drop** - Easy file upload interface
- ✅ **Modern UI** - Beautiful responsive design
- ✅ **File Validation** - Size limits and type checking
- ✅ **Real-time Processing** - Fast OCR with progress indicators

---

## 🚀 Quick Start

### 1️⃣ Prerequisites Install করুন

#### Tesseract OCR (Required)
**Windows:**
- Download: https://github.com/UB-Mannheim/tesseract/wiki
- Install করুন (Default location: `C:\Program Files\Tesseract-OCR`)

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install tesseract-ocr libtesseract-dev
```

**MacOS:**
```bash
brew install tesseract
```

#### Poppler (PDF processing এর জন্য)
**Windows - Manual Install:**
1. Download: https://github.com/oschwartz10612/poppler-windows/releases/latest
2. Download করুন: `Release-24.08.0-0.zip`
3. Extract করুন: `C:\poppler`
4. PATH এ add করুন: `C:\poppler\Library\bin`

**Windows - PowerShell দিয়ে (Admin):**
```powershell
# Download and extract
Invoke-WebRequest -Uri "https://github.com/oschwartz10612/poppler-windows/releases/download/v24.08.0-0/Release-24.08.0-0.zip" -OutFile "$env:TEMP\poppler.zip"
Expand-Archive -Path "$env:TEMP\poppler.zip" -DestinationPath "C:\poppler" -Force

# Add to PATH
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\poppler\Library\bin", "Machine")
```

**Linux:**
```bash
sudo apt install poppler-utils
```

**MacOS:**
```bash
brew install poppler
```

### 2️⃣ Project Setup
```bash
# Clone/Download করুন project
cd "Image Scanner OCR"

# Virtual environment তৈরি করুন
python -m venv venv

# Virtual environment activate করুন
# Windows (Git Bash):
source venv/Scripts/activate

# Windows (CMD):
venv\Scripts\activate

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Linux/Mac:
source venv/bin/activate

# Dependencies install করুন
pip install --upgrade pip
pip install -r requirements.txt
```

### 3️⃣ Configuration

`main.py` file এ Tesseract path check করুন:
```python
# Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Linux/Mac (usually automatic, but if needed):
# pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
```

### 4️⃣ Run Server
```bash
# Method 1: Python দিয়ে
python main.py

# Method 2: Uvicorn দিয়ে
uvicorn main:app --reload

# Method 3: Custom host/port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5️⃣ Access Application

Browser এ খুলুন:
```
http://localhost:8000
```

API Documentation:
```
http://localhost:8000/docs
```

---

## 📁 Project Structure
```
Image Scanner OCR/
│
├── main.py                 # FastAPI application (main entry point)
├── image_processing.py     # Image OCR functions
├── pdf_processing.py       # PDF OCR functions
├── index.html             # Frontend UI
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore            # Git ignore rules
│
└── venv/                 # Virtual environment (auto-generated)
```

---

## 🛠️ API Endpoints

### Health Check
```http
GET /health
```
Response:
```json
{
  "status": "healthy",
  "service": "OCR API"
}
```

### Image OCR
```http
POST /ocr-image/
Content-Type: multipart/form-data
Body: file (image file)
```

Response:
```json
{
  "success": true,
  "filename": "example.jpg",
  "text": "Extracted text from image...",
  "tables": [
    {
      "position": {"x": 100, "y": 200, "width": 500, "height": 300},
      "rows": ["Row 1 text", "Row 2 text"]
    }
  ],
  "text_length": 1234,
  "table_count": 1
}
```

### PDF OCR
```http
POST /ocr-pdf/
Content-Type: multipart/form-data
Body: file (PDF file)
```

Response:
```json
{
  "success": true,
  "filename": "example.pdf",
  "text": "--- Page 1 ---\nExtracted text...\n--- Page 2 ---\n...",
  "tables": [
    {
      "page": 1,
      "position": {"x": 100, "y": 200, "width": 500, "height": 300},
      "rows": ["Row 1 text", "Row 2 text"]
    }
  ],
  "text_length": 5678,
  "table_count": 2
}
```

---

## ⚙️ Configuration Options

### File Size Limit
`main.py` তে modify করুন:
```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB (default)
```

### Allowed File Types
```python
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/tiff", "image/bmp"}
ALLOWED_PDF_TYPES = {"application/pdf"}
```

### OCR Language
`image_processing.py` এবং `pdf_processing.py` তে:
```python
# English only (default)
text = pytesseract.image_to_string(image, lang='eng')

# Bengali only
text = pytesseract.image_to_string(image, lang='ben')

# Multiple languages
text = pytesseract.image_to_string(image, lang='eng+ben')

# Arabic
text = pytesseract.image_to_string(image, lang='ara')
```

**Note:** Additional language support এর জন্য Tesseract language data download করতে হবে।

---

## 🐛 Troubleshooting

### Issue: "Unable to import 'cv2'"
**Solution:**
```bash
pip install opencv-python
```

### Issue: "Unable to import 'pdf2image'"
**Solution:**
```bash
pip install pdf2image
```

### Issue: "Tesseract not found"
**Solution:**
1. Tesseract install করুন (Prerequisites section দেখুন)
2. `main.py` তে path সঠিকভাবে set করুন
3. Terminal restart করুন

### Issue: "Unable to get page count. Is poppler installed?"
**Solution:**
1. Poppler install করুন (Prerequisites section দেখুন)
2. PATH এ add করা আছে কিনা verify করুন:
```bash
   pdfinfo -v
```
3. Terminal/Command Prompt restart করুন
4. Server restart করুন

### Issue: Virtual environment activate হচ্ছে না
**Git Bash:**
```bash
source venv/Scripts/activate
```

**CMD:**
```cmd
venv\Scripts\activate
```

**PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

### Issue: Low OCR Accuracy
**Solutions:**
- Image quality ভালো রাখুন (minimum 300 DPI)
- Image এ text clear এবং readable রাখুন
- Proper lighting এ scan করুন
- Image preprocessing parameters adjust করুন

---

## 📦 Dependencies
```
fastapi==0.104.1           # Web framework
uvicorn==0.24.0           # ASGI server
python-multipart==0.0.9   # File upload support
pytesseract==0.3.10       # OCR engine wrapper
Pillow>=10.0.0            # Image processing
opencv-python>=4.8.0      # Computer vision
pdf2image>=1.16.0         # PDF to image conversion
numpy>=1.24.0             # Numerical operations
```

---

## 🎯 Usage Examples

### Basic Image Upload (Python)
```python
import requests

url = "http://localhost:8000/ocr-image/"
files = {"file": open("image.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

### Basic PDF Upload (Python)
```python
import requests

url = "http://localhost:8000/ocr-pdf/"
files = {"file": open("document.pdf", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

### Using cURL
```bash
# Image OCR
curl -X POST "http://localhost:8000/ocr-image/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@image.jpg"

# PDF OCR
curl -X POST "http://localhost:8000/ocr-pdf/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

---

## 🚀 Production Deployment

### Using Gunicorn (Linux/Mac)
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker
Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t ocr-app .
docker run -p 8000:8000 ocr-app
```

### Environment Variables (Optional)
Create `.env` file:
```env
MAX_FILE_SIZE=10485760
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
HOST=0.0.0.0
PORT=8000
```

---

## 📝 Development

### Run in Development Mode
```bash
uvicorn main:app --reload --log-level debug
```

### Run Tests
```bash
pytest tests/
```

### Code Formatting
```bash
pip install black
black .
```

### Linting
```bash
pip install pylint
pylint main.py image_processing.py pdf_processing.py
```

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - Free to use for personal and commercial projects.

---

## 👨‍💻 Author

Created with ❤️ for easy OCR processing

---

## 🔗 Useful Links

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Poppler Utils](https://poppler.freedesktop.org/)
- [OpenCV Documentation](https://docs.opencv.org/)

---
<img width="1310" height="647" alt="image" src="https://github.com/user-attachments/assets/695585de-e2a1-482d-b6d4-b79aa22b7cee" />

## 📞 Support

কোন সমস্যা হলে:
1. Check করুন Troubleshooting section
2. GitHub Issues এ post করুন
3. Documentation পড়ুন

---

## 🎉 Quick Reference

**Start Server:**
```bash
source venv/Scripts/activate  # Activate venv
uvicorn main:app --reload     # Start server
```

**Access:**
- Application: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

**Stop Server:**
Press `Ctrl + C` in terminal

---

**Happy OCR Processing! 🚀**
