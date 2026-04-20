from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_mail import Mail, Message
import sqlite3
import os
from flask import send_file
import io
app = Flask(__name__)
app.secret_key = "secret123"

# 🔹 MAIL CONFIG
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'darshan5939r@gmail.com'   # your email
app.config['MAIL_PASSWORD'] = 'kfavsmpypufipkyd'        # NOT your normal password

mail = Mail(app)

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("database.db", timeout=5)
    c = conn.cursor()

    # 🔹 USERS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT
    )
    """)

    # 🔹 PROJECTS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY,
        title TEXT,
        description TEXT,
        tools TEXT,
        link TEXT
    )
    """)

    # 🔹 CERTIFICATES TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS certificates (
        id INTEGER PRIMARY KEY,
        title TEXT,
        issuer TEXT,
        image TEXT
    )
    """)

    # 🔹 PROFILE TABLE (BASE STRUCTURE)
    c.execute("""
    CREATE TABLE IF NOT EXISTS profile (
        id INTEGER PRIMARY KEY,
        name TEXT,
        role TEXT,
        bio TEXT,
        image TEXT
    )
    """)

    # 🔹 RESUME TABLE (ONLY ONE ROW)
    c.execute("""
    CREATE TABLE IF NOT EXISTS resume (
        id INTEGER PRIMARY KEY,
        filename TEXT
    )
    """)

    # ensure only one resume row exists
    c.execute("SELECT * FROM resume WHERE id=1")
    if not c.fetchone():
        c.execute("INSERT INTO resume (id, filename) VALUES (1, '')")

    # 🔥 ADD NEW COLUMNS SAFELY
    def add_column_if_not_exists(column_name):
        c.execute("PRAGMA table_info(profile)")
        columns = [col[1] for col in c.fetchall()]
        if column_name not in columns:
            c.execute(f"ALTER TABLE profile ADD COLUMN {column_name} TEXT")

    # EXISTING
    add_column_if_not_exists("skills")
    add_column_if_not_exists("linkedin")
    add_column_if_not_exists("github")
    add_column_if_not_exists("instagram")

    # 🔥 NEW CONTACT FIELDS
    add_column_if_not_exists("email")
    add_column_if_not_exists("location")
    add_column_if_not_exists("status")

    # 🔥 ENSURE ONLY ONE PROFILE ROW
    c.execute("SELECT * FROM profile")
    rows = c.fetchall()

    TOTAL_COLS = 12

    if len(rows) == 0:
        c.execute("""
        INSERT INTO profile 
        (id, name, role, bio, image, skills, linkedin, github, instagram, email, location, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1,
            'Your Name',
            'Your Role',
            'Your bio',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            ''
        ))

    elif len(rows) > 1:
        first = rows[0]
        c.execute("DELETE FROM profile")

        data = list(first) + [""] * (TOTAL_COLS - len(first))

        c.execute("""
        INSERT INTO profile 
        (id, name, role, bio, image, skills, linkedin, github, instagram, email, location, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data[:TOTAL_COLS])

    else:
        if rows[0][0] != 1:
            first = rows[0]
            c.execute("DELETE FROM profile")

            data = list(first) + [""] * (TOTAL_COLS - len(first))

            c.execute("""
            INSERT INTO profile 
            (id, name, role, bio, image, skills, linkedin, github, instagram, email, location, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (1, *data[1:TOTAL_COLS]))

    # 🔹 DEFAULT ADMIN USER
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", "admin123")
        )

    conn.commit()
    conn.close()

# ---------------- ROUTES ----------------

def is_logged_in():
    return "user" in session

@app.route("/")
def home():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM projects")
    projects = c.fetchall()

    c.execute("SELECT * FROM certificates")
    certificates = c.fetchall()

    # 🔥 ADD PROFILE
    c.execute("SELECT * FROM profile WHERE id=1")
    profile = c.fetchone()

    conn.close()

    return render_template(
        "index.html",
        projects=projects,
        certificates=certificates,
        profile=profile
    )


