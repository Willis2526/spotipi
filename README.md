# Spotify Controller Web UI

A sleek, modern web-based Spotify controller built with FastAPI and Vue.js that can run on any system including Raspberry Pi. Control your Spotify playback with a beautiful, responsive interface from any device on your network.

## Features

- 🎵 **Full Playback Control**: Play, pause, next, previous track
- 🔀 **Shuffle & Repeat**: Toggle shuffle and cycle through repeat modes
- 🎯 **Seek**: Click anywhere on the progress bar to jump to that position
- 🎨 **Modern UI**: Android Auto-inspired design with ambient album art glow
- 💡 **Dynamic Lighting**: Album art glow that fades like an incandescent bulb when paused
- ⚙️ **Easy Configuration**: Built-in settings modal for credentials
- 🌐 **Network Access**: Access from any device on your network
- 📱 **Fully Responsive**: Works perfectly from phone to 4K displays
- 💻 **Cross-Platform**: Works on Raspberry Pi, Linux, Mac, Windows
- 🚀 **FastAPI Backend**: Modern, fast, and auto-documented API

## Screenshots

The UI features:
- Large centered album artwork with ambient LED-style glow effect
- Android Auto-inspired control layout
- Clickable progress bar for seeking
- Shuffle and repeat controls
- Settings modal for configuration
- Responsive design for all screen sizes

## Tech Stack

- **Backend**: FastAPI with Uvicorn ASGI server
- **Frontend**: Vue.js 3 (CDN, no build process)
- **API**: Spotify Web API via Spotipy
- **Styling**: Pure CSS with modern animations

## Prerequisites

1. **Spotify Premium Account** (required for API access)
2. **Python 3.7+**
3. **Spotify Developer App** (free to create)

## Setup Instructions

