# ✨ URL Shortener Pro

A modern, feature-rich URL shortener built with FastAPI, featuring a beautiful glassmorphism UI, multi-language support, sound effects, and QR code generation.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## 🌟 Features

### Core Functionality
- ⚡ **URL Shortening** - Convert long URLs into short, shareable links
- 📊 **Click Analytics** - Track how many times each URL is clicked
- 🔗 **Permanent Storage** - SQLite database for reliable data persistence
- 🎯 **Base62 Encoding** - Short, readable URL codes

### User Experience
- 🎨 **Modern Glassmorphism UI** - Beautiful, translucent card design
- 🌈 **Animated Gradient Background** - Dynamic color-shifting backgrounds
- ✨ **Floating Particles** - Ambient particle animations
- 🎭 **Dark/Light Theme** - Toggle between themes with smooth transitions
- 📱 **Fully Responsive** - Works perfectly on mobile and desktop

### Advanced Features
- 🌍 **Multi-Language Support** - English, Turkish (Türkçe), German (Deutsch)
- 🔊 **Sound Effects** - Audio feedback for all interactions
- 🎉 **Confetti Animation** - Celebration effects on successful shortening
- 📲 **QR Code Generation** - Automatic QR codes for each shortened URL
- 📋 **One-Click Copy** - Copy URLs to clipboard with visual feedback

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or navigate to the project directory:**
```bash
cd "/Users/emre/Desktop/Github Projects/url shortener"
```

2. **Create and activate virtual environment:**
```bash
python3 -m venv ../.venv
source ../.venv/bin/activate  # On macOS/Linux
# or
../.venv\Scripts\activate  # On Windows
```

3. **Install dependencies:**
```bash
pip install fastapi uvicorn[standard] pydantic qrcode[pil]
```

4. **Run the application:**
```bash
uvicorn url-shortener:app --reload --port 8002
```

5. **Open in browser:**
```
http://localhost:8002
```

## 📚 Usage

### Web Interface

1. **Shorten a URL:**
   - Enter a long URL in the input field
   - Click "🚀 Shorten" or press Enter
   - Get your shortened URL with QR code instantly

2. **Change Language:**
   - Click 🇬🇧 EN for English
   - Click 🇹🇷 TR for Turkish
   - Click 🇩🇪 DE for German

3. **Toggle Theme:**
   - Click the 🌙/☀️ button in the top-right corner

4. **Copy URL:**
   - Click the 📋 Copy button next to any shortened URL

5. **Delete URL:**
   - Click the 🗑️ button to remove a shortened URL

### API Endpoints

#### **POST /shorten**
Create a shortened URL.

**Request:**
```json
{
  "url": "https://example.com/very-long-url"
}
```

**Response:**
```json
{
  "code": "a",
  "short_url": "http://localhost:8002/a",
  "long_url": "https://example.com/very-long-url",
  "qr_code": "base64_encoded_png..."
}
```

#### **GET /{code}**
Redirect to the original URL (increments click counter).

**Example:**
```bash
curl -L http://localhost:8002/a
# Redirects to original URL
```

#### **GET /urls**
Get all shortened URLs with statistics.

**Response:**
```json
[
  {
    "id": 1,
    "code": "a",
    "original_url": "https://example.com",
    "created_at": "2025-11-09T12:00:00",
    "clicks": 5
  }
]
```

#### **DELETE /urls/{id}**
Delete a shortened URL by ID.

**Example:**
```bash
curl -X DELETE http://localhost:8002/urls/1
```

## 🎨 User Interface Features

### Animations
- **Fade-in-up** - Smooth entrance animations for cards
- **Gradient shift** - Dynamic background color transitions
- **Particle floating** - Ambient particle motion
- **Confetti burst** - Success celebration effect
- **Button shine** - Interactive button hover effects

### Sound Effects
- 🎵 **Success** - Ascending musical notes (C-E-G)
- 📋 **Copy** - Short confirmation beep
- 🗑️ **Delete** - Descending tone
- ❌ **Error** - Low warning tone
- 👆 **Click** - Tactile button feedback

### Themes
- **Light Mode** - Clean, bright interface
- **Dark Mode** - Eye-friendly dark interface
- Smooth transitions between themes
- Persistent theme selection

