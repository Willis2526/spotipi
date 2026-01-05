#!/usr/bin/env python3
"""
Spotify Controller Server
A web-based Spotify controller with a modern UI using FastAPI
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
from pathlib import Path
from typing import Optional
import uvicorn

# Configuration file path - in project root
CONFIG_FILE = Path(__file__).parent / "config.json"
CACHE_FILE = Path(__file__).parent / ".spotify_cache"

# Default configuration
DEFAULT_CONFIG = {
    "client_id": "",
    "client_secret": "",
    "redirect_uri": "http://127.0.0.1:8888/callback",
    "port": 8888,
    "host": "0.0.0.0"
}

# Global state for auth manager
_auth_manager_cache = None

# Pydantic models
class Config(BaseModel):
    client_id: Optional[str] = ""
    client_secret: Optional[str] = ""
    redirect_uri: Optional[str] = "http://127.0.0.1:8888/callback"
    port: Optional[int] = 8888
    host: Optional[str] = "0.0.0.0"

class VolumeRequest(BaseModel):
    volume: int

class ShuffleRequest(BaseModel):
    state: bool

class RepeatRequest(BaseModel):
    state: str  # "off", "track", "context"

class SeekRequest(BaseModel):
    position_ms: int

class SetupRequest(BaseModel):
    client_id: str
    client_secret: str


def load_config():
    """Load configuration from file"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return {**DEFAULT_CONFIG, **config}
    return DEFAULT_CONFIG.copy()

