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
    rank = 'Rang 0: Voyageur Neutre'
    if rep < 0: 
        if rep >= -5:
            rank='Rang -1: Suspect'
        elif rep >= -15:
            rank='Rang -2: Menteur pathologique'
        elif rep >= -25:
            rank='Rang -3: Mage du scepticisme'
        elif rep >= -35:
            rank='Rang -4: Potentiel homosexuel'
        elif rep >= -45:
            rank='Rang -5: Archimage gay-pride'
    else:
        if rep <= 5:
            rank='Rang 1: Observateur'
        elif rep <= 10:
            rank='Rang 2: Chercheur de grâce'
        elif rep <= 15:
            rank='Rang 3: Protecteur des délices'
        elif rep <= 25:
            rank='Rang 4: Paladin des escortes'
        elif rep <= 40:
            rank='Rang 5: Noble défourayeur'
        elif rep <= 60:
            rank='Rang 6: Baron du fion'
        elif rep <= 80:
            rank='Rang 7: Pineur traditionnel'
        elif rep <= 115:
            rank='Rang 8: Seigneur du baisodrôme'
    return rank