import string
import sqlite3

#table creation function
def create_table():
	con = sqlite3.connect("chat_history.db")
	cur = con.cursor()
	cur.execute("CREATE TABLE chat_history(userid, request, response)")

	con.commit()
	con.close()

#insert function
def save_chat_history(userid:int, request:string, response:string):
	con = sqlite3.connect('chat_history.db')
	cur = con.cursor()
	cur.execute('INSERT INTO chat_history(userid, request, response) VALUES (?, ?, ?)', (userid, request, response))

	con.commit()
	con.close()


if __name__ == '__main__':
	create_table()
	save_chat_history(1,'a', 'a')

	con = sqlite3.connect("chat_history.db")
	cur = con.cursor()
	for row in cur.execute('SELECT * FROM chat_history'):
		print(row)
	con.close()


