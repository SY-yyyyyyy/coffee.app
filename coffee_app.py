import sqlite3
import requests
import os
#APIキー
GOOGLE_API_KEY ="****GOOGLE_API_KEY*****"
from bottle import post,get,request,route,run,template,TEMPLATE_PATH,redirect,response,static_file

 #HTMLファイルにつなぐ
TEMPLATE_PATH.append(r"C:\Users\yyyuu\views")
 #CSSファイルにつなぐ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@route('/look/<filename>')
def server_static(filename):
    return static_file(
        filename,
        root=r'C:\Users\yyyuu\views\look'
    )


def get_login_user_id():
    user_id = request.get_cookie('user_id', secret='secret-key')
    if not user_id:
        redirect('/blist/login')
    return int(user_id)



#ホーム画面
@route('/home')
def home():
    user_id = get_login_user_id()

    con = sqlite3.connect('coffee.db')
    cur = con.cursor()

    # タイトルとして使う豆の名前を取得
    cur.execute(
    'SELECT bean_id, title_name FROM user_beans WHERE user_id = ?',
    (user_id,)
)
    beans = cur.fetchall()

    cur.execute(
    'SELECT user_name FROM users_data WHERE user_id = ?',
    (user_id,)
) 
    user_names = cur.fetchone()

    con.close()

    return template('upload_coffee_home', beans=beans,user_id=user_id,user_name=user_names)

