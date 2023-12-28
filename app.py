import sqlite3
from flask import Flask, render_template, request, g

app = Flask(__name__)
DATABASE = 'wnjpn.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def SearchSimilarWords(word):
    # get_dbを使用してデータベース接続を取得
    conn = get_db()
    # 問い合わせしたい単語がWordnetに存在するか確認する
    cur = conn.execute("select wordid from word where lemma='%s'" % word)
    word_id = 99999999  #temp 
    for row in cur:
        word_id = row[0]

    # Wordnetに存在する語であるかの判定
    if word_id==99999999:
        print("「%s」は、Wordnetに存在しない単語です。" % word)
        return
    else:
        print("【「%s」の類似語を出力します】\n" % word)

    # 入力された単語を含む概念を検索する
    cur = conn.execute("select synset from sense where wordid='%s'" % word_id)
    synsets = []
    for row in cur:
        synsets.append(row[0])
    results = []
    # 概念に含まれる単語を検索して画面出力する
    no = 1
    for synset in synsets:
        cur1 = conn.execute("select name from synset where synset='%s'" % synset)
        for row1 in cur1:
            concept_name = row1[0]

        cur2 = conn.execute("select def from synset_def where (synset='%s' and lang='jpn')" % synset)
        sub_no = 1
        for row2 in cur2:
            definition = row2[0]
            sub_no += 1
        cur3 = conn.execute("select wordid from sense where (synset='%s' and wordid!=%s)" % (synset, word_id))
        sub_no = 1
        synonyms = []
        for row3 in cur3:
            target_word_id = row3[0]
            cur3_1 = conn.execute("select lemma from word where wordid=%s" % target_word_id)
            for row3_1 in cur3_1:
                synonyms.append(row3_1[0])
                sub_no += 1

        results.append((no, concept_name, definition, synonyms))
        no += 1

    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    word = request.form['word']
    result = SearchSimilarWords(word)
    if result is None:
        return render_template('index.html', word=word, result="「%s」は、Wordnetに存在しない単語です。" % word)
    return render_template('result.html', word=word, result=result)

if __name__ == '__main__':
    app.run(debug=True)
