#!/bin/bash

# Spotify Controller Installation Script
# For Linux/Raspberry Pi

echo "=========================================="
echo "Spotify Controller Installation"
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3.7 or higher first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed!"
    echo "Installing pip..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi

echo "✓ pip3 is available"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    echo "Installing python3-venv..."
    sudo apt-get install -y python3-venv
    python3 -m venv venv
fi

echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing Python dependencies (FastAPI, Uvicorn, Spotipy)..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Make the main script executable
chmod +x server.py

echo "=========================================="
echo "✓ Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Create a Spotify App at:"
echo "   https://developer.spotify.com/dashboard"
echo ""
echo "2. Start the server:"
echo "   python server.py"
echo ""
echo "3. Open your browser to:"
echo "   http://localhost:8888"
echo ""
echo "4. Click the settings icon (⚙️) and enter your credentials"
echo ""
echo "5. Restart the server and enjoy!"
echo ""
echo "📚 API Documentation available at:"
echo "   http://localhost:8888/docs"
echo ""

# Ask if user wants to create systemd service
read -p "Would you like to install as a systemd service (auto-start on boot)? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    CURRENT_DIR=$(pwd)
    CURRENT_USER=$(whoami)
    
    echo "Creating systemd service..."
    
    sudo tee /etc/systemd/system/spotify-controller.service > /dev/null <<EOF
[Unit]
Description=Spotify Controller Web UI
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
ExecStart=$CURRENT_DIR/venv/bin/python $CURRENT_DIR/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable spotify-controller
    
    echo "✓ Systemd service created and enabled"
    echo ""
    echo "Service commands:"
    echo "  Start:   sudo systemctl start spotify-controller"
    echo "  Stop:    sudo systemctl stop spotify-controller"
    echo "  Status:  sudo systemctl status spotify-controller"
    echo "  Logs:    sudo journalctl -u spotify-controller -f"
    echo ""
    echo "To start now, run:"
    echo "  sudo systemctl start spotify-controller"
fi

echo ""
echo "=========================================="
echo "Installation complete! 🎵"
echo "=========================================="
echo ""
echo "Features:"
echo "  • Play/Pause, Next, Previous controls"
echo "  • Shuffle and Repeat modes"
echo "  • Seekable progress bar"
echo "  • Ambient album art glow effect"
echo "  • Fully responsive design"
echo "  • FastAPI with auto-generated docs"
echo ""