#ログイン
@route('/blist/login', method=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.forms.getunicode('user_name')
        password = request.forms.getunicode('password')

        con = sqlite3.connect('coffee.db')
        cur = con.cursor()
        cur.execute(
            'SELECT user_id, password FROM users_data WHERE user_name = ?',
            (user_name,)
        )
        row = cur.fetchone()
        con.close()

        if row and row[1] == password:
            response.set_cookie(
                'user_id',
                str(row[0]),
                secret='secret-key',
                path='/'
            )
            return redirect('/home')

        return template('upload_coffee_login',
                            error='ユーザー名またはパスワードが違います')

    return template('upload_coffee_login')

# 新規ユーザー登録
@route('/blist/sign_in', method=['GET', 'POST'])
def register():
    # 登録ボタンが押されたとき (POST)
    if request.method == 'POST':
        new_user = request.forms.getunicode('user_name')
        new_pass = request.forms.getunicode('password')

        # 空欄チェック
        if not new_user or not new_pass:
            return 'ユーザー名とパスワードを入力してください。<a href="/blist/register">戻る</a>'

        con = sqlite3.connect('coffee.db')
        cur = con.cursor()

        # すでに存在するかチェック
        cur.execute('SELECT * FROM users_data WHERE user_name = ?', (new_user,))
        existing = cur.fetchone()

        if existing:
            con.close()
            return template('upload_coffee_signin',
                            error='そのユーザー名はすでに使われています')
        

        # データを保存 (INSERT)
        cur.execute('INSERT INTO users_data (user_name, password) VALUES (?, ?)', (new_user, new_pass))
        con.commit() # 変更を確定する重要コマンド
        con.close()

        return template('upload_coffee_signin2')

        

    # 登録画面を表示 (GET)
    return template('upload_coffee_signin')

#データの挿入(input)
@route('/blist/init')
def init():
    con = sqlite3.connect('coffee.db')
    cur = con.cursor()
    #テーブル削除
    cur.execute('DROP TABLE IF EXISTS user_beans')
    cur.execute('DROP TABLE IF EXISTS user_shops')
    cur.execute('DROP TABLE IF EXISTS users_data')

    #users_data 作成
    cur.execute(
        'CREATE TABLE users_data ('
        'user_id INTEGER PRIMARY KEY AUTOINCREMENT,'
        'user_name TEXT UNIQUE NOT NULL,'
        'password TEXT NOT NULL'
        ')'
)

    #user_shops 作成
    cur.execute(
    'CREATE TABLE user_shops ('
    'store_id INTEGER PRIMARY KEY AUTOINCREMENT,'   # store_id：店舗ID（自動採番）
    'place_id TEXT UNIQUE NOT NULL,' #place_id：Google Places API が発行する店舗固有ID、UNIQUE にすることで「同じ店の重複登録」を防ぐ
    'store_name TEXT NOT NULL,' #store_name：店舗名
    'address TEXT NOT NULL,'  # address：店舗の住所
    'latitude REAL NOT NULL,' # latitude：緯度
    'longitude REAL NOT NULL,' # longitude：経度（
    'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP' # created_at：登録日時
    ')'
    )

    #user_beans 作成
    cur.execute(
        'CREATE TABLE user_beans('
        'bean_id INTEGER PRIMARY KEY AUTOINCREMENT,'
        'user_id INTEGER NOT NULL,'
        'title_name VARCHAR(30) NOT NULL,'
        'bean_name VARCHAR(30) NOT NULL,'
        'roast_level INTEGER,'
        'acidity INTEGER,'
        'bitterness INTEGER,'
        'richness INTEGER,'
        'aroma INTEGER,'
        'purchase_date DATE,'
        'price INTEGER,'
        'amount INTEGER,'
        'comment TEXT,'
        'image_url TEXT,'
        'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,'
        'updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,'
        'store_id INTEGER,'
        'FOREIGN KEY (store_id) REFERENCES user_shops(store_id)'
    ')'
    )

    #ユーザーデータ
    cur.execute(
    'INSERT INTO users_data (user_name, password) VALUES (?, ?)',
    ('aaa', 'pass1')
    )

    #店舗データ
    cur.execute(
        '''
        INSERT INTO user_shops
        (place_id, store_name, address, latitude, longitude)
        VALUES (?, ?, ?, ?, ?)
        ''',
        (
            'id_001',
            'カルディ 仙台店',
            '宮城県仙台市青葉区中央1-1-1',
            38.2600,
            140.8800
        )
    )

    # store_id を取得
    cur.execute("SELECT store_id FROM user_shops WHERE place_id = ?", ('id_001',))
    store_id = cur.fetchone()[0]

    

    #豆データ
    cur.execute("""
    INSERT INTO user_beans
    (user_id, title_name, bean_name, roast_level, acidity, bitterness, richness, aroma,
    purchase_date, price, amount, comment, image_url, store_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,(
        1,                      # 1:user_id
        'おすすめ',              # 2:title_name
        'もか',                  # 3:bean_name
        3,                      # 4:roast_level（中煎り）
        3,                      # 5:acidity
        2,                      # 6:bitterness
        4,                      # 7:richness
        4,                      # 8:aroma
        '2025-11-20',           # 9:purchase_date
        1200,                   # 10:price
        200,                    # 11:amount (g)
        'アイスコーヒーに使いやすく、香りが良い。',  # 12:comment
        'https://example.com/image.jpg' , # 13:image_url
        store_id                # 14:store_id
    ))

    con.commit()
    blist=select_all(cur)
    blist_s = select_all_shops(cur)
    con.close()

    if len(blist)>0:
        tplt = """
        <p>テーブルuser_beans,user_shopsを作成しました</p>
       <p>豆情報:</p>
        %for cell in blist[-1]:
            {{cell}},
        %end
        <p>店舗情報:</p>
        %for cell in blist_s[-1]:
            {{cell}},
        %end
        """
        return template(tplt,blist=blist,blist_s=blist_s)

    return('初期化操作失敗')

def insert_user_beans(cur, user_id, title_name, bean_name, roast_level, acidity, bitterness, richness, aroma,
                store_id, purchase_date, price, amount, comment, image_url):

    insert_str = 'INSERT INTO user_beans(' + \
        'user_id, title_name, bean_name, roast_level, acidity, bitterness, richness, aroma,' + \
        'store_id,purchase_date, price, amount, comment, image_url' + \
        ') VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'

    cur.execute(insert_str, (
        user_id, title_name,  bean_name, roast_level, acidity, bitterness, richness, aroma,
        store_id, purchase_date, price, amount, comment, image_url
    ))
    
def select_all(cur):
    select_str = 'SELECT * FROM user_beans'
    cur.execute(select_str)
    return cur.fetchall()

def select_all_shops(cur):
    cur.execute('SELECT * FROM user_shops')
    return cur.fetchall()

def get_lat_lng(address):
    """住所から緯度経度を取得"""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_API_KEY}
    resp = requests.get(url, params=params)
    data = resp.json()
    if data["status"] == "OK":
        loc = data["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]
    else:
        return None, None
    
@get('/blist/new')
def new():
    get_login_user_id() # ログインチェック
    try:
        return template('upload_coffee_input')
    except:
         return "テンプレート 'upload_coffee_input' が見つかりません。"

@post('/blist/new')

def aded_newbean():
    con = sqlite3.connect('coffee.db')
    cur = con.cursor()

    # ログインユーザー
    user_id = get_login_user_id()

    #豆
    
    title_name = request.forms.getunicode('title_name')
    bean_name = request.forms.getunicode('bean_name')

    roast_level = int(request.forms.get('roast_level'))
    acidity = int(request.forms.get('acidity'))
    bitterness = int(request.forms.get('bitterness'))
    richness = int(request.forms.get('richness'))
    aroma = int(request.forms.get('aroma'))
    purchase_date = request.forms.getunicode('purchase_date')
    if not purchase_date:
        purchase_date = None
    price = request.forms.get('price')
    amount = request.forms.get('amount')
    comment = request.forms.getunicode('comment')
    image_url = request.forms.getunicode('image_url')

    #店舗
    store_name = request.forms.getunicode('store_name')
    address = request.forms.getunicode('address') 
    lat = request.forms.get('latitude')
    lng = request.forms.get('longitude')

    
    # 緯度経度取得
   
    lat, lng = get_lat_lng(address)
    if lat is None or lng is None:
        lat, lng = 0, 0

    # place_id を生成（店名+住所）
    place_id =  request.forms.getunicode('place_id')

     # 店舗情報
    cur.execute(
    '''
    INSERT INTO user_shops (store_name, address, latitude, longitude,place_id)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(place_id) DO NOTHING
    ''',
    (store_name, address, lat, lng, place_id)
)
    #store_id を取得
    cur.execute("""
    SELECT store_id FROM user_shops WHERE place_id = ?
    """, (place_id,))
    store_id = cur.fetchone()[0]

    # 豆情報
    cur.execute("""
    INSERT INTO user_beans
    (user_id,title_name, bean_name, roast_level, acidity, bitterness, richness, aroma,  purchase_date,price,amount,comment,image_url,store_id)
    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
    user_id,title_name, bean_name,
    roast_level, acidity, bitterness, richness, aroma,  purchase_date,price,amount,comment,image_url,store_id
    ))
    

    con.commit()

     # 登録した豆のIDを取得
    cur.execute('SELECT last_insert_rowid()')
    bean_id = cur.fetchone()[0]

    con.close()

    # 登録した豆の詳細ページへつなげる
    return redirect(f'/detail/{bean_id}')

