from dotenv import load_dotenv
load_dotenv()  # [OK] FIRST

import os
from flask import Flask, render_template, request, redirect, session, url_for, flash, send_file
from flask_mail import Mail, Message
import cloudinary
import cloudinary.uploader
import requests
from io import BytesIO
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
def get_db_connection():
    try:
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            print("DB CONNECTION ERROR: DATABASE_URL is not set!")
            return None
        # Log sanitized URL for debugging (hide password)
        safe_url = db_url.split("@")[-1] if "@" in db_url else "unknown"
        print(f"[DB] Connecting to: ...@{safe_url}")
        return psycopg2.connect(
            db_url,
            connect_timeout=10
        )
    except Exception as e:
        print("DB CONNECTION ERROR:", e)
        return None

def safe_db_connection():
    conn = get_db_connection()
    if not conn:
        print("DB connection failed")
        return None, None
    return conn, conn.cursor()

def is_logged_in():
    return "user" in session

app = Flask(__name__)

# [OK] FIXED SECRET KEY
app.secret_key = os.getenv("SECRET_KEY") or "fallback_secret_123"

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    return response

#  MAIL CONFIG
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")

mail = Mail(app)

#  CLOUDINARY CONFIG
cloudinary.config(
    cloud_name=os.environ.get("CLOUD_NAME"),
    api_key=os.environ.get("API_KEY"),
    api_secret=os.environ.get("API_SECRET")
)


