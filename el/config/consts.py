LOG_FILE: str = ".el_execution_log.db"

HISTORY_RECORDS_LIMIT: int = 10
MIN_MEMORY_IMPORTANCE: int = 2
LLM_MODEL: str = "llama3.1"
BASE_URL: str = "http://localhost:11434"
LLM_TIMEOUT: int = 60 * 60

ALLOWED_COMMANDS = {
    "ls",
    "cat",
    "pwd",
    "whoami",
    "hostname",
    "ss",
    "ip",
    "ifconfig",
    "iwconfig",
    "date",
    "time",
    "free",
    "df",
}

DESTRUCTIVE_COMMANDS = {
    "rm",
    "shutdown",
    "reboot",
    "kill",
    "pkill",
    "dd",
}
