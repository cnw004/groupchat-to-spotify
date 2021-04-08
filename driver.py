
from db import ChatDb
from spotify import SpotifyClient

DB_PATH = "/Users/whitguy/Library/Messages/chat.db"
TYVEK_GANG_CHAT_ID = "chat76159326338185108"
SPOTIFY = "spotify"
PLAYLIST_NAME = "tyvek gang"
CLIENT_SCOPE = "playlist-modify-private, playlist-read-private, playlist-modify-public"

def main():
  # initialize clients
  chat_db = ChatDb(DB_PATH)
  spotify_client = SpotifyClient(CLIENT_SCOPE)

  # get links from chat
  links = chat_db.get_all_links_from_chat(TYVEK_GANG_CHAT_ID, str_filter=SPOTIFY)

  # get playlist_id
  playlist_id = spotify_client.get_playlist_id_by_name(PLAYLIST_NAME)

  # add songs to playlist
  spotify_client.add_items_to_playlist(playlist_id, links)

if __name__ == "__main__":
  main()