@app.route("/")
def home():
    conn = get_db_connection()

    if not conn:
        print("[ERROR] DB connection failed in home()")
        return render_template(
            "index.html",
            projects=[],
            certificates=[],
            profile=None,
            education=[],
            experience=[]   # ✅ added
        )

    try:
        c = conn.cursor()

        c.execute("SELECT * FROM projects ORDER BY id DESC")
        projects = c.fetchall()

        c.execute("SELECT * FROM certificates ORDER BY id DESC")
        certificates = c.fetchall()

        c.execute("SELECT * FROM profile WHERE id=%s", (1,))
        profile = c.fetchone()

        c.execute("SELECT * FROM education ORDER BY id DESC")
        education = c.fetchall()

        # ✅ ADD THIS
        c.execute("SELECT * FROM experience ORDER BY id DESC")
        experience = c.fetchall()

    except Exception as e:
        print("[ERROR] HOME ERROR:", e)
        projects, certificates, profile, education, experience = [], [], None, [], []  # ✅ updated

    finally:
        if conn:
            conn.close()

    return render_template(
        "index.html",
        projects=projects,
        certificates=certificates,
        profile=profile,
        education=education,
        experience=experience   # ✅ added
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")

        #  Basic validation
        if not user or not pwd:
            flash("Username and password are required", "error")
            return redirect("/login")

        conn = None

        try:
            conn = get_db_connection()

            # [!] Handle DB failure
            if not conn:
                print("DB connection failed in login")
                flash("Database connection failed", "error")
                return redirect("/login")

            c = conn.cursor()

            # [OK] Fetch user
            c.execute("SELECT * FROM users WHERE username=%s", (user,))
            result = c.fetchone()

            print("DB result:", result)

            if result:
                stored_password = result[2]

                print("Stored hash:", stored_password)

                # [OK] Safe password check
                try:
                    match = check_password_hash(stored_password, pwd)
                except Exception as hash_error:
                    print("HASH ERROR:", hash_error)
                    flash("Password verification failed", "error")
                    return redirect("/login")

                print("Password match:", match)

                if match:
                    session["user"] = user
                    flash("Login successful", "success")
                    return redirect("/admin")
                else:
                    flash("Invalid username or password", "error")
            else:
                flash("Invalid username or password", "error")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print("LOGIN ERROR:", e)
            flash("Server error. Check logs.", "error")
            return redirect("/login")

        finally:
            if conn:
                conn.close()

    return render_template("login.html")

@app.route("/admin")
def admin():
    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()

    if not conn:
        print("DB connection failed in admin()")
        return "Database connection failed", 500

    try:
        c = conn.cursor()

        # 🔹 Projects
        c.execute("SELECT * FROM projects ORDER BY id DESC")
        projects = c.fetchall()

        # 🔹 Education
        c.execute("SELECT * FROM education ORDER BY id DESC")
        education = c.fetchall()

        # 🔥 ADD THIS (IMPORTANT)
        c.execute("SELECT * FROM project_screenshots ORDER BY id DESC")
        screenshots = c.fetchall()

    except Exception as e:
        print("ADMIN ERROR:", e)

        projects = []
        education = []
        screenshots = []   # 🔥 prevent crash

    finally:
        conn.close()

    return render_template(
        "admin.html",
        projects=projects,
        education=education,
        screenshots=screenshots   # 🔥 PASS TO TEMPLATE
    )


@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    #  Check login
    if not is_logged_in():
        return redirect('/login')

    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']
            tools = request.form['tools']
            link = request.form['link']

            #  Basic validation
            if not title or not description:
                flash("Title and Description are required!", "error")
                return redirect('/add_project')

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO projects (title, description, tools, link)
                VALUES (%s, %s, %s, %s)
            """, (title, description, tools, link))

            conn.commit()
            conn.close()

            flash("Project added successfully!", "success")
            return redirect('/admin')

        except Exception as e:
            print("Add error:", e)
            flash("Failed to add project!", "error")
            return redirect('/add_project')

    return render_template('add_project.html')

@app.route("/delete_project/<int:id>", methods=["POST"])
def delete_project(id):
    if not is_logged_in():
        return redirect("/login")

    try:
        conn = get_db_connection()
        c = conn.cursor()

        c.execute("DELETE FROM projects WHERE id=%s", (id,))
        conn.commit()

        flash("Project deleted successfully!", "error")

    except Exception as e:
        print("Delete Project Error:", e)
        flash("Failed to delete project", "error")

    finally:
        conn.close()

    return redirect("/admin")

@app.route("/admin/add_education", methods=["GET", "POST"])
def add_education():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    c = conn.cursor()

    if request.method == "POST":
        c.execute(
            "INSERT INTO education (degree, institution, year, description) VALUES (%s, %s, %s, %s)",
            (
                request.form["degree"],
                request.form["institution"],
                request.form["year"],
                request.form["description"]
            )
        )
        conn.commit()
        conn.close()

        flash("Education added successfully!", "success")

        # [OK] PRG pattern (keep this)
        return redirect(url_for("add_education"))

    # [OK] GET request  fetch data
    c.execute("SELECT * FROM education ORDER BY id DESC")
    education = c.fetchall()

    conn.close()

    return render_template("add_education.html", education=education)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


@app.route("/admin/edit_education/<int:id>", methods=["GET", "POST"])
def edit_education(id):
    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    c = conn.cursor()

    # Get existing data
    c.execute("SELECT * FROM education WHERE id=%s", (id,))
    edu = c.fetchone()

    if not edu:
        conn.close()
        return "Education not found", 404

    if request.method == "POST":
        degree = request.form.get("degree")
        institution = request.form.get("institution")
        year = request.form.get("year")
        description = request.form.get("description")

        #  Basic validation
        if not degree or not institution or not year:
            flash("All fields except description are required", "error")
            return render_template("edit_education.html", edu=edu)

        c.execute("""
            UPDATE education 
            SET degree=%s, institution=%s, year=%s, description=%s 
            WHERE id=%s
        """, (degree, institution, year, description, id))

        conn.commit()
        conn.close()

        flash("Education updated successfully!", "success")

        return redirect(url_for("add_education"))

    conn.close()
    return render_template("edit_education.html", edu=edu)


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

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE projects 
            SET title=%s, description=%s, tools=%s, link=%s 
            WHERE id=%s
        """, (title, description, tools, link, id))

        conn.commit()
        conn.close()

        flash("Project updated successfully", "success")

    except Exception as e:
        print("Update Error:", e)
        flash("Failed to update project", "error")

    return redirect(url_for('edit_project', id=id))

@app.route('/edit_project/<int:id>')
def edit_project(id):
    if not is_logged_in():
        return redirect('/login')

    conn = get_db_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM projects WHERE id=%s", (id,))
    project = c.fetchone()

    conn.close()

    if not project:
        return "Project not found", 404

    return render_template('edit_project.html', project=project)

@app.route("/certificates")
def certificates_page():
    if "user" not in session:
        flash("Please login first", "error")
        return redirect("/login")

    try:
        conn = get_db_connection()
        c = conn.cursor()

        c.execute("SELECT * FROM certificates ORDER BY id DESC")
        certificates = c.fetchall()

    except Exception as e:
        certificates = []
        print("DB Error:", e)
        flash("Failed to load certificates", "error")

    finally:
        conn.close()

    return render_template("certificates.html", certificates=certificates)

