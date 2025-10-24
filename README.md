# 🤖 AI Document Reader

A powerful AI-powered document reader with ChatGPT-like interface that can analyze, summarize, and chat about your documents.

## ✨ Features

- **📄 Document Preview** - View PDF pages, tables, and HTML content
- **🤖 AI Summaries** - Get intelligent summaries using Google Gemini AI
- **💬 Interactive Chat** - Ask questions about your documents
- **📊 Multiple Formats** - Support for PDF, CSV, Excel, and HTML files
- **📤 Export Summaries** - Download summaries as text files
- **🎨 Modern UI** - ChatGPT-inspired dark theme interface

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Shaheer-20/ai-document-reader.git
cd ai-document-reader
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root:
```env
# Google Gemini API Key
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_actual_api_key_here

# Flask Secret Key (for session management)
SECRET_KEY=your-secret-key-change-this-in-production
```

### 4. Run the Application
```bash
python app.py
```

Visit `http://127.0.0.1:5000` in your browser.

## 🔧 Setup Instructions

### Getting Your Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and add it to your `.env` file

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `SECRET_KEY`: Flask secret key for session management (optional, will use default)

## 📁 Project Structure

```
ai-document-reader/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## 🛡️ Security

- `.env` files are automatically ignored by Git
- API keys are never committed to the repository
- Session data is stored securely
- All file processing happens locally

## 🎯 Usage

1. **Upload a Document** - Drag and drop or click to select a file
2. **Preview** - View your document content
3. **Get Summary** - AI generates an intelligent summary
4. **Chat** - Ask questions about the document content
5. **Export** - Download the summary as a text file

## 📋 Supported File Types

- **PDF** - Text extraction and page preview
- **CSV** - Table data analysis
- **Excel (XLSX)** - Spreadsheet processing
- **HTML** - Web page content extraction

## 🔧 Advanced Features

- **Document Preview** - Visual preview of PDF pages
- **Table Analysis** - CSV/Excel data visualization
- **Interactive Chat** - Real-time Q&A with AI
- **Export Functionality** - Download summaries
- **Session Management** - Persistent document context

## 🐛 Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your `GEMINI_API_KEY` is correctly set in the `.env` file
2. **File Upload Issues**: Check that your file is in a supported format
3. **Preview Not Loading**: Ensure the document is not corrupted or password-protected

### Getting Help

If you encounter issues:
1. Check the console for error messages
2. Verify your API key is valid
3. Ensure all dependencies are installed
4. Check that your file format is supported

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⭐ Star the Repository

If you found this project helpful, please give it a star on GitHub!
