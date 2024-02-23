from flask import Flask, redirect, url_for, render_template, request,session
from flask_session import Session
#import datetime
import pymysql
import bcrypt
from quiz import A1  # appのインスタンス化はこっちでやっている、そのインスタンスA1をインポート

A1.config['SECRET_KEY'] = 'your_secret_key_here'
A1.config['SESSION_TYPE'] = 'filesystem'
Session(A1)

connect={"host":"localhost", "user":"root", "password":"", "db":"user"}

@A1.route("/")
def start():
    return redirect(url_for("login"))

@A1.route("/login",methods=["GET"])#フォーム送信
def login():
    return render_template("login.html",message="こんちは")

@A1.route("/login",methods=["POST"])#フォーム受信
def login2():
    #POSTデータの取得
    username = request.form.get('username')
    password = request.form.get('password')
    # データベースに接続
    D1 = pymysql.connect(**connect)
    C1 = D1.cursor()
    sql = f"select * from users where id_name=%s "
    # SQLクエリを作成
    C1.execute(sql, (username))    # SQLクエリを実行
    fetch_data = C1.fetchone()
    #fetch_data=(2, 'rrr', '$2b$12$1ufbC9OYOcTABhWqtDvOc.nRUi3vivdGCM.CbllbQmpkHkTGhjBUK', 0)
    D1.close()    # データベース接続を閉じる
    
    if fetch_data :#データベースにusenameがあるなら（パスワードが一致したならではなく、単にユーザーが登録済みなら）
        if fetch_data[3]>=3:#try_count>3?
            print("THIS NAME IS LOCKED")
            return "THIS NAME IS LOCKED"
        try:#ｄｂには以前つくったデータが入っているので（ハッシュに加えてソルト込とは限らない）
            chk= bcrypt.checkpw(password.encode('utf-8'),fetch_data[2].encode('utf-8'))#合致するかのチェック（ハッシュに加えてソルト込みで）
        except ValueError:
            chk=False            

        if chk:
            # データベースのtry_countをゼロクリア
            D1 = pymysql.connect(**connect)
            C1 = D1.cursor()
            sql = f"UPDATE users SET try_count = 0 WHERE id_name = %s"            # SQLクエリを作成
            C1.execute(sql, (username,))    # SQLクエリを実行
            D1.commit()                     # 変更をコミット
            D1.close()                      # データベース接続を閉じる
            session.clear()
            session["status"]="login"
            session["Q_no"]=0
            session["Q_total"]=5
            session["kekka"]={}
            print( "login ok")
            return redirect(url_for("makeAQuiz"))#クイズ本体へ
        else:#ログイン失敗　パスワードが合致しない  try_countを + 1する
            # データベースに接続
            D1 = pymysql.connect(**connect)
            C1 = D1.cursor()
            sql = f"UPDATE users SET try_count = try_count + 1 WHERE id_name = %s"    # SQLクエリを作成
            C1.execute(sql, (username,))    # SQLクエリを実行
            D1.commit()                     # 変更をコミット
            D1.close()                      # データベース接続を閉じる
            return redirect(url_for("login2"))#パスワード再入力

    else:#データベースにusenameがないなら
        return redirect(url_for("regist1"))


@A1.route('/regist', methods=['GET'])#フォーム受信
def regist1():
    return render_template("regist.html",mes="新規登録")

@A1.route('/regist', methods=['POST'])
def regist2():
    username = request.form.get('username')
    password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')
    if password!=password_confirm:
        return render_template("regist.html",mes="confirm error")
    # データの存在チェック
    # if not username or not password:
    #     return 'Username or password is missing.', 400  # 400はBadRequestのHTTPステータスコードです。
    h_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    D1 = pymysql.connect(**connect)
    C1 = D1.cursor()
    sql = f"INSERT INTO users (id_name,password,try_count) VALUES (%s,%s,%s)"            # SQLクエリを作成
    C1.execute(sql, (username,h_pw,0))    # SQLクエリを実行
    D1.commit()                     # 変更をコミット
    D1.close()                      # データベース接続を閉じる
    return render_template("login.html")

A1.run(debug=True)
#A1.run(host="0.0.0.0", port=8800)