@app.route("/add_certificate", methods=["GET", "POST"])
def add_certificate():
    if "user" not in session:
        flash("Please login first", "error")
        return redirect("/login")

    if request.method == "POST":
        title = request.form.get("title")
        issuer = request.form.get("issuer")
        file = request.files.get("image")

        #  Basic validation
        if not title or not issuer:
            flash("Title and Issuer are required", "error")
            return redirect("/add_certificate")

        if not file or file.filename == "":
            flash("Please upload an image", "error")
            return redirect("/add_certificate")

        #  File type validation
        if not file.mimetype.startswith("image/"):
            flash("Only image files are allowed", "error")
            return redirect("/add_certificate")

        try:
            #  Upload to Cloudinary (UNCHANGED)
            upload_result = cloudinary.uploader.upload(
                file,
                folder="certificates"
            )
            image_url = upload_result["secure_url"]

            # [OK] PostgreSQL connection
            conn = get_db_connection()
            c = conn.cursor()

            c.execute(
                "INSERT INTO certificates (title, issuer, image) VALUES (%s, %s, %s)",
                (title, issuer, image_url)
            )

            conn.commit()
            conn.close()

            flash("Certificate added successfully!", "success")
            return redirect("/certificates")

        except Exception as e:
            print("Upload Error:", e)
            flash("Failed to upload certificate", "error")
            return redirect("/add_certificate")

    return render_template("add_certificate.html")

@app.route("/edit_certificate/<int:id>", methods=["GET", "POST"])
def edit_certificate(id):
    if "user" not in session:
        flash("Please login first", "error")
        return redirect("/login")

    conn = get_db_connection()
    c = conn.cursor()

    #  Check if certificate exists
    c.execute("SELECT * FROM certificates WHERE id=%s", (id,))
    cert = c.fetchone()

    if not cert:
        conn.close()
        flash("Certificate not found", "error")
        return redirect("/certificates")

    if request.method == "POST":
        title = request.form.get("title")
        issuer = request.form.get("issuer")
        file = request.files.get("image")

        #  Basic validation
        if not title or not issuer:
            flash("Title and Issuer are required", "error")
            return redirect(url_for("edit_certificate", id=id))

        image_url = cert[3]  # existing image

        #  If new file uploaded (UNCHANGED)
        if file and file.filename != "":
            if not file.mimetype.startswith("image/"):
                flash("Only image files are allowed", "error")
                return redirect(url_for("edit_certificate", id=id))

            try:
                upload_result = cloudinary.uploader.upload(
                    file,
                    folder="certificates"
                )
                image_url = upload_result["secure_url"]

            except Exception as e:
                print("Upload Error:", e)
                flash("Image upload failed", "error")
                return redirect(url_for("edit_certificate", id=id))

        try:
            c.execute("""
                UPDATE certificates 
                SET title=%s, issuer=%s, image=%s 
                WHERE id=%s
            """, (title, issuer, image_url, id))

            conn.commit()
            flash("Certificate updated successfully!", "success")

        except Exception as e:
            print("DB Error:", e)
            flash("Failed to update certificate", "error")

        finally:
            conn.close()

        return redirect("/certificates")

    conn.close()
    return render_template("edit_certificate.html", cert=cert)

