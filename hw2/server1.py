import json
import os
from _sha256 import sha256
import cut

from flask import Flask, render_template, send_from_directory, request, session

server = Flask(__name__)

SER_ROOT = os.path.dirname(os.path.abspath(__file__))


# the home page
@server.route("/")
def index():
    return render_template("./home.html", image1="./image1.jpg")


@server.route("/sign_up_in")
def sign_up_in():
    return render_template('sign_up_in.html')


# change logged_in status after clicking log out
@server.route('/log_out')
def logOut():
    session['logged_in'] = False
    session['user'] = None
    return render_template('home.html')


@server.route('/uploadImage')
def uploadImage():
    return render_template('uploadImage.html')


@server.route('/do_sign_up', methods=['POST'])
def doSignUp():
    # get account infor from front-end
    user = request.get_json()[u'sign_in_name'].encode('ascii')
    password = request.get_json()[u'sign_in_password'].encode('ascii')
    # user = do_xor(user)
    # password = do_xor(user)
    user = str(user)
    password = str(password)

    dic = os.getcwd()
    print(dic)
    # check if account has been signed up
    directory = dic + '/image_repo/' + user + '/'
    if os.path.exists(directory):
        return json.dumps({'status': 'FAIL'})

    if not os.path.exists(directory):
        os.makedirs(directory)

    # store account info as sha256
    # it allow user have same user name
    m = sha256()
    m.update(user.encode())
    m.update(password.encode())
    info = m.hexdigest() + '\n'
    print(os.getcwd())
    if os.path.isfile('userInfo.txt'):
        with open('userInfo.txt', 'a') as secret:
            secret.write(info)
            secret.close()
    else:
        with open('userInfo.txt', 'w+') as secret:
            secret.write(info)
            secret.close()

    return json.dumps({'status': 'OK'})


@server.route('/do_sign_in', methods=['POST'])
def doSignIn():
    print(request.get_json())
    user = request.get_json()[u'sign_in_name'].encode('ascii')
    password = request.get_json()[u'sign_in_password'].encode('ascii')
    # user = do_xor(user)
    # password = do_xor(user)
    user = str(user)
    password = str(password)

    m = sha256()
    m.update(user.encode())
    m.update(password.encode())
    info = m.hexdigest()

    # compare input sha with stored sha
    if os.path.isfile('userInfo.txt'):
        with open('userInfo.txt', 'r') as secret:
            line = secret.readline()
            while line:
                if info == line.strip():
                    session['logged_in'] = True
                    session['username'] = user
                    session['startPos'] = 0
                    return json.dumps({'status': 'OK'})
                line = secret.readline()
    return json.dumps({'status': 'FAIL'})


@server.route("/upload", methods=['POST'])
def upload():
    # check if user logged_in
    if not session['logged_in']:
        return render_template('home.html')

    # once logged_in, user is able to store images to his own folder
    # under image_repo directory
    tmp = 'image_repo/' + session['username'] + '/'
    savePath = os.path.join(SER_ROOT, tmp)
    if not os.path.isdir(savePath):
        os.mkdir(savePath)
    else:
        print("Failed to create directory\n")

    item = request.files.getlist('file')
    if len(item) == 0:
        return render_template('uploadImage.html')

    # set upload time
    for image in request.files.getlist('file'):
        filename = image.filename
        print(filename.split('.')[1])
        if filename.split('.')[1] in ['jpg', 'png', 'jpeg']:
            image.save(savePath + filename)
            os.utime(savePath + filename, None)

    files = os.listdir(savePath)
    s = []
    for file in files:
        s.append(str(file) + '\n')
        photoName = savePath + '/' + file
        cut.cut(photoName)
    return render_template("complete.html")


@server.route("/gallery/<startPos>")
def displayGallery(startPos):
    # check if user logged_in
    # load images and sort them based on utime
    if session.get('logged_in'):
        print(startPos)
        pos = int(startPos) * 10
        image_names = os.listdir('./image_repo/' + session['username'])
        bubbleSort(image_names)
        print(image_names)
        tmp = image_names[pos:pos + 10]
        return render_template("gallery.html", image_names=tmp)
    else:
        return render_template('home.html')


# send images from server to view gallery
@server.route("/upload/<filename>")
def send_image(filename):
    folder = "image_repo/" + session['username']
    return send_from_directory(folder, filename)


@server.route("/home/<filename>")
def show_image(filename):
    folder = "./templates"
    return send_from_directory(folder, filename)


# do bubble sort based on image upload time
def bubbleSort(image_names):
    imagePath = SER_ROOT + '/image_repo/' + session['username'] + '/'
    for passnum in range(len(image_names) - 1, 0, -1):
        for i in range(passnum):
            if os.path.getmtime(imagePath + image_names[i]) < os.path.getmtime(imagePath + image_names[i + 1]):
                tmp = image_names[i]
                image_names[i] = image_names[i + 1]
                image_names[i + 1] = tmp


def do_xor(msg):
    newMsg = ''
    for index in range(0, len(msg)):
        newMsg += chr(int(str(ord(msg[index]) ^ 6)))
    return msg


if __name__ == "__main__":
    server.secret_key = os.urandom(12)
    server.run(port=5454, debug=True)
