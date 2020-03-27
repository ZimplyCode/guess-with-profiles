import random, uuid, hashlib
from flask import Flask, render_template, request, make_response, redirect, url_for
from models import User, Comment, db

app = Flask(__name__)
db.create_all()


@app.route("/", methods=["GET"])
def index():
    session_token = request.cookies.get("session_token")

    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
    else:
        user = None

    title = "Guess The Secret Number"
    return render_template("index.html", user=user, title=title)


@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("user-name")
    email_address = request.form.get("user-email")
    password = request.form.get("user-password")

    # hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # create a secret number
    secret_number = random.randint(1, 100)

    # see if user already exists
    user = db.query(User).filter_by(email=email_address).first()

    if not user:
        # create a User object
        user = User(name=name, email=email_address, secret_number=secret_number, password=hashed_password)

        db.add(user)
        db.commit()

    # check if password is incorrect
    if hashed_password != user.password:
        return "WRONG PASSWORD! Go back and try again."
    else:
        # create a random session token for this user
        session_token = str(uuid.uuid4())

        # save the session token in a database
        user.session_token = session_token
        db.add(user)
        db.commit()

        # save user's session token into a cookie
        response = make_response(redirect(url_for('index')))
        response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')

        return response


@app.route("/result", methods=["POST"])
def result():
    guess = int(request.form.get("guess"))

    session_token = request.cookies.get("session_token")

    # get user from the database based on her/his email address
    user = db.query(User).filter_by(session_token=session_token).first()

    if guess == user.secret_number:
        title = "Succes!"
        message = "Correct! The secret number is {0}".format(str(guess))

        # create a new random secret number
        new_secret = random.randint(1, 30)

        # update the user's secret number in the User collection
        user.secret_number = new_secret
        db.add(user)
        db.commit()
    elif guess > user.secret_number:
        title = "Guess to high!"
        message = "Your guess is not correct... try something smaller."
    else:
        title = "Guess to low!"
        message = "Your guess is not correct... try something bigger."

    return render_template("result.html", message=message, title=title)


@app.route("/profile", methods=["GET"])
def profile():
    session_token = request.cookies.get("session_token")

    # get user from the database based on her/his email address
    user = db.query(User).filter_by(session_token=session_token).first()

    if user:
        return render_template("profile.html", user=user, title="Profile page")
    else:
        return redirect(url_for("index"))


@app.route("/profile/edit", methods=["GET", "POST"])
def profile_edit():
    session_token = request.cookies.get("session_token")

    # get user from the database based on her/his email address
    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        if user:  # if user is found
            return render_template("profile_edit.html", user=user, title="Edit Profile")
        else:
            return redirect(url_for("index"))
    else:
        name = request.form.get("profile-name")
        email = request.form.get("profile-email")

        # update the user object
        user.name = name
        user.email = email

        # store changes into the database
        db.add(user)
        db.commit()

        return redirect(url_for("profile"))


@app.route("/profile/delete", methods=["GET", "POST"])
def profile_delete():
    session_token = request.cookies.get("session_token")

    # get user from the database based on her/his email address
    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        if user:  # if user is found
            return render_template("profile_delete.html", user=user, title="Delete User?")
        else:
            return redirect(url_for("index"))
    else:
        # delete the user in the database
        db.delete(user)
        db.commit()

        return redirect(url_for("index"))


@app.route("/users", methods=["GET"])
def all_users():
    users = db.query(User).all()

    return render_template("users.html", users=users, title="All users")


@app.route("/user/<user_id>", methods=["GET"])
def user_details(user_id):
    user = db.query(User).get(user_id)  # .get() can help you query by the EMail

    return render_template("user_details.html", user=user, title="User details")


@app.route("/comments", methods=["GET", "POST"])
def comments():
    session_token = request.cookies.get("session_token")

    # get user from the database based on her/his email address
    user = db.query(User).filter_by(session_token=session_token).first()
    users = db.query(User).all()
    comments = db.query(Comment).all()

    if request.method == "GET":
        if user:  # if user is found
            return render_template("comments.html", user=user, users=users, comments=comments, title="Leave a comment, and make us happy!")
        else:
            return redirect(url_for("index"))
    else:
        userid = request.form.get("user-id")
        usercomment = request.form.get("user-comment")

        # update the user object
        comment = Comment(userid=userid, comment=usercomment)

        # store changes into the database
        db.add(comment)
        db.commit()

        return redirect(url_for("comments"))


if __name__ == '__main__':
    app.run(debug=True)