@app.route("/delete_certificate/<int:id>", methods=["POST"])
def delete_certificate(id):
    if "user" not in session:
        flash("Please login first", "error")
        return redirect("/login")

    conn = get_db_connection()
    c = conn.cursor()

    try:
        #  Check if certificate exists
        c.execute("SELECT image FROM certificates WHERE id=%s", (id,))
        result = c.fetchone()

        if not result:
            flash("Certificate not found", "error")
            return redirect("/certificates")

        image_url = result[0]

        #  OPTIONAL: delete from Cloudinary (unchanged)

        #  Delete from DB
        c.execute("DELETE FROM certificates WHERE id=%s", (id,))
        conn.commit()

        flash("Certificate deleted successfully!", "success")

    except Exception as e:
        print("Delete Error:", e)
        flash("Failed to delete certificate", "error")

    finally:
        conn.close()

    return redirect("/certificates")

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if "user" not in session:
        flash("Please login first", "error")
        return redirect('/login')

    conn = get_db_connection()
    c = conn.cursor()

    #  Ensure profile exists
    c.execute("SELECT * FROM profile WHERE id=%s", (1,))
    profile_data = c.fetchone()

    if not profile_data:
        conn.close()
        flash("Profile not found", "error")
        return redirect('/')

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
        headline = request.form.get("headline")
        footer_text = request.form.get("footer_text")
        header_text = request.form.get("header_text")

        #  Basic validation
        if not name or not role:
            flash("Name and Role are required", "error")
            return redirect('/profile')

        image_url = profile_data[4]  # existing image

        #  Handle new image upload (UNCHANGED)
        if file and file.filename:
            if not file.mimetype.startswith("image/"):
                flash("Only image files are allowed", "error")
                return redirect('/profile')

            try:
                upload_result = cloudinary.uploader.upload(
                    file,
                    folder="profile"
                )
                image_url = upload_result["secure_url"]

            except Exception as e:
                print("Upload Error:", e)
                flash("Image upload failed", "error")
                return redirect('/profile')

        try:
            c.execute("""
                UPDATE profile
                SET name=%s, role=%s, bio=%s, skills=%s, linkedin=%s, github=%s,
                    instagram=%s, email=%s, location=%s, status=%s,
                    headline=%s, footer_text=%s, header_text=%s, image=%s
                WHERE id=%s
            """, (
                name, role, bio, skills, linkedin, github, instagram,
                email, location, status, headline, footer_text, header_text,
                image_url, 1
            ))

            conn.commit()
            flash("Profile updated successfully!", "success")

        except Exception as e:
            print("DB Error:", e)
            flash("Failed to update profile", "error")

        finally:
            conn.close()

        return redirect('/profile')

    conn.close()
    return render_template('profile.html', profile=profile_data)

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

    return redirect(url_for('home'))

@app.route("/upload_resume", methods=["GET", "POST"])
def upload_resume():
    if "user" not in session:
        flash("Please login first", "error")
        return redirect("/login")

    conn = get_db_connection()
    c = conn.cursor()

    if request.method == "POST":
        file = request.files.get("resume")

        #  Check file exists
        if not file or file.filename.strip() == "":
            flash("Please select a file", "error")
            conn.close()
            return redirect(url_for('upload_resume'))

        #  Validate extension
        if not file.filename.lower().endswith(".pdf"):
            flash("Only PDF files are allowed", "error")
            conn.close()
            return redirect(url_for('upload_resume'))

        try:
            original_name = file.filename.strip()

            #  Cloudinary upload (UNCHANGED)
            upload_result = cloudinary.uploader.upload(
                file,
                resource_type="raw",
                folder="resume"
            )

            file_url = upload_result["secure_url"]

            # [OK] PostgreSQL UPDATE
            c.execute(
                "UPDATE resume SET filename=%s, original_name=%s WHERE id=%s",
                (file_url, original_name, 1)
            )
            conn.commit()

            flash("Resume uploaded successfully!", "success")

        except Exception as e:
            print("Upload Error:", e)
            flash("Failed to upload resume", "error")

        finally:
            conn.close()

        return redirect(url_for('upload_resume'))

    #  GET current resume
    c.execute("SELECT original_name FROM resume WHERE id=%s", (1,))
    result = c.fetchone()
    current_resume = result[0] if result and result[0] else None

    conn.close()

    return render_template("upload_resume.html", current_resume=current_resume)


@app.route('/download-resume')
def download_resume():
    conn = get_db_connection()
    c = conn.cursor()

    #  get BOTH url + original name
    c.execute("SELECT filename, original_name FROM resume WHERE id=%s", (1,))
    result = c.fetchone()
    conn.close()

    if not result or not result[0]:
        return "Resume not uploaded yet", 404

    file_url = result[0]
    original_name = result[1] or "resume.pdf"

    try:
        #  fetch file (UNCHANGED)
        response = requests.get(file_url)
        response.raise_for_status()

        #  send file with correct name
        return send_file(
            BytesIO(response.content),
            as_attachment=True,
            download_name=original_name,
            mimetype="application/pdf"
        )

    except Exception as e:
        print("Download error:", e)
        return "Failed to download resume", 500
    