from flask import flash, session

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        result = c.fetchone()
        conn.close()

        if result:
            session["user"] = user
            return redirect("/admin")
        else:
            flash("Invalid username or password")   

    return render_template("login.html")

@app.route("/admin")
def admin():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM projects")
    projects = c.fetchall()
    conn.close()

    return render_template("admin.html", projects=projects)


@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    # 🔒 Check login
    if not is_logged_in():
        return redirect('/login')

    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']
            tools = request.form['tools']
            link = request.form['link']

            # 🔹 Basic validation
            if not title or not description:
                flash("Title and Description are required!", "error")
                return redirect('/add_project')

            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO projects (title, description, tools, link)
                VALUES (?, ?, ?, ?)
            """, (title, description, tools, link))

            conn.commit()
            conn.close()

            # 🟢 GREEN SUCCESS MESSAGE
            flash("Project added successfully!", "success")

            return redirect('/admin')

        except Exception as e:
            print("Add error:", e)
            flash("Failed to add project!", "error")
            return redirect('/add_project')

    return render_template('add_project.html')

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

from flask import flash, redirect
import sqlite3

@app.route('/delete_project/<int:id>', methods=['POST'])
def delete_project(id):
    if not is_logged_in():
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM projects WHERE id=?", (id,))
        conn.commit()

        # 🔴 RED (correct for delete)
        flash("Project deleted successfully!", "error")

    except Exception as e:
        print("Delete error:", e)
        flash("Failed to delete project!", "error")

    finally:
        conn.close()

    return redirect('/admin')   

@app.route('/edit_project/<int:id>')
def edit_project(id):
    if not is_logged_in():
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM projects WHERE id=?", (id,))
    project = cursor.fetchone()

    conn.close()

    if not project:
        return "Project not found", 404

    return render_template('edit_project.html', project=project)

@app.route('/update_project/<int:id>', methods=['POST'])
def update_project(id):
    if not is_logged_in():
        return redirect('/login')

    try:
        title = request.form['title']
        description = request.form['description']
        tools = request.form['tools']
        link = request.form['link']

        if not title or not description:
            flash("Title and Description are required!", "error")
            return redirect(url_for('edit_project', id=id))

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE projects 
            SET title=?, description=?, tools=?, link=? 
            WHERE id=?
        """, (title, description, tools, link, id))

        conn.commit()
        conn.close()

        flash("Project updated successfully", "success")

    except Exception as e:
        flash("Failed to update project", "error")

    return redirect(url_for('edit_project', id=id))

@app.route("/certificates")
def certificates_page():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM certificates")
    certificates = c.fetchall()
    conn.close()

    return render_template("certificates.html", certificates=certificates)


UPLOAD_FOLDER = "static/uploads"

# ensure folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
import uuid

@app.route("/add_certificate", methods=["GET", "POST"])
def add_certificate():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        issuer = request.form["issuer"]
        file = request.files["image"]

        filename = ""

        if file and file.filename != "":
            filename = str(uuid.uuid4()) + "_" + file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO certificates (title, issuer, image) VALUES (?, ?, ?)",
            (title, issuer, filename)
        )
        conn.commit()
        conn.close()

        flash("Certificate added successfully!")   # ✅ ADD THIS
        return redirect("/certificates")

    return render_template("add_certificate.html")

@app.route("/edit_certificate/<int:id>", methods=["GET", "POST"])
def edit_certificate(id):
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        issuer = request.form["issuer"]
        file = request.files.get("image")

        # get old image
        c.execute("SELECT image FROM certificates WHERE id=?", (id,))
        old_image = c.fetchone()[0]

        filename = old_image

        if file and file.filename != "":
            filename = str(uuid.uuid4()) + "_" + file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

        c.execute("""
            UPDATE certificates 
            SET title=?, issuer=?, image=? 
            WHERE id=?
        """, (title, issuer, filename, id))

        conn.commit()
        conn.close()

        return redirect("/certificates")

    c.execute("SELECT * FROM certificates WHERE id=?", (id,))
    cert = c.fetchone()
    conn.close()

    return render_template("edit_certificate.html", cert=cert)

