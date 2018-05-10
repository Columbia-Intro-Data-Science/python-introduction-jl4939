from flask import Flask, render_template, flash, request, url_for, redirect, session
from content_management import Content, All_data
from recommend import entry_variables, set_matrix, cal_distance
import pandas as pd
from dbconnect import connection
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
from functools import wraps
from sklearn.metrics import pairwise_distances

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'



# Logged in Decrator
# --------------------
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first!")
            return redirect(url_for('login_page'))
    return wrap



# Index Page
# --------------------
# TEST_1 = Content()

@app.route('/')
def index():
    return render_template('index.html')


# Recommend Page
# --------------------
@app.route('/recommend/')
@login_required
def recommend_page():
    return render_template('recommend.html')


# Recommend Result Page
# --------------------
@app.route('/recommend_result/', methods=['POST'])
@login_required
def recommend_result_page():
    try:
        df = pd.read_csv('/home/jl4939/mysite/static/data/data_cn_1950.csv',index_col=None)
        id_entry = int(request.form['rank'])-1

        # Verify the input value is in the range(1950)
        if id_entry >= 0 and id_entry <=1949:
            # Extract Streamer Function
            def extract_streamer(df, listed_streamer):
                like_streamer = ['_' for _ in range(31)]
                i = 0
                for index in listed_streamer:
                    like_streamer[i] = list(df.iloc[index][['排名','主播', '平台','类别','直播间地址']])
                    i += 1
                like_streamer.sort()
                for s in range(31):
                    if like_streamer[s][0] == id_entry+1:
                        del like_streamer[s]
                        break
                return like_streamer

            listed_streamer = cal_distance(df, id_entry)
            recommendation_list_thirty = extract_streamer(df, listed_streamer)
            recommendation_list = []
            for i in range(10):
                recommendation_list.append(recommendation_list_thirty[i])

            return render_template('recommend_result.html', recommendation_list=recommendation_list)

        # Not in range(1950), redirect to recommend_page
        else:
            flash("Rank Number must be between 1 to 1950 !")
            return redirect(url_for('recommend_page'))

    except Exception as e:
        return str(e)


# Add 3 Liked Streamer Page
# --------------------
@app.route('/add_streamer/', methods=['POST'])
@login_required
def add_streamer_page():
    try:
        temp_streamer_rank = []
        temp_streamer_rank.append(str(request.form['streamer_rank_1']))
        temp_streamer_rank.append(str(request.form['streamer_rank_2']))
        temp_streamer_rank.append(str(request.form['streamer_rank_3']))
        streamer_rank = list(set(temp_streamer_rank))
        sql_data = ','.join(streamer_rank)
        c, conn = connection()
        c.execute("UPDATE users SET settings='{0}' WHERE username='{1}';".format(sql_data, str(session['username'])))
        conn.commit()
        flash("Successfully Added!")
        c.close()
        conn.close()

        return redirect(url_for('test'))
    except Exception as e:
        return str(e)







# All Data Page
# --------------------
data_matrix = All_data()

@app.route('/all_data/')
def all_data():
    try:
        return render_template('all_data.html',data_matrix=data_matrix)
    except Exception as e:
        return str(e)



# Profile Page
# --------------------
@app.route('/profile/')
@login_required
def profile_page():
    try:
        c, conn = connection()
        profile_username = str(session['username'])
        c.execute("SELECT * FROM users WHERE username='{0}'".format(str(session['username'])))
        profile_data = c.fetchall()
        profile_email = profile_data[0][3]
        profile_settings = profile_data[0][4]
        c.close()
        conn.close()

        return render_template("profile.html", profile_username=profile_username, profile_email=profile_email, profile_settings=profile_settings)

    except Exception as e:
        return str(e)





# Logout Page
# --------------------
@app.route('/logout/')
@login_required
def logout_page():
    session.clear()
    flash("You have been logged out!")
    return redirect(url_for('test'))





# Login Page
# --------------------
@app.route('/login/', methods=["GET","POST"])
def login_page():
    try:
        c, conn = connection()
        if request.method == "POST":
            data = c.execute("SELECT * FROM users WHERE username = (%s)", [thwart(request.form['username'])])
            data = c.fetchone()[2]

            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['username'] = request.form['username']


                flash("You are now logged in!")
                return redirect(url_for("recommend_page"))

            else:
                error = "Invalid credentials, try again."

        return render_template("login.html")

    except Exception as e:
        error = "Invalid credentials, try again."
        return render_template("login.html", error=error)



