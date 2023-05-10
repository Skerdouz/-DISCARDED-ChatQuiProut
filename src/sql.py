import sqlite3

def create_connection():
    conn = sqlite3.connect('user_counts.db')
    return conn

    
def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_counts
                    (user_id INTEGER PRIMARY KEY,
                    oui_count INTEGER NOT NULL,
                    non_count INTEGER NOT NULL,
                    rep INTEGER NOT NULL)''') 
    conn.commit()

def update_user_count(conn, user_id, oui, non, rep):
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO user_counts (user_id, oui_count, non_count, rep) VALUES (?, 0, 0, 0)', (user_id,))
    cursor.execute('UPDATE user_counts SET oui_count = oui_count + ?, non_count = non_count + ?, rep = rep + ? WHERE user_id = ?', (oui, non, rep, user_id))
    conn.commit()

def get_user_count(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('SELECT oui_count, non_count, rep FROM user_counts WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    return result if result else (0, 0, 0)

def get_leaderboard(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, oui_count, non_count, rep FROM user_counts ORDER BY rep DESC')
    result = cursor.fetchall()
    return result

def get_rank(rep):
    rank = 'Voyageur neutre'
    if rep < 0: 
        if rep >= -5:
            rank='Suspect'
        elif rep >= -15:
            rank='Menteur pathologique'
        elif rep >= -25:
            rank='Mage du scepticisme'
        elif rep >= -35:
            rank='Potentiel homosexuel'
        elif rep >= -55:
            rank='Archimage gay-pride'
        elif rep < -55:
            rank='Asexuel affirmé'
    else:
        if rep <= 5:
            rank='Observateur'
        elif rep <= 10:
            rank='Chercheur de grâce'
        elif rep <= 25:
            rank='Protecteur des délices'
        elif rep <= 50:
            rank='Paladin des escortes'
        elif rep <= 90:
            rank='Noble défourayeur'
        elif rep <= 150:
            rank='Baron du fion'
        elif rep <= 250:
            rank='Pineur traditionnel'
        elif rep <= 350:
            rank='Seigneur du baisodrôme'
        elif rep <= 500:
            rank='Bête affamée'
        elif rep > 500:
            rank='Détraqué sexuel'
    return rank