## 🌍 Supported Languages

| Language | Code | Native Name |
|----------|------|-------------|
| English  | en   | English     |
| Turkish  | tr   | Türkçe      |
| German   | de   | Deutsch     |

All UI elements, messages, and date formats adapt to the selected language.

## 🗂️ Project Structure

```
url shortener/
├── url-shortener.py      # Main application file
├── url_shortener.db      # SQLite database (auto-created)
└── README.md            # This file
```

## 🔧 Technical Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **Uvicorn** - Lightning-fast ASGI server
- **Pydantic** - Data validation
- **SQLite** - Embedded database
- **qrcode** - QR code generation

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **CSS3** - Modern styling with animations
- **Web Audio API** - Sound effects
- **HTML5** - Semantic markup

### Features Implementation
- **Base62 Encoding** - Short URL generation
- **Web Audio API** - Real-time sound synthesis
- **LocalStorage** - Persistent user preferences
- **Clipboard API** - One-click copying
- **Canvas/SVG** - QR code rendering

## 📊 Database Schema

```sql
CREATE TABLE urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_url TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    clicks INTEGER DEFAULT 0
);

CREATE UNIQUE INDEX idx_original_url ON urls(original_url);
```

## 🎯 Configuration

### Change Port
Edit the uvicorn command:
```bash
uvicorn url-shortener:app --reload --port YOUR_PORT
```

### Change Base URL
The base URL is automatically detected from the request. To override:
```python
short_url = f"https://yourdomain.com/{code}"
```

### Disable Sound Effects
Sound effects gracefully degrade if Web Audio API is unavailable.

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8002
lsof -ti:8002 | xargs kill -9

# Or use a different port
uvicorn url-shortener:app --reload --port 8003
```

### Module Import Errors
```bash
# Ensure virtual environment is activated
source ../.venv/bin/activate

# Reinstall dependencies
pip install --upgrade fastapi uvicorn pydantic qrcode[pil]
```

### Database Issues
```bash
# Delete and recreate database
rm url_shortener.db

# Restart the application (will auto-create DB)
uvicorn url-shortener:app --reload --port 8002
```

### Audio Not Working
- Check browser console for errors
- Some browsers require user interaction before playing audio
- Audio is optional - app works without it

## 🚀 Deployment

### Production Recommendations

1. **Use a production ASGI server:**
```bash
pip install gunicorn
gunicorn url-shortener:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. **Set up HTTPS:**
   - Use Nginx or Caddy as reverse proxy
   - Obtain SSL certificate (Let's Encrypt)

3. **Configure environment variables:**
```bash
export PORT=8002
export DATABASE_URL=/path/to/database.db
```

4. **Enable CORS if needed:**
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)
```

## 🎨 Customization

### Change Colors
Edit CSS variables in the `<style>` section:
```css
:root {
  --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --accent: #2563eb;
  --bg: #f8f9fe;
}
```

### Add New Language
Add to the `translations` object:
```javascript
const translations = {
  // ... existing languages
  es: {
    title: '✨ Acortador de URL Pro',
    subtitle: 'Acorta enlaces largos al instante',
    // ... more translations
  }
};
```

### Modify Sound Effects
Edit frequency values in the `playSound()` function:
```javascript
case 'success':
  oscillator.frequency.setValueAtTime(523.25, audioContext.currentTime);
```

## 📝 API Documentation

FastAPI automatically generates interactive API docs:

- **Swagger UI:** http://localhost:8002/docs
- **ReDoc:** http://localhost:8002/redoc

## 🤝 Contributing

Contributions are welcome! Ideas for improvements:
- [ ] Custom short URL slugs
- [ ] Expiration dates for URLs
- [ ] Password protection
- [ ] Analytics dashboard
- [ ] Rate limiting
- [ ] More languages
- [ ] Export statistics
- [ ] URL validation enhancements

## 📄 License

MIT License - Feel free to use this project for personal or commercial purposes.

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- The open-source community
- Modern web standards (Web Audio API, Clipboard API, etc.)

## 📧 Support

For issues, questions, or suggestions, please open an issue on the project repository.

---

**Made with ❤️ and modern web technologies**

*Last updated: November 9, 2025*