### Step 1: Create a Spotify App

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create an App"
4. Fill in the app name and description
5. Accept the terms and create
6. Note your **Client ID** and **Client Secret**
7. Click "Edit Settings"
8. Add `http://localhost:8888/callback` to Redirect URIs (or use your Pi's IP)
9. Save the settings

### Step 2: Install the Application

#### On Raspberry Pi / Linux:

```bash
# Clone or download the files to your system
cd ~
mkdir spotify-controller
cd spotify-controller

# Run the automated installation script
chmod +x install.sh
./install.sh
```

The install script will:
- Create a virtual environment
- Install all dependencies (FastAPI, Uvicorn, Spotipy)
- Make scripts executable
- Optionally set up systemd service for auto-start

#### Manual Installation:

```bash
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

#### On Windows:

```bash
# Navigate to the directory
cd spotify-controller

# Create a virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Run the Server

```bash
# Activate virtual environment if not already active
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Run the server
python server.py
```

The server will start on `http://0.0.0.0:8888` by default.

### Step 4: Configure Credentials

1. Open your browser and go to `http://localhost:8888` (or your Pi's IP address)
2. Click the **settings icon** (⚙️) in the top right
3. Enter your Spotify **Client ID** and **Client Secret**
4. Adjust the Redirect URI if needed (match what you set in Spotify Dashboard)
5. Click "Save Configuration"
6. **Restart the server**

### Step 5: Authenticate

1. After restarting, the first time you try to control playback, you'll be redirected to Spotify
2. Log in and authorize the application
3. You'll be redirected back to the controller
4. Start playing music on any Spotify device
5. Use the web UI to control playback!

## Usage

### Accessing from Other Devices

Once running on your Raspberry Pi or server:

1. Find your device's IP address:
   ```bash
   hostname -I  # Linux/Pi
   ipconfig     # Windows
   ```

2. Access from any device on your network:
   ```
   http://YOUR_IP_ADDRESS:8888
   ```

### Features Available

- **Play/Pause**: Large center button
- **Next/Previous Track**: Skip buttons on either side
- **Shuffle**: Left side button, turns green when active
- **Repeat**: Right side button, cycles through off/context/track modes
- **Seek**: Click anywhere on the progress bar to jump to that position
- **Album Glow**: Ambient lighting effect that fades out when paused
- **Settings**: Configure credentials and server settings

### API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: `http://localhost:8888/docs`
- **ReDoc**: `http://localhost:8888/redoc`
- **OpenAPI JSON**: `http://localhost:8888/openapi.json`

## Running on Startup (Raspberry Pi)

### Method 1: systemd Service (Recommended)

The install script can set this up automatically, or manually:

1. Create a service file:
```bash
sudo nano /etc/systemd/system/spotify-controller.service
```

2. Add this content (adjust paths):
```ini
[Unit]
Description=Spotify Controller Web UI
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/spotify-controller
ExecStart=/home/pi/spotify-controller/venv/bin/python /home/pi/spotify-controller/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:
```bash
sudo systemctl enable spotify-controller
sudo systemctl start spotify-controller
```

4. Check status:
```bash
sudo systemctl status spotify-controller
```

5. View logs:
```bash
sudo journalctl -u spotify-controller -f
```

### Method 2: Crontab

```bash
crontab -e
```

Add this line:
```
@reboot sleep 30 && cd /home/pi/spotify-controller && /home/pi/spotify-controller/venv/bin/python server.py > /tmp/spotify.log 2>&1
```

## Configuration

Configuration is stored in `config.json` in the project root directory.

Default settings:
- **Port**: 8888
- **Host**: 0.0.0.0 (accessible from network)
- **Redirect URI**: http://localhost:8888/callback

You can modify these through the settings UI or by editing the config file directly.

The Spotify authentication cache is stored as `.spotify_cache` in the project root.

## API Endpoints

The FastAPI server exposes these REST API endpoints:

**Playback Control:**
- `GET /api/playback` - Get current playback state
- `POST /api/play` - Resume playback
- `POST /api/pause` - Pause playback
- `POST /api/next` - Next track
- `POST /api/previous` - Previous track
- `POST /api/seek` - Seek to position (body: `{"position_ms": 90000}`)

**Settings:**
- `POST /api/volume` - Set volume (body: `{"volume": 50}`)
- `POST /api/shuffle` - Toggle shuffle (body: `{"state": true}`)
- `POST /api/repeat` - Set repeat mode (body: `{"state": "off"}`)

**Configuration:**
- `GET /api/config` - Get configuration
- `POST /api/config` - Update configuration

## Troubleshooting

### "No active device found"
- Make sure Spotify is playing on at least one device
- Open Spotify on your phone/computer and start playing something
- The controller will then be able to control that device

### "Please configure your Spotify credentials"
- Open settings and enter your Client ID and Client Secret
- Make sure you restart the server after saving

### Cannot access from other devices
- Check your firewall settings
- Make sure the Pi and your device are on the same network
- Try accessing via IP address instead of localhost

### Authentication issues
- Verify your Redirect URI matches exactly in both:
  - Spotify Developer Dashboard
  - Controller settings
- Clear the cache file: `rm .spotify_cache` (in project directory)
- Try authenticating again

### Album art glow not showing
- Make sure album art is loading (check browser console)
- Verify the track has album artwork in Spotify
- Try refreshing the page

## Development

### Project Structure
```
spotify-controller/
├── server.py    # FastAPI backend
├── templates/
│   └── index.html           # Vue.js frontend
├── requirements.txt         # Python dependencies
├── install.sh              # Installation script
└── README.md               # This file
```

### Architecture
- **Backend**: FastAPI with class-based route handlers
- **Frontend**: Single-file Vue.js 3 application
- **State Management**: Vue reactive data
- **API Communication**: Fetch API with async/await
- **Authentication**: Spotipy OAuth flow with file-based cache

## Security Notes

- The server runs on your local network by default
- Credentials are stored locally in `config.json` in the project root
- Client Secret is masked in the UI after saving
- Consider using environment variables for credentials in production
- If exposing to the internet, use HTTPS and proper authentication
- Add `config.json` and `.spotify_cache` to `.gitignore` if using version control

## Customization

### Changing the Port

Edit the settings in the UI or modify `config.json`:
```json
{
  "port": 8080
}
```

### Adjusting the Glow Effect

Edit `templates/index.html` and modify the `.album-art-glow` CSS:
```css
filter: blur(80px);        /* Blur amount */
opacity: 0.5;              /* Brightness */
transform: scale(1.2);     /* Size */
```

### Changing Colors

The green accent color (#1db954) can be changed throughout the CSS in `templates/index.html`.

## Requirements

- Python 3.7+
- FastAPI 0.109.0+
- Uvicorn 0.27.0+
- Spotipy 2.23.0
- Pydantic 2.5.0+
- Spotify Premium Account
- Active internet connection

## License

MIT License - Feel free to modify and use as you wish!

## Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Vue.js](https://vuejs.org/) - Progressive JavaScript framework
- [Spotipy](https://spotipy.readthedocs.io/) - Spotify API wrapper
- [Uvicorn](https://www.uvicorn.org/) - ASGI server

Inspired by Android Auto's clean, driver-focused interface design.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Verify your Spotify Developer App settings
3. Check the server logs for error messages
4. Ensure your Spotify Premium is active
5. Visit the API docs at `/docs` for endpoint testing

Enjoy your music! 🎵