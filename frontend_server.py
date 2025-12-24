#!/usr/bin/env python3
"""
Healthcare-AI-Quantum-System - Frontend Server
Serves the premium landing page with API integration
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path

# Create FastAPI app
app = FastAPI(
    title="Healthcare-AI-Quantum-System - Landing Page",
    version="1.0.0",
    description="Premium landing page for the world's first quantum-enhanced healthcare AI"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
frontend_dir = Path(__file__).parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_dir / "static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def landing_page():
    """Serve the premium landing page"""
    html_file = frontend_dir / "templates" / "index.html"
    with open(html_file, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/{page_name}.html", response_class=HTMLResponse)
async def serve_html_page(page_name: str):
    """Serve any HTML page from templates directory"""
    html_file = frontend_dir / "templates" / f"{page_name}.html"
    if html_file.exists():
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    else:
        # Return 404 page if exists, otherwise generic 404
        notfound_file = frontend_dir / "templates" / "404.html"
        if notfound_file.exists():
            with open(notfound_file, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read(), status_code=404)
        return HTMLResponse(content="<h1>404 - Page Not Found</h1>", status_code=404)

@app.get("/health")
async def health_check():
    """Health check for frontend server"""
    return {
        "status": "healthy",
        "service": "Healthcare-AI-Quantum-System Landing Page",
        "version": "1.0.0",
        "pages_available": 26
    }

if __name__ == "__main__":
    print("=" * 70)
    print("🏥 Healthcare-AI-Quantum-System - Premium Landing Page")
    print("=" * 70)
    print("")
    print("✨ Features:")
    print("  • Bilingual (Turkish/English)")
    print("  • Animated particle background")
    print("  • Live API demonstrations")
    print("  • Quantum visualization")
    print("  • Premium UI/UX")
    print("")
    print("🌐 Server starting...")
    print("  • Landing Page: http://localhost:3000")
    print("  • API Backend:  http://localhost:8000")
    print("")
    print("📚 Available Pages (26 total):")
    print("  • Home:          http://localhost:3000")
    print("  • Features:      http://localhost:3000/features.html")
    print("  • Demo:          http://localhost:3000/demo.html")
    print("  • Pricing:       http://localhost:3000/pricing.html")
    print("  • Contact:       http://localhost:3000/contact.html")
    print("  • About:         http://localhost:3000/about.html")
    print("  • +20 more pages available!")
    print("")
    print("=" * 70)
    print("")

    uvicorn.run(
        "frontend_server:app",
        host="0.0.0.0",
        port=3000,
        reload=False,
        log_level="info"
    )