def save_config(config: dict):
    """Save configuration to file"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def get_auth_manager():
    """Get Spotify OAuth manager"""
    global _auth_manager_cache

    config = load_config()

    if not config["client_id"] or not config["client_secret"]:
        return None

    # Create manager if not cached
    if _auth_manager_cache is None:
        scope = "user-read-playback-state,user-modify-playback-state,user-read-currently-playing"
        _auth_manager_cache = SpotifyOAuth(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            redirect_uri=config["redirect_uri"],
            scope=scope,
            cache_path=str(CACHE_FILE),
            open_browser=False,
            show_dialog=False
        )

    return _auth_manager_cache

def get_spotify_client():
    """Get authenticated Spotify client"""
    auth_manager = get_auth_manager()

    if not auth_manager:
        return None

    try:
        # Check if we have a cached token (don't trigger auth flow)
        token_info = auth_manager.get_cached_token()
        if not token_info:
            return None

        # Use auth_manager so tokens auto-refresh
        sp = spotipy.Spotify(auth_manager=auth_manager)
        return sp
    except Exception as e:
        print(f"Error creating Spotify client: {e}")
        return None


class SpotifyController:
    """Main Spotify Controller class"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Spotify Controller",
            description="Control your Spotify playback with a modern web interface",
            version="1.0.0"
        )
        
        # Setup all API routes
        self.setup_routes()
    
    def setup_routes(self):
        """Setup all API routes"""
        # Main UI
        self.app.add_api_route(
            path="/",
            endpoint=self.index_handler,
            methods=["GET"],
            response_class=HTMLResponse,
            include_in_schema=False
        )
        
        # Configuration endpoints
        self.app.add_api_route(
            path="/api/config",
            endpoint=self.get_config_handler,
            methods=["GET"],
            include_in_schema=True
        )
        
        self.app.add_api_route(
            path="/api/config",
            endpoint=self.update_config_handler,
            methods=["POST"],
            include_in_schema=True
        )

        # Setup endpoints
        self.app.add_api_route(
            path="/api/setup/status",
            endpoint=self.get_setup_status_handler,
            methods=["GET"],
            include_in_schema=True
        )

        self.app.add_api_route(
            path="/api/setup",
            endpoint=self.setup_credentials_handler,
            methods=["POST"],
            include_in_schema=True
        )

        # OAuth endpoints
        self.app.add_api_route(
            path="/api/auth/url",
            endpoint=self.get_auth_url_handler,
            methods=["GET"],
            include_in_schema=True
        )

        self.app.add_api_route(
            path="/callback",
            endpoint=self.oauth_callback_handler,
            methods=["GET"],
            include_in_schema=False
        )

        # Playback endpoints
        self.app.add_api_route(
            path="/api/playback",
            endpoint=self.get_playback_handler,
            methods=["GET"],
            include_in_schema=True
        )
        
        self.app.add_api_route(
            path="/api/play",
            endpoint=self.play_handler,
            methods=["POST"],
            include_in_schema=True
        )
        
        self.app.add_api_route(
            path="/api/pause",
            endpoint=self.pause_handler,
            methods=["POST"],
            include_in_schema=True
        )
        
        self.app.add_api_route(
            path="/api/next",
            endpoint=self.next_track_handler,
            methods=["POST"],
            include_in_schema=True
        )
        
        self.app.add_api_route(
            path="/api/previous",
            endpoint=self.previous_track_handler,
            methods=["POST"],
            include_in_schema=True
        )
        
        self.app.add_api_route(
            path="/api/volume",
            endpoint=self.set_volume_handler,
            methods=["POST"],
            include_in_schema=True
        )
        
        self.app.add_api_route(
            path="/api/shuffle",
            endpoint=self.toggle_shuffle_handler,
            methods=["POST"],
            include_in_schema=True
        )
        
        self.app.add_api_route(
            path="/api/repeat",
            endpoint=self.set_repeat_handler,
            methods=["POST"],
            include_in_schema=True
        )
        
        self.app.add_api_route(
            path="/api/seek",
            endpoint=self.seek_handler,
            methods=["POST"],
            include_in_schema=True
        )
    
    async def index_handler(self):
        """Serve the main UI"""
        html_file = Path(__file__).parent / "templates" / "index.html"
        if html_file.exists():
            return html_file.read_text()
        return "<h1>Template not found</h1>"
    
    async def get_config_handler(self):
        """Get configuration (masked secret)"""
        config = load_config()
        safe_config = config.copy()
        if safe_config["client_secret"]:
            safe_config["client_secret"] = "••••••••"
        return safe_config
    
    async def update_config_handler(self, config: Config):
        """Update configuration"""
        current_config = load_config()
        
        # Update only provided fields
        if config.client_id:
            current_config["client_id"] = config.client_id
        if config.client_secret and config.client_secret != "••••••••":
            current_config["client_secret"] = config.client_secret
        if config.redirect_uri:
            current_config["redirect_uri"] = config.redirect_uri
        if config.port:
            current_config["port"] = config.port
        if config.host:
            current_config["host"] = config.host
        
        save_config(current_config)
        return {"success": True}

    async def get_setup_status_handler(self):
        """Check if credentials are configured"""
        config = load_config()
        has_credentials = bool(config["client_id"] and config["client_secret"])

        # Check if user is authenticated
        is_authenticated = False
        if has_credentials:
            auth_manager = get_auth_manager()
            if auth_manager:
                token_info = auth_manager.get_cached_token()
                is_authenticated = bool(token_info)

        return {
            "has_credentials": has_credentials,
            "is_authenticated": is_authenticated,
            "needs_setup": not has_credentials,
            "needs_auth": has_credentials and not is_authenticated
        }

    async def setup_credentials_handler(self, setup: SetupRequest):
        """Setup Spotify API credentials via web UI"""
        if not setup.client_id or not setup.client_secret:
            raise HTTPException(status_code=400, detail="client_id and client_secret are required")

        # Load current config and update credentials
        config = load_config()
        config["client_id"] = setup.client_id
        config["client_secret"] = setup.client_secret

        # Save to config file
        save_config(config)

        # Clear cached auth manager so new credentials are used
        global _auth_manager_cache
        _auth_manager_cache = None

        # Delete old token cache since credentials changed
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
            print("🗑️  Cleared old authentication cache")

        print(f"✅ Credentials updated via web UI - client_id: {setup.client_id[:20]}...")

        return {
            "success": True,
            "message": "Credentials saved. Please authenticate with Spotify using /api/auth/url"
        }

    async def get_auth_url_handler(self):
        """Get Spotify authorization URL"""
        auth_manager = get_auth_manager()
        if not auth_manager:
            raise HTTPException(status_code=401, detail="Not configured")

        # Check if already authenticated
        token_info = auth_manager.get_cached_token()
        if token_info:
            return {"authenticated": True, "auth_url": None}

        # Get authorization URL
        auth_url = auth_manager.get_authorize_url()
        return {"authenticated": False, "auth_url": auth_url}

    async def oauth_callback_handler(self, request: Request):
        """Handle Spotify OAuth callback"""
        code = request.query_params.get('code')
        error = request.query_params.get('error')

        if error:
            # Redirect to main page with error message
            error_msg = "access_denied" if error == "access_denied" else "auth_failed"
            return RedirectResponse(url=f"/?error={error_msg}", status_code=302)

        if code:
            try:
                # Exchange code for token
                auth_manager = get_auth_manager()
                if not auth_manager:
                    return RedirectResponse(url="/?error=config_error", status_code=302)

                # Get the full callback URL
                callback_url = str(request.url)
                token_info = auth_manager.get_access_token(code, as_dict=True, check_cache=False)

                if token_info:
                    # Redirect back to main page - success!
                    return RedirectResponse(url="/?success=true", status_code=302)
                else:
                    return RedirectResponse(url="/?error=token_failed", status_code=302)
            except Exception as e:
                print(f"Error during OAuth callback: {e}")
                return RedirectResponse(url="/?error=auth_error", status_code=302)

        return RedirectResponse(url="/?error=no_code", status_code=302)

    async def get_playback_handler(self):
        """Get current playback state"""
        sp = get_spotify_client()
        if not sp:
            raise HTTPException(status_code=401, detail="Not authenticated. Please visit /api/auth/url to get the authorization link.")
        
        try:
            playback = sp.current_playback()
            if not playback:
                raise HTTPException(status_code=404, detail="No active device")
            
            track = playback["item"]
            return {
                "is_playing": playback["is_playing"],
                "track_name": track["name"],
                "artist_name": ", ".join([artist["name"] for artist in track["artists"]]),
                "album_name": track["album"]["name"],
                "album_art": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
                "duration_ms": track["duration_ms"],
                "progress_ms": playback["progress_ms"],
                "volume": playback["device"]["volume_percent"],
                "shuffle": playback["shuffle_state"],
                "repeat": playback["repeat_state"]
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def play_handler(self):
        """Resume playback"""
        sp = get_spotify_client()
        if not sp:
            raise HTTPException(status_code=401, detail="Not configured")
        
        try:
            sp.start_playback()
            return {"success": True}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def pause_handler(self):
        """Pause playback"""
        sp = get_spotify_client()
        if not sp:
            raise HTTPException(status_code=401, detail="Not configured")
        
        try:
            sp.pause_playback()
            return {"success": True}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def next_track_handler(self):
        """Skip to next track"""
        sp = get_spotify_client()
        if not sp:
            raise HTTPException(status_code=401, detail="Not configured")
        
        try:
            sp.next_track()
            return {"success": True}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def previous_track_handler(self):
        """Skip to previous track"""
        sp = get_spotify_client()
        if not sp:
            raise HTTPException(status_code=401, detail="Not configured")
        
        try:
            sp.previous_track()
            return {"success": True}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def set_volume_handler(self, request: VolumeRequest):
        """Set volume"""
        sp = get_spotify_client()
        if not sp:
            raise HTTPException(status_code=401, detail="Not configured")
        
        try:
            sp.volume(request.volume)
            return {"success": True}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def toggle_shuffle_handler(self, request: ShuffleRequest):
        """Toggle shuffle"""
        sp = get_spotify_client()
        if not sp:
            raise HTTPException(status_code=401, detail="Not configured")
        
        try:
            sp.shuffle(request.state)
            return {"success": True}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def set_repeat_handler(self, request: RepeatRequest):
        """Set repeat mode"""
        sp = get_spotify_client()
        if not sp:
            raise HTTPException(status_code=401, detail="Not configured")
        
        try:
            sp.repeat(request.state)
            return {"success": True}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def seek_handler(self, request: SeekRequest):
        """Seek to position in track"""
        sp = get_spotify_client()
        if not sp:
            raise HTTPException(status_code=401, detail="Not configured")
        
        try:
            sp.seek_track(request.position_ms)
            return {"success": True}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    config = load_config()
    print(f"Starting Spotify Controller on http://{config["host"]}:{config["port"]}")
    print(f"Configuration stored in: {CONFIG_FILE}")
    print(f"API docs available at: http://{config["host"]}:{config["port"]}/docs")
    
    controller = SpotifyController()
    
    uvicorn.run(
        controller.app,
        host=config["host"],
        port=config["port"],
        log_level="info"
    )