-- Create the university_table
CREATE TABLE university_table (
        uni_id TEXT PRIMARY KEY,
        real_name TEXT
            
);

-- Create the synonym_table
CREATE TABLE synonym_table (
        synonym_text TEXT PRIMARY KEY,
        language TEXT
            
);

-- Create the mapping_table with composite key and additional attributes
CREATE TABLE mapping_table (
        uni_id TEXT,
        synonym_text TEXT,
        editor TEXT,
        created_time TEXT,
        PRIMARY KEY (uni_id, synonym_text)
                                
);

