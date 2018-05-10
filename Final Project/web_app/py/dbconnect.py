import MySQLdb

def connection():
    conn = MySQLdb.connect(host="jl4939.mysql.pythonanywhere-services.com", user="jl4939", passwd="apma4990", db="jl4939$apma4990")
    c = conn.cursor()

    return c, conn