#内容確認用
    # blist = select_all(cur)
    # blist_s = select_all_shops(cur)
    # con.close()

    # tplt = """
    # <h1>データを保存しました</h1>
    # <p>豆情報:</p>
    # %for cell in blist[-1]:
    #     {{cell}}
    # %end
    # <p>店舗情報:</p>
    # %for cell in blist_s[-1]:
    #     {{cell}}
    # %end
    # """
    # return template(tplt, blist=blist, blist_s=blist_s)

CLMS = [
    ('user_id', 'ユーザーID'),
    ('title_name', 'タイトル'),
    ('bean_name', '豆の名前'),
    ('roast_level', '焙煎度(1〜5)'),
    ('acidity', '酸味(1〜5)'),
    ('bitterness', '苦味(1〜5)'),
    ('richness', 'コク(1〜5)'),
    ('aroma', '香り(1〜5)'),
    ('store_id', '店舗ID'),
    ('store_name', '購入店舗名'),
    ('purchase_date', '購入日'),
    ('price', '価格(円)'),
    ('amount', '購入量(g)'),
    ('comment', 'コメント'),
    ('image_url', '画像URL')
]

def aded_newshop():
    # 店舗情報（Google Places 由来）
    place_id = request.forms.getunicode('place_id')
    store_name = request.forms.getunicode('store_name')
    address = request.forms.getunicode('address')
    lat = float(request.forms.get('latitude'))
    lng = float(request.forms.get('longitude'))

    
    return f"""
    <h2>受信データ確認</h2>
    place_id: {place_id}<br>
    store_name: {store_name}<br>
    address: {address}<br>
    latitude: {latitude}<br>
    longitude: {longitude}<br>
    """

def form_template():
    tplt = """
    %for i in range(len(clms)): 
    <p><label for = '{{clms[i][0]}}'>{{clms[i][1]}}:</label>
    <input type = 'text' id ='{{clms[i][0]}}' name='{{clms[i][0]}}'
    size = '20'></p>
    %end
    <input type='submit' value='GO'>
    """
    return tplt




#詳細表示
@route('/detail/<bean_id>')
def detail(bean_id):
    user_id = get_login_user_id()

    con = sqlite3.connect('coffee.db')
    cur = con.cursor()

    cur.execute(
        'SELECT * FROM user_beans WHERE bean_id = ? AND user_id = ?',
    (bean_id, user_id)
    )
    beans = cur.fetchone() #1件取得
    
    store_id = beans[16] 
    
    cur.execute('SELECT * FROM user_shops WHERE store_id = ?', (store_id,))
    shop = cur.fetchone()


    con.close()
    return template('upload_coffee_view', title='コーヒー豆詳細', bean=beans,shop=shop)

#削除機能
@route('/blist/delete/<bean_id>')
def delete_it(bean_id):
    get_login_user_id() # ログインチェック
    return template('upload_coffee_delete',bean_id=bean_id)

