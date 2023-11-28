
#!/bin/bash

sqlite3 mydatabase.db < create_table.sql && sqlite3 mydatabase.db < insert_data.sql && sqlite3 mydatabase.db < insert_mapping_data.sql
