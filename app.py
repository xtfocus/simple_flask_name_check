import logging
from flask import Flask, render_template, request
import sqlite3
from datetime import datetime

app = Flask(__name__)
#app.logger = logging.getapp.logger(__name__)

# SQLite database configuration
DATABASE = 'mydatabase.db'

def get_tables():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return tables

def fetch_synonyms(uni_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Fetch synonyms using the uni_id by first filtering mapping_table, then joining with synonym_table
    cursor.execute("""
    SELECT st.synonym_text, mt.editor, mt.created_time
    FROM (SELECT synonym_text, uni_id, editor, created_time FROM mapping_table WHERE uni_id = ?) mt
    JOIN synonym_table st
    ON mt.synonym_text = st.synonym_text
    """, (uni_id,))

    synonyms_result = cursor.fetchall()
    app.logger.info(f"uni_id={uni_id} have synonyms:\n{synonyms_result}")
    conn.close()
    return synonyms_result if synonyms_result else None


def fetch_university_details(uni_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Fetch true university details
    cursor.execute("""
        SELECT uni_id, real_name
        FROM university_table
        WHERE uni_id = ?
    """, (uni_id,))
    true_record = cursor.fetchone()

    # Fetch synonyms using the uni_id
    synonyms_record = fetch_synonyms(uni_id)

    conn.close()


    result = {'true_record': true_record, 'synonym_record': synonyms_record}

    app.logger.info(f"Returning \n\t{result}")

    return result

def search_university_by_name(search_term):

    return_dict = {"search_term": search_term}

    app.logger.info("Start searching")


    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Search directly in university_table, column real_name
    cursor.execute("""
        SELECT uni_id
        FROM university_table
        WHERE real_name = ?
    """, (search_term,))
    uni_id_result = cursor.fetchone()

    if uni_id_result:
        app.logger.info(f"search univesity_table returns {uni_id_result}")
        # A match found in university_table, retrieve the details
        return_dict.update(fetch_university_details(uni_id_result[0]))
        return return_dict
    else:
        app.logger.info(f"search univesity_table returns nothing")

    # If no match found in university_table, search in synonym_table
    cursor.execute("""
        SELECT uni_id
        FROM mapping_table
        WHERE synonym_text = ?
    """, (search_term,))
    uni_id_result = cursor.fetchone()

    if uni_id_result:
        # A match found in synonym_table, use the mapping table to retrieve details
        app.logger.info(f"search mapping_table returns {uni_id_result}")
        return_dict.update(fetch_university_details(uni_id_result[0]))
        return return_dict
    else:
        app.logger.info(f"search mapping_table returns nothing")


    conn.close()

    app.logger.info("Found nothing")
    # No match found
    return_dict.update({'true_record': None, 'synonym_record': None})
    return return_dict


def render_result_template(search_result):
    # Added the 'search_term' to pass to the template
    return render_template('search_result.html', search_result=search_result, search_term=search_result.get('search_term', ''))

@app.route('/')
def index():
    tables = get_tables()
    return render_template('index.html', tables=tables)

@app.route('/search_university_by_name', methods=['GET', 'POST'])
def search():
    app.logger.info("search now")
    if request.method == 'POST':
        university_name = request.form['university_name']
        search_result = search_university_by_name(university_name)
        app.logger.info(f"Search result: {search_result}")
        return render_result_template(search_result)

    return render_template('search_form.html')

if __name__ == '__main__':
    app.run(debug=True)

