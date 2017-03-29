SELECT Genre.Name, count(*) as num
  FROM Genre JOIN Track
    ON Track.GenreID = Genre.GenreID,
      (SELECT avg(Milliseconds) as avgtime
      	 FROM Track
      ) AS Squery
 WHERE Track.Milliseconds < avgtime
 GROUP BY Genre.Name
 ORDER BY num DESC;