SELECT count(*) AS total
  FROM Track JOIN MediaType
    ON Track.MediaTypeID = MediaType.MediaTypeID
  JOIN Genre
    ON Track.GenreID = Genre.GenreID
 WHERE Genre.Name = 'Pop'
   AND MediaType.Name = 'MPEG audio file';