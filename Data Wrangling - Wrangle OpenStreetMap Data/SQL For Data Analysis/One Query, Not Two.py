# Find the players whose weight is less than the average.
# 
# The function below performs two database queries in order to find the right players.
# Refactor this code so that it performs only one query.
#

def lightweights(cursor):
    """Returns a list of the players in the db whose weight is less than the average."""
    query = '''
	SELECT name, weight
	  FROM players,
	  	   (SELECT avg(weight) as av
	  		  FROM players
	  		) AS avg_weight
	 WHERE players.weight < av

    '''
    cursor.execute(query)

    return cursor.fetchall()