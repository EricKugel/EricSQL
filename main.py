import os
from pathlib import Path

from logic.database import Database

import logic.parser
import logic.query

import logic.table

from server import server

cwd = Path.cwd()


databases = [file for file in cwd.iterdir() if file.is_file() and os.path.basename(file).endswith("db")]

if not databases:
    print("No databases found. Create now? (Y/n)")
    response = input()
    if "n" in response or "N" in response:
        print("Exiting")
        quit()
    else:
        print("Input the database name.")
        response = input().strip()
        db_file = Path(f"{response}.db")
        db_file.touch()
else:
    db_file = databases[0]

# """SELECT * From Customers ORDER BY City ASC CustomerID DESC"""
def handle_query(query_string):
    results = []
    for query in logic.query.create_queries(logic.parser.tokenize(query_string), db):
        result = query.execute()
        if not isinstance(result, logic.table.Table):
            results.append("Success")
        else:
            results.append(result.data.values.tolist())
    return results

db = Database(db_file)
print("Starting database " + db.name)
app = server.init(handle_query)

if __name__ == "__main__":
    app.run(host=server.HOST, port=server.PORT)

db.write_out()