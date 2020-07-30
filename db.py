import mysql
import mysql.connector
from mysql.connector import errorcode

def dbh(query,type,*params):
	#print(query,type,*params)
	try:
		cnx = mysql.connector.connect(
			user='root', 
			password='root',
	        host='127.0.0.1',
	        database='wildberries')
		if type == "query":
			cursor = cnx.cursor(dictionary=True, buffered=True)
			cursor.execute(query,(params))
			#print("DB:select")
			result = []
			for row in cursor:
				result.append(row)
			cursor.close()
			cnx.close()
			return result
		elif type == "do":
			cursor = cnx.cursor(buffered=True)
			cursor.execute(query,(params))
			#print("DB:do")
			cnx.commit()
			cursor.close()
			cnx.close()
			return cursor
	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("Something is wrong with your user name or password")
		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			print("Database does not exist")
		else:
			print(err)
	else:
		cnx.close()