@app.route("/delete_education/<int:id>", methods=["POST"])
def delete_education(id):
    if "user" not in session:
        return redirect(url_for("login"))

    try:
        conn = get_db_connection()
        c = conn.cursor()

        c.execute("DELETE FROM education WHERE id=%s", (id,))
        conn.commit()

        flash("Education deleted successfully!", "danger")

    except Exception as e:
        print("Delete Error:", e)
        flash("Failed to delete education", "error")

    finally:
        conn.close()

    return redirect(url_for("add_education"))

from flask import flash   # 🔹 make sure this is imported

@app.route("/add_experience", methods=["GET", "POST"])
def add_experience():
    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    c = conn.cursor()

    if request.method == "POST":
        role = request.form.get("role")
        company = request.form.get("company")
        duration = request.form.get("duration")
        description = request.form.get("description")

        c.execute(
            "INSERT INTO experience (role, company, duration, description) VALUES (%s, %s, %s, %s)",
            (role, company, duration, description)
        )
        conn.commit()

        flash("Experience Added Successfully", "success")  # ✅ ADD THIS

        return redirect("/add_experience")

    c.execute("SELECT * FROM experience ORDER BY id DESC")
    experience = c.fetchall()

    conn.close()

    return render_template("add_experience.html", experience=experience)


@app.route("/update_experience/<int:id>", methods=["POST"])
def update_experience(id):
    if "user" not in session:
        return redirect("/login")

    role = request.form.get("role")
    company = request.form.get("company")
    duration = request.form.get("duration")
    description = request.form.get("description")

    conn = get_db_connection()
    c = conn.cursor()

    c.execute(
        "UPDATE experience SET role=%s, company=%s, duration=%s, description=%s WHERE id=%s",
        (role, company, duration, description, id)
    )

    conn.commit()
    conn.close()

    flash("Experience Updated Successfully", "success")  # ✅ correct message

    return redirect("/add_experience")

from flask import flash

@app.route("/delete_experience/<int:id>", methods=["POST"])
def delete_experience(id):
    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    c = conn.cursor()

    c.execute("DELETE FROM experience WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    flash("Experience Deleted Successfully", "danger")  # ✅ add this

    return redirect("/add_experience")

@app.route("/upload_screenshot/<int:project_id>", methods=["POST"])
def upload_screenshot(project_id):
    if "user" not in session:
        return redirect("/login")

    file = request.files.get("image")

    if not file:
        flash("No file selected", "error")
        return redirect("/admin")

    try:
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(file)
        image_url = upload_result["secure_url"]

        # Save to DB
        conn = get_db_connection()
        c = conn.cursor()

        c.execute(
            "INSERT INTO project_screenshots (project_id, image_url) VALUES (%s, %s)",
            (project_id, image_url)
        )

        conn.commit()
        conn.close()

        flash("Screenshot uploaded successfully!", "success")

    except Exception as e:
        print("UPLOAD ERROR:", e)
        flash("Failed to upload screenshot", "error")

    return redirect("/admin")

@app.route("/project/<int:project_id>/screenshots")
def project_screenshots(project_id):
    conn = get_db_connection()
    c = conn.cursor()

    # Get project title
    c.execute("SELECT title FROM projects WHERE id=%s", (project_id,))
    project = c.fetchone()
    project_title = project[0] if project else "Project"

    # Get screenshots for this project
    c.execute(
        "SELECT image_url FROM project_screenshots WHERE project_id=%s",
        (project_id,)
    )
    images = c.fetchall()

    conn.close()

    return render_template("project_screenshots.html", images=images, project_title=project_title)

@app.route("/delete_screenshot/<int:id>", methods=["POST"])
def delete_screenshot(id):
    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    c = conn.cursor()

    try:
        # 🔹 Get image URL first
        c.execute("SELECT image_url FROM project_screenshots WHERE id=%s", (id,))
        result = c.fetchone()

        if result:
            image_url = result[0]

            # 🔥 Extract public_id from URL
            import cloudinary.uploader
            public_id = image_url.split("/")[-1].split(".")[0]

            # 🔥 Delete from Cloudinary
            cloudinary.uploader.destroy(public_id)

        # 🔹 Delete from DB
        c.execute("DELETE FROM project_screenshots WHERE id=%s", (id,))
        conn.commit()

    except Exception as e:
        print("DELETE ERROR:", e)

    finally:
        conn.close()

    return redirect("/admin")

if __name__ == "__main__":
    app.run(debug=True)