@app.route("/delete_certificate/<int:id>", methods=["POST"])
def delete_certificate(id):
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # 🔹 get image filename
    c.execute("SELECT image FROM certificates WHERE id=?", (id,))
    img = c.fetchone()

    # 🔹 delete file from folder
    if img and img[0]:
        try:
            os.remove(os.path.join(UPLOAD_FOLDER, img[0]))
        except Exception as e:
            print("File delete error:", e)   # better than silent fail

    # 🔹 delete from DB
    c.execute("DELETE FROM certificates WHERE id=?", (id,))
    conn.commit()
    conn.close()

    flash("Certificate deleted successfully!")   # ✅ THIS LINE
    return redirect("/certificates")

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    print("PROFILE ROUTE HIT")

    if "user" not in session:
        print("NOT LOGGED IN")
        return redirect('/login')

    conn = sqlite3.connect('database.db', timeout=5)
    c = conn.cursor()

    if request.method == "POST":
        name = request.form.get('name')
        role = request.form.get('role')
        bio  = request.form.get('bio')
        skills = request.form.get('skills')
        linkedin = request.form.get('linkedin')
        github = request.form.get('github')
        instagram = request.form.get("instagram")
        email = request.form.get("email")
        location = request.form.get("location")
        status = request.form.get("status")

        file = request.files.get("image")

        if file and file.filename:
            filename = str(uuid.uuid4()) + "_" + file.filename
            file.save(os.path.join("static/uploads", filename))

            c.execute("""
            UPDATE profile
            SET name=?, role=?, bio=?, skills=?, linkedin=?, github=?, instagram=?, email=?, location=?, status=?, image=?
            WHERE id=1
            """, (
    name, role, bio, skills, linkedin, github, instagram,
    email, location, status, filename
            ))
        else:
           c.execute("""
            UPDATE profile
            SET name=?, role=?, bio=?, skills=?, linkedin=?, github=?, instagram=?, email=?, location=?, status=?
            WHERE id=1
                """, (
    name, role, bio, skills, linkedin, github, instagram,
    email, location, status
            ))

        conn.commit()
        conn.close()

        flash("Profile updated successfully ✅")
        return redirect('/profile')

    # GET request
    c.execute("SELECT * FROM profile WHERE id=1")
    profile = c.fetchone()
    conn.close()

    print("RETURNING TEMPLATE")
    return render_template('profile.html', profile=profile)

from flask import request, redirect, flash

@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    try:
        msg = Message(
            subject=f"Message from {name}",
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_USERNAME']]
        )

        msg.body = f"""
        Name: {name}
        Email: {email}

        Message:
        {message}
        """

        mail.send(msg)
        flash("Message sent successfully!", "success")

    except Exception as e:
        print(e)
        flash("Failed to send message!", "error")

    return redirect(url_for('home'))   # go back to home

@app.route("/upload_resume", methods=["GET", "POST"])
def upload_resume():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":
        file = request.files.get("resume")

        if file and file.filename.endswith(".pdf"):
            original_name = file.filename.strip()

            # 🔹 keep fixed filename (your current logic)
            filename = "resume.pdf"

            filepath = os.path.join("static/uploads", filename)
            file.save(filepath)

            # 🔹 store original name for display
            c.execute("UPDATE resume SET filename=? WHERE id=1", (original_name,))
            conn.commit()

            # 🟢 success message (with category)
            flash("Resume uploaded successfully!", "success")

            return redirect(url_for('upload_resume'))

        else:
            flash("Only PDF files are allowed!", "error")

    # 🔹 GET current resume
    c.execute("SELECT filename FROM resume WHERE id=1")
    result = c.fetchone()
    current_resume = result[0] if result and result[0] else None

    conn.close()

    return render_template("upload_resume.html", current_resume=current_resume)

@app.route('/download-resume')
def download_resume():
    filepath = os.path.join("static/uploads", "resume.pdf")

    if not os.path.exists(filepath):
        return "Resume not uploaded yet", 404

    return send_file(
        filepath,
        as_attachment=True
    )



if __name__ == "__main__":
    init_db()
    app.run(debug=True)
   