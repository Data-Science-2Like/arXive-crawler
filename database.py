import sqlite3

conn = sqlite3.connect('arxiv_metadate.sqlite')

def initDatabase():
    cur = conn.cursor();
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS papers (
    id INTEGER NOT NULL PRIMARY KEY,
    title TEXT,
    url TEXT,
    datetime TEXT
    );
    CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT UNIQUE
    );
    CREATE TABLE IF NOT EXISTS authors (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT UNIQUE
    );
    CREATE TABLE IF NOT EXISTS published (
    paperID INTEGER,
    authorID INTEGER,
    PRIMARY KEY(paperID, authorID)
    FOREIGN KEY (paperID) REFERENCES papers(id)
    FOREIGN KEY (authorID) REFERENCES authors(id)
    );
    CREATE TABLE IF NOT EXISTS tagged (
    paperID INTEGER,
    subjectID INTEGER,
    PRIMARY KEY(paperID, subjectID)
    FOREIGN KEY (paperID) REFERENCES papers(id)
    FOREIGN KEY (subjectID) REFERENCES subjects(id)
    );
    ''')



def insertPaper(identifier, title, authors, subjects, datetime, url):
    cur = conn.cursor()

    # insert paper into database
    cur.execute('''
    INSERT INTO papers (id, title, url, datetime)
    VALUES (?,?,?,?)
    ''',(identifier, title[0], url[0], datetime[-1]))

    authorIds = list()
    for author in authors:
        cur.execute('INSERT OR IGNORE INTO authors (name) VALUES (?)', (author,))

        cur.execute('SELECT id FROM authors WHERE name = ?', (author,))
        authorId = cur.fetchone()[0]
        authorIds.append(authorId)

        cur.execute('INSERT OR IGNORE INTO published VALUES (?,?)', (identifier, authorId))

    subjectIds = list()
    for subject in subjects:
        cur.execute('INSERT OR IGNORE INTO subjects (name) VALUES (?)', (subject,))

        cur.execute('SELECT id FROM subjects WHERE name = ?', (subject,))
        subjectId = cur.fetchone()[0]
        subjectIds.append(subjectId)

        cur.execute('INSERT OR IGNORE INTO tagged VALUES (?,?)',(identifier,subjectId))

    print('inserted record with id ', identifier)

def getPaperUrls(startingId = 0) :

    cur = conn.cursor()
    cur.execute('''SELECT id, title, url, datetime FROM papers WHERE id >= ?''', (startingId,))

    result = cur.fetchall()

    return result

def get_paper_info_from_title(title):
    cur = conn.cursor()
    cur.execute("SELECT id, title FROM papers WHERE title LIKE '%" + title.replace(".","") + "%'")

    result = cur.fetchall()
    return result

def getPaperUrlsByCategory(categories,startingId = 0, stopId = 3000000000):
    cur = conn.cursor()

    # becase python, we first need to convert all ints to str
    converted = [str(element) for element in categories]

    categoriesStr = ",".join(converted)
    cur.execute('''SELECT DISTINCT id, title, url, datetime FROM papers
    INNER JOIN tagged ON papers.id = tagged.paperID
    WHERE papers.id >= ? AND papers.id <= ? AND tagged.subjectID IN(''' + categoriesStr + ')', (startingId, stopId,))
    # we need to add the categories string manually because passing it as a parameter doesn't work somehow


    result = cur.fetchall()

    return result

def getPaperCountsPerYearByCateogry(categories):
    cur = conn.cursor()

    # becase python, we first need to convert all ints to str
    converted = [str(element) for element in categories]

    categoriesStr = ",".join(converted)
    cur.execute('''SELECT DISTINCT COUNT(*) , strftime('%Y',datetime) AS year FROM papers
       INNER JOIN tagged ON papers.id = tagged.paperID
       WHERE tagged.subjectID IN(''' + categoriesStr + ') GROUP BY year')
    # we need to add the categories string manually because passing it as a parameter doesn't work somehow

    result = cur.fetchall()

    return result

def getYearOfPaper(id):
    cur = conn.cursor()
    cur.execute('''SELECT strftime('%Y',datetime) FROM papers WHERE id = ?''', (id,))
    return cur.fetchone()[0]


def commit():
    conn.commit()