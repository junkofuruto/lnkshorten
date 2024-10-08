import dotenv, os, time

dotenv.load_dotenv()

TOKEN: str = os.getenv("TOKEN")
MYSQL_P: str = os.getenv("MYSQL_P")
MYSQL_U: str = os.getenv("MYSQL_U")
LOG_FILE: str = f"log-{int(time.time() * 1000)}.log"