@get('/blist/deleted/<bean_id>')
def deleted(bean_id):
    get_login_user_id() # ログインチェック
    con = sqlite3.connect('coffee.db')
    cur = con.cursor()

    delete_bean(cur,bean_id)
    

    con.commit()
    con.close()
    return template('upload_coffee_delete2')
                    
def delete_bean(cur,bean_id):
    delete_str = 'DELETE FROM user_beans where bean_id=?'
    cur.execute(delete_str,(bean_id,))

#傾向分析
@route('/blist/analysis')

def recommend():
    get_login_user_id() # ログインチェック
    user_id = get_login_user_id()#ログインユーザーのIDを取得
    con = sqlite3.connect('coffee.db')
    cur = con.cursor()
    
    #平均値を出す
    cur.execute("""
    SELECT AVG(roast_level), AVG(acidity), AVG(bitterness), AVG(richness), AVG(aroma) 
    FROM user_beans 
    WHERE user_id = ?
    """, (user_id,))
    avg=cur.fetchone()#一つ取得
    con.close()

    # データが1件もない場合の処理
    if not avg or avg[0] is None:
        return template('upload_coffee_analysis',
                            error='まずは豆を1件以上登録してください！')
        

    con = sqlite3.connect('bean_master.db')
    cur = con.cursor()
    cur.execute("""
        SELECT bean_name, acidity, bitterness, body, aroma
        FROM bean_master
    """)
    beans = cur.fetchall()
    con.close()

#ユークリッド距離で一番近い豆をおすすめする
#距離 = (酸味差)^2 + (苦味差)^2 + (コク差)^2 + (香り差)^2

    best_bean = None
    min_dist = float('inf')

    for bean in beans:
        name, a, b, body, ar = bean
        dist = (
        (a - avg[1]) ** 2 + # 酸味
        (b - avg[2]) ** 2 + # 苦味
        (body - avg[3]) ** 2 + # コク
        (ar - avg[4]) ** 2   # 香り
        )

        if dist < min_dist:
            min_dist = dist
            best_bean = bean

    return template(
        'upload_coffee_analysis',
        avg=avg,
        bean=best_bean,
        distance=round(min_dist, 2)
    )

#マップ表示
@route('/blist/map')
def show_map():
    get_login_user_id() # ログインチェック
    user_id = get_login_user_id()#ログインユーザーのIDを取得
    con = sqlite3.connect('coffee.db')
    cur = con.cursor()

    cur.execute('''
        SELECT DISTINCT s.* FROM user_shops s
        JOIN user_beans b ON s.store_id = b.store_id
        WHERE b.user_id = ?
    ''', (user_id,))
    
    shops = cur.fetchall() 
    con.close()

    return template('upload_coffee_map', shops=shops)


# 店舗ごとの豆リストを表示
@route('/shop_beans/<store_id>')
def shop_beans(store_id):
    get_login_user_id() # ログインチェック
    con = sqlite3.connect('coffee.db')
    cur = con.cursor()

    # その店舗の情報を取得
    cur.execute('SELECT * FROM user_shops WHERE store_id = ?', (store_id,))
    shop = cur.fetchone()

    # その店舗に関連付けられた豆をすべて取得
    cur.execute('SELECT * FROM user_beans WHERE store_id = ?', (store_id,))
    beans = cur.fetchall()

    con.close()

    
    return template('upload_coffee_shop_beans', shop=shop, beans=beans)

# 登録データの一覧表示
@route('/blist/view')
def view():
    con = sqlite3.connect('coffee.db')
    cur = con.cursor()

    # 既存のデータ取得
    blist = select_all(cur)
    blist_s = select_all_shops(cur)

    # ユーザーデータを全件取得
    cur.execute('SELECT * FROM users_data')
    users = cur.fetchall()

    con.close()

    
    tplt = """
    <h2>登録データ一覧</h2>

    <h3>コーヒー豆リスト</h3>
    %if not blist:
        <p>データなし</p>
    %else:
        %for row in blist:
            <p>
            %for cell in row:
                {{cell}} | 
            %end
            </p>
        %end
    %end

    <h3>お店リスト</h3>
    %if not blist_s:
        <p>データなし</p>
    %else:
        %for row in blist_s:
            <p>{{row}}</p>
        %end
    %end

    <h3>ユーザーリスト (users_data)</h3>
    %if not users:
        <p>ユーザーなし</p>
    %else:
        %for row in users:
            <p>
            ID: {{row[0]}}, 名前: {{row[1]}}, PASS: {{row[2]}}
            </p>
        %end
    %end
    """
    
    
    return template(tplt, blist=blist, blist_s=blist_s, users=users)

run(host='localhost',port=8782,reloader=True)
