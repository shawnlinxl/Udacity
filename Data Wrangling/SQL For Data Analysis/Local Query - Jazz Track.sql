SELECT COUNT(DISTINCT Customer.CustomerId)
  FROM Customer JOIN Invoice
    ON Customer.CustomerId = Invoice.CustomerId
  JOIN InvoiceLine
    ON Invoice.InvoiceId = InvoiceLine.InvoiceId
  JOIN Track 
    ON InvoiceLine.TrackId = Track.TrackId
  JOIN Genre
    ON Track.GenreID = Genre.GenreID
 WHERE Genre.Name = 'Jazz';