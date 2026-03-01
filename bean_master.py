import sqlite3
from bottle import post,get,request,route,run,template

@route('/blist/bean')
def init():
    drop_tb = 'DROP TABLE IF EXISTS bean_master'
    create_tb = 'CREATE TABLE bean_master(' + \
    'bean_id INTEGER PRIMARY KEY AUTOINCREMENT,' + \
    'bean_name VARCHAR(30) NOT NULL,' + \
    'acidity INTEGER,' + \
    'bitterness INTEGER,' + \
    'body INTEGER,' + \
    'aroma INTEGER' + \
    ')'


    con = sqlite3.connect('bean_master.db')
    cur = con.cursor()
    cur.execute(drop_tb)
    cur.execute(create_tb)


    beans = [
    ('クリスタルマウンテン',  # bean_name
    5,       # acidity　酸味
    5,       # bitterness　苦味
    5,       # body　コク
    4        # aroma　香り
    ),
    ('ベネズエラ', 2, 5, 3, 2),
    ('コナ', 5, 4, 4, 5),
    ('ブルーマウンテン', 5, 4, 5, 5),
    ('ケニア', 4, 4, 2, 3),
    ('キリマンジャロ', 5, 3, 2, 4),
    ('エメラルドマウンテン', 4, 3, 5, 5),
    ('ジャワ', 1, 3, 4, 4),
    ('コロンビア', 2, 3, 4, 4),
    ('トラジャ', 2, 3, 5, 3),
    ('コスタリカ', 4, 2, 3, 4),
    ('モカ', 2, 3, 3, 4),
    ('サントス', 2, 1, 2, 3),
    ('グアマテラ', 4, 2, 2, 5),
    ('キューバ', 3, 2, 1, 3),
    ('メキシコ', 2, 1, 1, 2),
    ('マンデリン', 1, 1, 3, 2)
    ]

    for bean in beans:
        insert_user_beans(cur, * bean)


    con.commit()
    blist=select_all(cur)
    con.close()

    if len(blist)>0:
        tplt = """
        <p>テーブルbean_masterを作成しました</p>
        <p>
        %for cell in blist:
        {{cell}},
        %end
        </p>
        """
        return template(tplt,blist=blist)

    return('初期化操作失敗')

def insert_user_beans(cur, bean_name, acidity, bitterness, body, aroma):
    insert_str = 'INSERT INTO bean_master(' + \
        'bean_name, acidity, bitterness, body, aroma' + \
        ') VALUES (?,?,?,?,?)'

    cur.execute(insert_str, (
        bean_name, acidity, bitterness, body, aroma
    
    ))

    
def select_all(cur):
    select_str = 'SELECT * FROM bean_master'
    cur.execute(select_str)
    return cur.fetchall()



run(host='localhost',port=8782,reloader=True)