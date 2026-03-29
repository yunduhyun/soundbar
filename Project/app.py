from flask import Flask, render_template, redirect, url_for, session, request, jsonify
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(32)
UPLOAD_FOLDER = 'static/uploads'

#<-------------------------------------------db 처리 ⬇️-------------------------------------------------->
def init_db():
    conn = sqlite3.connect('accounts.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname    TEXT NOT NULL,
            username    TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sounds(
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname    TEXT NOT NULL,
            decibel     INTEGER NOT NuLL,
            filename    TEXT NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP       
        )
    ''')

    conn.commit() 
    conn.close() 



def check_account(username, password):
  conn = sqlite3.connect('accounts.db')
  cursor = conn.cursor()
  cursor.execute('SELECT * FROM accounts WHERE username = ? AND password = ?',(username, password))
  user = cursor.fetchone()
  conn.close()
  return user



def add_account(nickname, username ,password):
  conn = sqlite3.connect('accounts.db')
  cursor = conn.cursor()
  try:
    cursor.execute('INSERT INTO accounts (nickname, username, password) VALUES (?, ?, ?)',(nickname,username,password))
    conn.commit()
    conn.close()
    return True
  except sqlite3.IntegrityError:
    conn.close()
    return False
  finally:
    conn.close()



def add_sound(nickname, decibel, filename):
  conn = sqlite3.connect('accounts.db')
  cursor = conn.cursor()
  cursor.execute('INSERT INTO sounds (nickname, decibel, filename) VALUES (?, ?, ?)',(nickname,decibel,filename))
  conn.commit()
  conn.close()
  return True



def get_sound():
  conn = sqlite3.connect('accounts.db')
  cursor = conn.cursor()
  cursor.execute('SELECT nickname, decibel, filename FROM sounds ORDER BY decibel DESC LIMIT 3') 
  top3_data = cursor.fetchall()
  conn.close()
  return top3_data
# def delete_account(nickname, )



def delete_soundfile_db(filename):
  conn = sqlite3.connect('accounts.db')
  cursor = conn.cursor()
  cursor.execute('DELETE FROM sounds WHERE filename = ?', (filename,))
  conn.commit()
  conn.close()

  file_path = os.path.join(UPLOAD_FOLDER, filename)
  if os.path.exists(file_path):
    os.remove(file_path)
  return True

#<-------------------------------------------db 처리 ⬆️-------------------------------------------------->

@app.route('/login', methods=['GET'])
def get_login():
  return render_template('login.html')



@app.route('/login', methods=['POST'])
def post_login():
  if 'username' in session:
    return redirect(url_for('get_index'))

  username = request.form.get('username')
  password = request.form.get('password')
  
  user = check_account(username,password)
  if user: 
      session['username'] = user[2]
      session['nickname'] = user[1]
      return redirect(url_for('get_index'))
  else:
    return redirect(url_for('get_login_failure'))
  


@app.route('/login_failure', methods=['GET'])
def get_login_failure():
  return render_template('login_failure.html')



@app.route('/register', methods=['GET'])
def get_register():
  if 'username' in session:
    return redirect(url_for('get_index'))
  return render_template('register.html')



@app.route('/register', methods=['POST'])
def post_register():
  if 'username' in session:
    return redirect(url_for('get_index'))
  
  username = request.form.get('username')
  password = request.form.get('password')
  nickname = request.form.get('nickname')

  if add_account(nickname, username, password):
    return redirect(url_for('get_login'))
  else:
    return redirect(url_for('get_register_failure'))



@app.route('/register_failure', methods=['GET'])
def get_register_failure():
  return render_template('register_failure.html')



@app.route('/logout', methods=['GET'])
def get_logout():
  session.clear()
  return redirect(url_for('get_login'))



@app.route('/index',methods=['GET'])
def get_index():
  if 'username' not in session:
    return redirect(url_for('get_login'))
  return render_template('index.html')



@app.route('/upload_sound', methods=['POST'])
def upload_sound():
  if 'sound_file' not in request.files:
    return jsonify({'error' : '파일이 없음'})
  
  file = request.files['sound_file']
  decibel = request.form.get('decibel','0')
  nickname = session.get('nickname','guest')
  now = datetime.now().strftime('%Y%m%d_%H%M%S')
  filename = f"{nickname}_{now}.wav"

  if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
  
  file_path = os.path.join(UPLOAD_FOLDER, filename)
  file.save(file_path)

  if add_sound(nickname, decibel, filename):
    return jsonify({
      "status" : "success",
      "filename" : filename,
      "recorded_at" : datetime.now().strftime('%Y-%m-%d')
    })



@app.route('/archive')
def archive():
  upload_path = 'static/uploads'

  if os.path.exists(upload_path):
    files = sorted(os.listdir(upload_path))
  else:
    files = []

  sound_list = []
  for f in files:
    if not f.endswith('.wav'):
      continue
    parts = f.replace('.wav', '').split('_')
    
    if len(parts) >= 3:
      nickname = parts[0]
      raw_date = parts[1]
      raw_time = parts[2]

      formatted_date = f"{raw_date[:4]}년 {raw_date[4:6]}월 {raw_date[6:8]}일"
      formatted_time = f"{raw_time[:2]}시 {raw_time[2:4]}분 {raw_time[4:6]}초"

      sound_list.append({
        'filename' : f,
        'nickname' :nickname,
        'date' : formatted_date,
        'time' : formatted_time
      })

  return render_template('archive.html', sounds = reversed(sound_list)) 
  #최신순으로 



@app.route('/ranking')
def ranking():
  top3_data = get_sound()

  top3_sounds = []
  for row in top3_data:
    top3_sounds.append({
      'nickname' : row[0],
      'decibel' : row[1],
      'filename' : row[2]
    })
  return render_template('ranking.html',top3 = top3_sounds)



@app.route('/delete_sound', methods=['POST'])
def delete_sound():
  print(f"DEGUG.. 현재 로그인 유저 {session.get('username')}")
  if 'username' not in session:
    return jsonify({'status':'error','messgae':'로그인이 필요합니다'}), 401

  if session.get('username') != 'admin':
    return jsonify({'status':'error', 'message':'권한이 없습니다. 관리자만 삭제 가능합니다'}), 403
  
  data = request.get_json()
  filename = data.get('filename')

  if delete_soundfile_db(filename):
    return jsonify({'status':'success'})
  else:
    return jsonify({'status':'error', 'message':'파일 삭제중 오류가 발생하였습니다'})



if __name__ == '__main__':
  init_db()
  app.run(host='0.0.0.0', port=8888, debug=True)