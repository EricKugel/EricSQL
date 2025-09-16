# EricSQL
(Pronounced "E-Squirrel")

EricSQL is an implementation of SQL. Eventually it will cover every typical statement; it's functional right now but still missing unions and GROUP BY. I'm learning a lot both about SQL and web security with this project (I've already accidentally sql-injected myself once).

### View Demo Website
You can see a working message board, written in Next.js with EricSQL, at [ericsql.erickugel.com](https://ericsql.erickugel.com). I'm running EricSQL on a GCP VM.

### About EricSQL
EricSQL has two main parts: The EricSQL server and EricSQL Engine. Features include:

Engine
 - Support for SELECT, SELECT DISTINCT, ORDER BY, WHERE, DELETE, INSERT INTO (and more coming soon...)
 - Expression parsing
 - Aggregate functions
 - Aliasing

Server
 - A rest API using python Flask

Here's some interesting queries EricSQL can handle:
```
SELECT COUNT(*) FROM (SELECT DISTINCT Name FROM PRODUCTS)

SELECT 2 * Price as DoublePrice, Quantity FROM Products

SELECT 2 * SUM(2 * Price) as QuadruplePrice from Products

SELECT Price FROM Products WHERE Quantity >= 2 ORDER BY Price ASC Quantity DESC
```


### Start instructions:
To start an EricSQL server with the starter database, run
`gunicorn main:app`.