# Register Page
# --------------------
class RegistrationForm(Form):
    username = TextField('Username', [validators.Required(), validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Required(), validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.Required(), validators.EqualTo('confirm', message='Password must match!')])
    confirm = PasswordField('Repeat Password')

    accept_tos = BooleanField("I accept the <a href="">Terms of Service</a> and the <a href="">Privacy Notice (Last updated 2018)</a>", [validators.Required()])

@app.route('/register/', methods=["GET","POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            c, conn = connection()

            x = c.execute("SELECT * FROM users WHERE username = (%s)", [(thwart(username))])

            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template('register.html', form=form)

            else:
                c.execute("INSERT INTO users (username, password, email, tracking) VALUES (%s, %s, %s, %s)", (thwart(username),thwart(password),thwart(email),thwart("/recommend/")))
                conn.commit()
                flash("Thanks for registering!")
                c.close()
                conn.close()


                session['logged_in'] = True
                session['username'] = username


                return redirect(url_for('test'))

        return render_template("register.html", form=form)

    except Exception as e:
        return str(e)




# Social Page
# --------------------
@app.route('/social/')
@login_required
def social_page():
    c, conn = connection()
    test_liked_streamer_rank = c.execute("SELECT settings FROM users WHERE username='{0}'".format(str(session['username'])))
    test_liked_streamer_rank = c.fetchall()

    # Test if the current user has any liked streamer
    if test_liked_streamer_rank[0][0] == None:
        c.close()
        conn.close()

        flash('You should add your liked streamer first !')
        return redirect(url_for('recommend_page'))

    else:

        # Get all "Liked Streamer Rank" from SQL
        tuple_all_liked_streamer_rank = c.execute("SELECT settings FROM users")
        tuple_all_liked_streamer_rank = c.fetchall()
        list_all_liked_streamer_rank = []
        for s in tuple_all_liked_streamer_rank:
            list_all_liked_streamer_rank.append(s[0])

        # Get all "username" from SQL
        tuple_all_username = c.execute("SELECT username FROM users")
        tuple_all_username = c.fetchall()
        list_all_username = []
        for s in tuple_all_username:
            list_all_username.append(s[0])

        ## Collaborative Filter: User to User

        # Construct "0-1 Matrix": Index = username, Column = streamer rank (1 - 1950)
        lis = range(1,1951)
        list1_1950 = ["{:}".format(x) for x in lis]
        df = pd.DataFrame(0, index=list_all_username, columns=list1_1950)
        length_of_users = 0

        for i in list_all_username:
            for index, row in df.iterrows():
                if list_all_liked_streamer_rank[length_of_users] != None:
                    for s in list_all_liked_streamer_rank[length_of_users].split(','):
                        if s in row:
                            df.set_value(i, s, 1)
            length_of_users = length_of_users+1
        # Compute User to User consine distance
        user_user = 1-pairwise_distances(df, metric="cosine")
        df_users = pd.DataFrame(user_user, columns=df.index, index=df.index)

        # Find the nearest username based on "Current User"
        current_user = str(session['username'])
        two_index_name = df_users.nlargest(2, current_user, keep='first').index
        if str(two_index_name[1]) == current_user:
            nearest_username = two_index_name[0]
        else:
            nearest_username = two_index_name[1]

        # Find the nearest user's email from SQL
        nearest_email = c.execute("SELECT email FROM users WHERE username = '{0}'".format(str(nearest_username)))
        nearest_email = c.fetchall()

        flash(nearest_username)
        flash(nearest_email[0][0])
        flash("This is the contact information of the one holding the same interest with you!")

        c.close()
        conn.close()

        return render_template("social.html")








# Test Page
# --------------------
@app.route('/test/', methods=["GET", "POST"])
def test():
    try:
        return render_template("test.html")
    except Exception as e:
        return str(e)





# 404 Error Page
# --------------------
@app.errorhandler(404)
def page_not_found(e):
    try:
        return render_template('404.html')
    except Exception as e:
        return str(e)