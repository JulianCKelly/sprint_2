'''imports for postgress'''
import sqlite3
import pymongo


PASSWORD = '8252804Jk'
DBNAME = 'cluster0'


def create_mdb_connection(password, dbname):
    client = pymongo.MongoClient(f'''mongodb+srv://juliancharlankelly:{password}@cluster0.zdpcogn.mongodb.net/{dbname}?retryWrites=true&w=majority''')
    return client


def create_sl_connection(dbname='rpg_db.sqlite3'):
    sl_conn = sqlite3.connect(dbname)
    return sl_conn


def execute_query(curs, query):
    return curs.execute(query).fetchall()


def doc_creation(db, sl_curs, character_table_query, item_table_query, weapon_table_query):
    weapons = execute_query(sl_curs, weapon_table_query)
    characters = execute_query(sl_curs, character_table_query)
    for character in characters:
        item_character_query = item_table_query.format("\'%s\'" % character[1])
        item_names = execute_query(sl_curs, item_character_query)
        weapon_names = []
        for item in item_names:
            if item in weapons:
                weapon_names.append(item[0])

        document = {
            'name': character[1],
            'level': character[2],
            'exp': character[3],
            'hp': character[4],
            'strength': character[5],
            'intelligence': character[6],
            'dexterity': character[7],
            'wisdom': character[8],
            'items': item_names,
            'weapons': weapon_names
        }
        db.insert_one(document)


def show_all(db):
    all_docs = list(db.find())
    return all_docs


GET_CHARACTER_TABLE = '''
    SELECT  * FROM charactercreator_character
'''

GET_ITEM_TABLE = '''
    SELECT ai.name AS item_name
    FROM (SELECT *
    FROM charactercreator_character AS cc_char
    INNER JOIN charactercreator_character_inventory AS cc_ci
    WHERE cc_char.character_id = cc_ci.character_id) AS char_ci
    INNER JOIN armory_item AS ai
    WHER Eai.item_id = char_ci.item_id
    AND char_ci.name = {};
'''

GET_WEAPON_TABLE = '''
    SELECT aw_ai.name
    FROM (SELECT *
    FROM armory_item AS ai
    INNER JOIN armory_weapon AS aw
    WHERE ai.item_id = aw.item_ptr_id) AS aw_ai
    INNER JOIN (SELECT *
    FROM charactercreator_character AS cc_char
    INNER JOIN charactercreator_character_inventory AS cc_ci
    WHERE cc_char.character_id = cc_ci.character_id) AS char_ci
    WHERE aw_ai.item_id = char_ci.item_id;
'''


if __name__ == '__main__':
    sl_conn = create_sl_connection()
    sl_curs = sl_conn.cursor()
    client = create_mdb_connection(PASSWORD, DBNAME)

    # connect to the collection that we want to add the documents to
    db = client.rpg_data
    col = db['rpg_data']
    # drop anythign that is already in colection
    col.drop({})
    doc_creation(col, sl_curs, GET_CHARACTER_TABLE, GET_ITEM_TABLE,
                 GET_WEAPON_TABLE)

    print(show_all(col))
