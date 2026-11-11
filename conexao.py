import psycopg2

def conectar():
    return psycopg2.connect(
        host="localhost",
        dbname="projetoi",
        port=5432,
        user="postgres",
        password="123456",
    )