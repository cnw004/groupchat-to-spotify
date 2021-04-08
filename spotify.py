import os
import spotipy
from config import Config
from spotipy.oauth2 import SpotifyOAuth
from typing import List
from utils import print_length

PAGING_LIMIT = 100
URL_PARAMS_SEPARATOR = "?"
URL_PREFIX = "http"
SLASH = "/"
COLON = ":"
SPOTIPY_CONFIG_SECTION = "spotipy"

class SpotifyClient:

  def __init__(self, scope: str):
    self._set_env_vars()
    self.connection = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

  def _set_env_vars(self):
    config = Config()
    for key, value in config.parser[SPOTIPY_CONFIG_SECTION].items():
      os.environ[key.upper()] = value

  def get_playlist_id_by_name(self, playlist_name: str) -> str:
    """
      Gets all playlist IDs for current user by fuzzy matching on playlist name 
    """
    filtered_playlist_ids = []
    offset = 0
    while True:
      response = self.connection.current_user_playlists(offset=offset)
      next_uri, all_playlists = response.get("next"), response.get("items")
      filtered_playlist_ids.extend([
          playlist.get("id") for playlist in all_playlists
          if playlist_name in playlist.get("name")
      ])
      if not next_uri:
        break
      offset += PAGING_LIMIT

    if len(filtered_playlist_ids) > 1:
      raise MoreThanOneMatchException(f"Expected 1 playlist but found {len(filtered_playlist_ids)}")
    if not filtered_playlist_ids:
      raise NoPlaylistFoundException

    return filtered_playlist_ids[0]

  @print_length(message="item ids currently on playlist")
  def get_item_ids_on_playlist(self, playlist_id: str, limit: int = PAGING_LIMIT) -> List[str]:
    """
      Gets all the item IDs on the given playlist
    """
    item_ids = []
    offset = 0
    while True:
      response = self.connection.playlist_items(playlist_id, offset=offset)
      next_uri, playlist_items = response.get("next"), response.get("items")
      item_ids.extend([item.get("track").get("id") for item in playlist_items])
      if not next_uri:
        break
      offset += PAGING_LIMIT
    return item_ids

  @print_length("songs being added to playlist")
  def add_items_to_playlist(self, playlist_id: str, items_to_add: List[str], should_filter=True) -> List[str]:
    """
      adds items to the playlist
      items can be in the form of URIs or IDs
      if should_filter is set to False then we won't check what songs are on the playlist before adding
    """
    if should_filter:
      items_to_add = list(set(self._sanitize_items(items_to_add)) - set(self.get_item_ids_on_playlist(playlist_id)))
    while True and items_to_add:
      self.connection.playlist_add_items(playlist_id, items_to_add[:PAGING_LIMIT])
      if len(items_to_add) > PAGING_LIMIT:
        items_to_add = items_to_add[PAGING_LIMIT:]
      else:
        break
    return items_to_add

  def _sanitize_items(self, items: List[str]) -> List[str]:
    """
      Takes a list of playlist items and turns them all into the form of IDs
    """
    sanitized_items = []
    for item in items:
      # http://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6
      if item.startswith(URL_PREFIX):
        if "track" not in item:  # ignore playlists and other types
          continue
        item_to_add = self._sanitize_url_item(item)
      
      # spotify:track:6rqhFgbbKwnb9MLmUQDhG6
      elif item.startswith("spotify"):
        item_to_add = self._sanitize_uri_item(item)

      # 6rqhFgbbKwnb9MLmUQDhG6
      else:
        item_to_add = item
      
      sanitized_items.append(item_to_add)
    return sanitized_items

  def _sanitize_url_item(self, item: str) -> str:
    return item.split(SLASH)[-1].split(URL_PARAMS_SEPARATOR)[0]

  def _sanitize_uri_item(self, item: str) -> str:
    return item.split(COLON)[-1]
        


  
class MoreThanOneMatchException(Exception):
  """
    Exception raised for unclear fuzzy finding
  """
  def __init__(self, message):
    self.message = message

class NoPlaylistFoundException(Exception):
  pass

class EnvironmentException(Exception):
  """
    Exception if necessary env vars aren't set
  """
  def __init__(self, message):
    self.message = message
