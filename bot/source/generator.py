import re, random, hashlib, config, sys
import mysql.connector

conn = mysql.connector.connect(
  host="127.0.0.1",
  user=config.MYSQL_U,
  password=config.MYSQL_P,
  db="lnkshortyfy"
)

def __sha256_checksum(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def __save(url: str, user_id: str) -> str | None:
    id = str(random.randint(0, sys.maxsize))
    path = __sha256_checksum(id)[:5]
    cur = conn.cursor()
    cur.execute("INSERT INTO link (path, user_id, url) VALUES (%s, %s, %s)", (path, user_id, url))
    conn.commit()
    cur.close()

    return path if cur.rowcount == 1 else None

def generate_url(url: str, user_id: int) -> tuple[str, None] | tuple[None, Exception]:
    if re.match(r"(^$|(http(s)?:\/\/)([\w-]+\.)+[\w-]+([\w ;,.\/?%&=]*))", url) == None:
        return None, Exception("Invalid URL format")
    if (path := __save(url, user_id)) == None:
        return None, Exception("Unable to save URL")
    return f"https://cnstrct.ru/{path}", None