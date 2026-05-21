import audio
import head_pose
import detection
import threading as th
from flask import request
import os
import threading
import signal
from flask import Flask, render_template,request,flash,redirect,url_for,session,jsonify,send_from_directory
import sqlite3
from prettytable import PrettyTable
from PIL import Image
import cv2
from urllib.parse import urlencode
from moviepy.editor import VideoFileClip
import webbrowser
import time

app = Flask(__name__, template_folder='template')
app.secret_key="123"

head_pose_thread = None
audio_thread = None
detection_thread = None
head_pose_result = None
audio_result = None
detection_result = None

@app.route('/')
def home():
    return render_template('home.html')

con=sqlite3.connect("database.db")
con.execute("create table if not exists customer(pid integer primary key,name text,address text,contact integer,mail text)")
con.close()

@app.route('/studentslogin',methods=["GET","POST"])
def studentslogin():
    if request.method=='POST':
        name=request.form['name']
        password=request.form['password']
        con=sqlite3.connect("database.db")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("select * from customer where name=? and mail=?",(name,password))
        data=cur.fetchone()

        if data:
            session["name"]=data["name"]
            session["mail"]=data["mail"]
            return redirect("customer")
        else:
            flash("Username and Password Mismatch","danger")
    return redirect(url_for("studentlogin"))

@app.route('/student',methods=["GET","POST"])
def student():
    return render_template("studentlogin.html")

@app.route('/customer',methods=["GET","POST"])
def customer():
    return render_template("customer.html")

@app.route('/studentregister',methods=['GET','POST'])
def studentregister():
    con = None 
    try:
        if request.method == 'POST':
            name = request.form['name']
            address = request.form['address']
            contact = request.form['contact']
            mail = request.form['mail']
            if is_username_exists1(name):
                flash("Username already exists. Please choose another name.", "danger")
            else:
                con = sqlite3.connect("database.db")
                cur = con.cursor()
                cur.execute("insert into customer(name, address, contact, mail) values(?,?,?,?)",(name, address, contact, mail))
                            
                con.commit()
                flash("Record Added Successfully", "success")

    except Exception as e:
        flash(f"Error in Insert Operation: {e}", "danger")

    finally:
        if con is not None:
            con.close()

    return render_template('studentregister.html')

def is_username_exists1(name):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM customer WHERE name=?", (name,))
    data = cur.fetchone()
    con.close()
    return data is not None

con=sqlite3.connect("database.db")
con.execute("create table if not exists admin(pid integer primary key,name text,address text,contact integer,mail text)")
con.close()

@app.route('/adminlog',methods=["GET","POST"])
def adminlog():
    if request.method=='POST':
        name=request.form['name']
        password=request.form['password']
        con=sqlite3.connect("database.db")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("select * from admin where name=? and mail=?",(name,password))
        data=cur.fetchone()

        if data:
            session["name"]=data["name"]
            session["mail"]=data["mail"]
            return redirect("adminpage")
        else:
            flash("Username and Password Mismatch","danger")
    return redirect(url_for("adminlogin"))

@app.route('/adminpage',methods=["GET","POST"])
def adminpage():
    return render_template("adminpage.html")

@app.route('/admin',methods=["GET","POST"])
def admin():
    return render_template("adminlogin.html")

def is_username_exists(name):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM admin WHERE name=?", (name,))
    data = cur.fetchone()
    con.close()
    return data is not None

@app.route('/adminregister', methods=['GET', 'POST'])
def adminregister():
    con = None 
    try:
        if request.method == 'POST':
            name = request.form['name']
            address = request.form['address']
            contact = request.form['contact']
            mail = request.form['mail']
            if is_username_exists(name):
                flash("Username already exists. Please choose another name.", "danger")
            else:
                con = sqlite3.connect("database.db")
                cur = con.cursor()
                cur.execute("insert into admin(name, address, contact, mail) values(?,?,?,?)",(name, address, contact, mail))
                            
                con.commit()
                flash("Record Added Successfully", "success")

    except Exception as e:
        flash(f"Error in Insert Operation: {e}", "danger")

    finally:
        if con is not None:
            con.close()

    return render_template('adminregister.html')

@app.route('/studentlogout')
def studentlogout():
    session.clear()
    return redirect(url_for("studentlogin"))
@app.route('/adminlogout')
def adminlogout():
    session.clear()
    return redirect(url_for("adminlogin"))

@app.route('/studentlogin')
def studentlogin():
    return render_template('studentlogin.html')

@app.route('/studentlogin1', methods=['POST'])
def studentlogin1():
   
    return redirect(url_for('adminpage'))

@app.route('/adminlogin')
def adminlogin():
    return render_template('adminlogin.html')

@app.route('/adminlogin1', methods=['POST'])
def adminlogin1():
    return redirect(url_for('adminpage'))

@app.route('/studentname', methods=["GET", "POST"])
def studentname():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM customer')
    data = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    conn.close()
    return render_template('studentdetails.html', column_names=column_names, data=data)

@app.route('/studentimage')
def studentimage():
    return render_template('studentimage.html')

@app.route('/studentvideo')
def studentvideo():
    return render_template('studentvideo.html')

video_folder = r'C:\Users\ahari\Desktop\proctoring-main\src\static\videos'
@app.route('/studentvideo2', methods=["GET", "POST"])
def list_and_play_videos():
    videos = [video for video in os.listdir(video_folder) if video.endswith(('.mp4', '.avi', '.webm'))]
    if not videos:
        return render_template('studentvideo.html', videos=[], message="No videos found in the specified folder.")
    return render_template('studentvideo.html', videos=videos)


@app.route('/getresult')
def getresult():
    image_dir = r'C:\Users\ahari\Desktop\proctoring-main\src\static\graphs'
    image_list = []
    for filename in os.listdir(image_dir):
        if filename.endswith(('jpg', 'jpeg', 'png')):
            image_list.append({'filename': filename})
    return jsonify(image_list)

@app.route('/start', methods=['POST'])
def run_python_code():
    head_pose_thread = th.Thread(target=head_pose.pose)
    audio_thread = th.Thread(target=audio.sound)
    detection_thread = th.Thread(target=detection.run_detection)

    head_pose_thread.start()
    audio_thread.start()
    detection_thread.start()

    head_pose_thread.join()
    audio_thread.join()
    detection_thread.join()
    result = " "
    return result

@app.route('/end', methods=['POST'])
def stop_threads():
    global head_pose_thread, audio_thread, detection_thread
    try:
        if head_pose_thread is not None and head_pose_thread.is_alive():
            head_pose_thread._stop()
            head_pose_thread.join()

        if audio_thread is not None and audio_thread.is_alive():
            audio_thread._stop()
            audio_thread.join()

        if detection_thread is not None and detection_thread.is_alive():
            detection_thread._stop()
            detection_thread.join()

    except threading.ThreadError as e:
        print(f"Error stopping threads: {e}")
    
    os.kill(os.getpid(), signal.SIGINT)
    session.clear()
    return redirect(url_for("studentlogin"))

@app.route('/aregister',methods=["GET","POST"])
def aregister():
    return render_template("adminregister.html")
@app.route('/sregister',methods=["GET","POST"])
def sregister():
    return render_template("studentregister.html")

if __name__ == '__main__':
    app.run(debug=True)