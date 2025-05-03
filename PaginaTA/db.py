import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        host="nozomi.proxy.rlwy.net",
        database="railway",
        user="postgres",
        password="EeXrqIxEarrSNiJRwyrfgNwONgKqHMWx",
        port=53046
    )
    return conn
