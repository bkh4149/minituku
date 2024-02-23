#ファイルから問題セットを読み込むようにした2023/08/18
#３問に増やした、セッションで 2023-08-15
#４たくで複数回答あり、解答群は多数の中から４つをランダムで選択という形式のクイズ
import random

from flask import Flask, redirect, url_for, render_template, request,session
from flask_session import Session
A1 = Flask(__name__)
import datetime

#解答群をランダムでつくって問題文や解答群そのもの（qa_set）をここから作れるようにする
def month():
    now = datetime.datetime.now()    # 現在の日付と時刻を取得
    m = now.month       # 現在の月を取得
    #print("@48 type=",type(m),m)
    #print(f"今月は{m}月です。")

#ファイルから問題解答群セットの読み込み
def readf(fn):
    sets = []  # クイズと解答群、正解、解説のセット
    with open(fn, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()  # 改行を取り除く
            items = line.split(",")  # カンマで分割
            sets.append(items)
    #print("sets=", sets)
    return sets

#------ここから--------------------------

A1.config['SECRET_KEY'] = 'your_secret_key_here'
A1.config['SESSION_TYPE'] = 'filesystem'
Session(A1)

fn="fff1.txt"#ファイルから問題解答群セットの読み込み
qa_sets=readf(fn)

@A1.route('/endOfQuiz', methods=['GET'])
def endOfQuiz():
    return "End OF Quiz"

@A1.route('/makeAQuiz', methods=['GET'])
def makeAQuiz():
    #ログインしてなければリダイレクト
    if session.get("status") != "login":
        return redirect(url_for("login"))
    #問題番号と問題の取得    
    Q_total = session["Q_total"]
    Q_no = session["Q_no"]
    if Q_no>Q_total:
        return redirect(url_for("endOfQuiz"))

    #問題が進むとsessionは、 session=<FileSystemSession {'status': 'login', 'Q_no': 8, 'kekka': {0: 1, 1: 1, 2: 0, 3: 1, 4: 1, 5: 0, 6: 0, 7: 1}, 'correct_ans': []}>
    qa=qa_sets[Q_no]
    #qa="問題3:以下の動物の中で鳥はどれ？,ライオンx:象x:ペンギンo:カンガルーx:カモメo:スズメo, ペンギンは鳥の一種ですが、飛べません,,雑学"

    #解答群の作成
    arr = qa[1].split(":")#解答群の作成　多数の中から４つをランダムで選択
    #ライオンx:象x:ペンギンo:カンガルーx:カモメo:スズメo
    #["ライオンx","象x","ペンギンo","カンガルーx","カモメo","スズメo"]
    solution_num=min(4,len(arr)) #回答群(solution_sets)

    tmps = random.sample(arr, solution_num )#解答群の中から４つ選択する
    #tmps =["ライオンx","象x","カンガルーx","スズメo"]
    solution_set2=[]
    for tmp in tmps:
        solution_set2.append(tmp.strip())#余分な空白を削除して配列に追加  
    #solution_set2 = ["ライオンx","象x","カンガルーx","スズメo"]

    #解答群と正解群の作成
    solution_set=[]#解答群
    correct_ans=[]#正解群
    for r1 in solution_set2:
        solution_set.append(r1[:-1]) #解答群に最後の１文字はoxなので除去下文字を追加     
        tmp_ox=r1[-1]
        if tmp_ox=="o":#正解なら正確群に追加していく
            correct_ans.append(r1[:-1])#最後の１文字はoxなので除去
        elif tmp_ox=="x":
            pass
        else:
            print("format error")    
    print("solution_set=",solution_set)# 解答群
    print("correct_ans=",correct_ans)# 正解群
    session["correct_ans"]=correct_ans#正解を一旦保存しておく
    #出題
    return render_template('makeAQuiz.html', question=qa[0], choices=solution_set)

@A1.route('/check_answer', methods=['POST'])
def check_answer():
    #ログインしてなければログインへ
    if session.get("status") != "login":
        return redirect(url_for("login"))
    # if "status" not in session or  session["status"]!="login":
    #     return redirect(url_for("login"))   

    #第何問目かを取得
    Q_no=session["Q_no"]
    qa=qa_sets[Q_no]

    #ユーザーの回答を取得
    user_choice = request.form.getlist('choice')
    
    #正解の取得
    correct_ans=session["correct_ans"]

    # #正解かどうかのチェック
    if set(correct_ans) == set(user_choice):
        kekka= "正解です！"
        session["kekka"][Q_no]=1
    else:
        kekka= "不正解です。"
        session["kekka"][Q_no]=0

    #解説がurlやimageか
    #print("@quiz 104")
    if "http" in qa[3] and "www" in qa[3]:    
        data_type="url"
    else:
        data_type="text"

    #最後の問題ならセッションを削除    
    if session["Q_no"]==len(qa_sets)-1:
        #print('==========session["Q_no"]=',session["Q_no"],"len(qa_sets)-1=",len(qa_sets)-1)
        del session['Q_no']    
        del session['status']    
    else:
        session["Q_no"]+=1

    #print('@86 session["Q_no"]=',session["Q_no"],"data_type=",data_type)
    return render_template('kekka.html',kekka=kekka,Q_no=Q_no,maxq=len(qa_sets),kaisetu=qa[2],data_type=data_type,janru=qa[3],correct_ans=correct_ans)
 
#if __name__ == "__main__":
#    A1.run(debug=True,port=8888)
