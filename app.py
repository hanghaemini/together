from flask import Flask, render_template, jsonify, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson.objectid import ObjectId

import jwt
import hashlib
import certifi

app = Flask(__name__)
client = MongoClient('mongodb+srv://text:sparta@cluster0.cvfqh2o.mongodb.net/cluster0?retryWrites=true&w=majority', tlsCAFile=certifi.where())
db = client.dbsparta

SECRET_KEY = 'SPARTA'

## HTML을 주는 부분
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    return render_template('index.html', istoken = bool(token_receive))

@app.route('/login')
def login():
    token_receive = request.cookies.get('mytoken')
    textInfo = [
        {"text": "아이디",
         "id": "user_id"
         },
        {"text": "비밀번호",
         "id": "user_pw"
         },
    ]
    return render_template('login.html', textInfo=textInfo, istoken=bool(token_receive))

@app.route('/login/api', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})
    
    if result is not None:
        payload = {
            'id': id_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60*60*1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

@app.route('/c')
def c():
    token_receive = request.cookies.get('mytoken')
    post_list = list(db.create.find({'category': 'C'}))
    return render_template('c.html', post_list = post_list, token=bool(token_receive))

@app.route('/java')
def java():
    token_receive = request.cookies.get('mytoken')
    post_list = list(db.create.find({'category': 'Java'}))
    return render_template('java.html', post_list = post_list, token=bool(token_receive))

@app.route('/cplusplus')
def cplusplus():
    token_receive = request.cookies.get('mytoken')
    post_list = list(db.create.find({'category': 'C++'}))
    return render_template('cplusplus.html', post_list = post_list, token=bool(token_receive))

@app.route('/python')
def python():
    token_receive = request.cookies.get('mytoken')
    post_list = list(db.create.find({'category': 'Python'}))
    return render_template('python.html', post_list = post_list, token=bool(token_receive))

@app.route('/visualbasic')
def visualbasic():
    token_receive = request.cookies.get('mytoken')
    post_list = list(db.create.find({'category': 'Visual Basic'}))
    return render_template('visualbasic.html', post_list = post_list, token=bool(token_receive))

@app.route('/javascript')
def javascript():
    token_receive = request.cookies.get('mytoken')
    post_list = list(db.create.find({'category': 'JavaScript'}))
    return render_template('javascript.html', post_list = post_list, token=bool(token_receive))



# detail주석
@app.route('/detail/<keyword>')
def detail(keyword):
    token_receive = request.cookies.get('mytoken')
    post = db.create.find_one({'_id':ObjectId(keyword)})
    return render_template('detail.html', post=post, token=bool(token_receive))

@app.route("/detail/comment", methods=["POST"])
def comment_post():
    token_receive = request.cookies.get('mytoken')
    if token_receive is not None:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload["id"]})
        id_receive = request.form['id_give']
        comment_receive = request.form['comment_give']
        post = db.create.find_one({'_id': ObjectId(id_receive)})
        comment_list = post['comment']
        dic = {
            'nickname': user_info['nickname'],
            'comment': comment_receive,
        }
        comment_list.append(dic)
        db.create.update_one({'_id':ObjectId(id_receive)},{'$set':{'comment':comment_list}})
        return jsonify({'msg': '댓글 등록 되었습니다.'})
    else:
        return jsonify({'msg': '로그인 후 이용해 주세요'})


# detail주석끝


# -----------------------------
# 회원가입 페이지(join.html)을 불러올 때 textInfo Array에 Input Text 값을 넣어서 보내줌
@app.route('/join')
def join():
    textInfo = [
        {"text": "아이디 (영문과 숫자 및 일부 특수문자(._-), 2-10자 길이)",
         "id": "user_id"
         },
        {"text": "비밀번호 (영문, 숫자는 필수이며 일부 특수 문자 사용 가능 8-20자 길이)",
         "id": "user_pw"
         },
        {"text": "비밀번호 재입력",
         "id": "user_pw_re"
         },
        {"text": "닉네임",
         "id": "user_nickname"
         },
        {"text": "Github 주소 (선택)",
         "id": "user_git"
         }
    ]
    return render_template('join.html', textInfo=textInfo)

# 아이디 중복 여부 체크, 입력 받은 아이디 값을 가져와 db에 같은 값이 있는지 확인하여 boolean 값으로 돌려줌
@app.route('/join/id_check', methods=["POST"])
def userIdCheck():
    idReceive = request.form['id_give']
    exists = bool(db.user.find_one({"id": idReceive}))
    return jsonify({'result:': 'success', 'exists': exists})

# 닉네임 중복 여부 체크, 위와 동일
@app.route('/join/nickname_check', methods=["POST"])
def userNicknameCheck():
    nicknameReceive = request.form['nickname_give']
    exists = bool(db.user.find_one({"nickname": nicknameReceive}))
    return jsonify({'result:': 'success', 'exists': exists})

# 회원 정보를 받아와서 비밀번호는 해쉬맵으로 암호화한 뒤에 db에 저장
@app.route('/join', methods=["POST"])
def userRegister():
    idReceive = request.form['id_give']
    pwReceive = request.form['pw_give']
    nicknameReceive = request.form['nickname_give']
    gitReceive = request.form['git_give']

    pwHash = hashlib.sha256(pwReceive.encode('utf-8')).hexdigest()

    doc = {
        'id': idReceive,
        'pw': pwHash,
        'nickname': nicknameReceive,
        'git': gitReceive,
    }
    db.user.insert_one(doc)

    return jsonify({'msg': '저장 완료!'})


# 게시글 작성 페이지 로드시 로그인 여부 확인 및 로그인시 작성자 닉네임 불러오기
@app.route('/create', methods=['GET'])
def create():
    token_receive = request.cookies.get('mytoken')
    try:
        if token_receive is not None:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.user.find_one({"id": payload["id"]})

            return render_template('create.html', user_info=user_info)
        else:
            return redirect("/login")
    except jwt.ExpiredSignatureError:
        return redirect('/login')

# 게시글 작성 저장
@app.route('/create', methods=['POST'])
def postCreate():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 포스팅하기
        userInfo = db.user.find_one({"id": payload["id"]})

        categoryReceive = request.form["categoryGive"]
        titleReceive = request.form["titleGive"]
        contentReceive = request.form["contentGive"]
        if titleReceive == "" or contentReceive == "":
            return jsonify({'msg': '내용을 모두 채워주세요.'})
        else:
            comment = []

            doc = {
                "id": userInfo["id"],
                "nickname": userInfo["nickname"],
                "category": categoryReceive,
                "title": titleReceive,
                "content": contentReceive,
                "comment": comment
            }
            db.create.insert_one(doc)
            return jsonify({"result": "success", 'msg': '포스팅 성공'})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)
