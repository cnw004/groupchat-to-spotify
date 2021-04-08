import sqlite3
from typing import Generator, List
from utils import print_length

class ChatDb:

  def __init__(self, connection_path: str):
    connection = sqlite3.connect(connection_path)
    self.cursor = connection.cursor()

  def _get_attachments_from_chat(self, chat_id: str) -> Generator[str, None, None]:
    for row in self.cursor.execute(
        f'''
            SELECT datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime")
            AS message_date, message.text, message.cache_has_attachments
            FROM chat join chat_message_join ON chat."ROWID"=chat_message_join.chat_id
            JOIN message on chat_message_join.message_id=message."ROWID" WHERE chat_identifier="{chat_id}"
            AND cache_has_attachments=1
            ORDER BY message_date DESC;
          '''
        ):
      yield row

  @print_length(message="links from chat db")
  def get_all_links_from_chat(self, chat_id: str, str_filter: str = "") -> List[str]:
    return [link for _, link, _ in self._get_attachments_from_chat(chat_id)
        if link and str_filter in link
    ]
