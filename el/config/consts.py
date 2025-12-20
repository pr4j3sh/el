LOG_FILE: str = ".el_execution_log.db"

HISTORY_RECORDS_LIMIT: int = 10
MIN_MEMORY_IMPORTANCE: int = 2
LLM_MODEL: str = "llama3.2"
LLM_TIMEOUT: int = 60

ALLOWED_COMMANDS = {
    "ls",
    "cat",
    "pwd",
    "whoami",
    "ss",
    "ip",
    "ifconfig",
    "iwconfig",
    "date",
    "time",
}

DESTRUCTIVE_COMMANDS = {
    "rm",
    "shutdown",
    "reboot",
    "kill",
    "pkill",
    "dd",
}
