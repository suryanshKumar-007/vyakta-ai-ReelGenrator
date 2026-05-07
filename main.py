from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'webm', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vyakta.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'vyakta-secret-key'

db = SQLAlchemy(app)


# ── Database Model ──
class Reel(db.Model):
    id            = db.Column(db.String(100), primary_key=True)
    title         = db.Column(db.String(200), nullable=True)
    desc          = db.Column(db.Text, nullable=True)
    video_file    = db.Column(db.String(200), nullable=True)
    image_file    = db.Column(db.String(200), nullable=True)
    has_thumbnail = db.Column(db.Boolean, default=False)
    views         = db.Column(db.Integer, default=0)
    likes         = db.Column(db.Integer, default=0)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title or "Untitled Reel",
            "desc": self.desc,
            "video_file": self.video_file,
            "image_file": self.image_file,
            "has_thumbnail": self.has_thumbnail,
            "thumbnail_url": url_for('thumbnail', rec_id=self.id) if self.has_thumbnail else None,
            "views": self.views,
            "likes": self.likes,
            "created_at": self.created_at.strftime("%d %b %Y"),
        }


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    reels = [r.to_dict() for r in Reel.query.order_by(Reel.created_at.desc()).limit(8).all()]
    return render_template("index.html", reels=reels)


@app.route("/create", methods=["GET", "POST"])
def create():
    myid = str(uuid.uuid1())

    if request.method == "POST":
        rec_id = request.form.get("uuid")
        desc   = request.form.get("desc")

        if not rec_id:
            flash("Something went wrong. Please try again.", "error")
            return redirect(url_for('create'))

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        files_saved = False
        image_file  = None

        for key, file in request.files.items():
            if file.filename == '':
                continue
            if not allowed_file(file.filename):
                flash(f"File type not allowed: {file.filename}", "error")
                continue

            filename   = secure_filename(file.filename)
            rec_folder = os.path.join(app.config['UPLOAD_FOLDER'], rec_id)
            os.makedirs(rec_folder, exist_ok=True)
            file.save(os.path.join(rec_folder, filename))
            files_saved = True

            if filename.rsplit('.', 1)[-1].lower() in {'jpg', 'jpeg', 'png'}:
                image_file = filename

        if rec_id and desc:
            rec_folder = os.path.join(app.config['UPLOAD_FOLDER'], rec_id)
            os.makedirs(rec_folder, exist_ok=True)
            with open(os.path.join(rec_folder, "desc.txt"), "w") as f:
                f.write(desc)

        # Database mein save karo
        reel = Reel(
            id            = rec_id,
            title         = desc[:40] if desc else "Untitled Reel",
            desc          = desc,
            image_file    = image_file,
            has_thumbnail = False,
        )
        db.session.add(reel)
        db.session.commit()

        if files_saved:
            flash("Reel created! Processing ho raha hai...", "success")

        return redirect(url_for('gallery'))

    return render_template("create.html", myid=myid)


@app.route("/gallery")
def gallery():
    reels = [r.to_dict() for r in Reel.query.order_by(Reel.created_at.desc()).all()]
    return render_template("gallery.html", reels=reels)


@app.route("/thumbnail/<rec_id>")
def thumbnail(rec_id):
    folder = os.path.join(app.config['UPLOAD_FOLDER'], rec_id)
    thumb  = os.path.join(folder, "thumbnail.jpg")

    if os.path.exists(thumb):
        return send_from_directory(folder, "thumbnail.jpg")

    for f in os.listdir(folder):
        if f.rsplit('.', 1)[-1].lower() in {'jpg', 'jpeg', 'png'}:
            return send_from_directory(folder, f)

    return "", 404


@app.route("/reel/<rec_id>")
def serve_reel(rec_id):
    folder = os.path.join(app.config['UPLOAD_FOLDER'], rec_id)

    # View count badhao
    reel = db.session.get(Reel, rec_id)
    if reel:
        reel.views += 1
        db.session.commit()

    return send_from_directory(folder, "reel.mp4")


# Like button ke liye
@app.route("/like/<rec_id>", methods=["POST"])
def like_reel(rec_id):
    reel = db.session.get(Reel, rec_id)
    if reel:
        reel.likes += 1
        db.session.commit()
        return {"likes": reel.likes}, 200
    return {"error": "Not found"}, 404


# generate_process.py thumbnail banne ke baad yeh call karega
@app.route("/update_thumbnail/<rec_id>", methods=["POST"])
def update_thumbnail(rec_id):
    reel = db.session.get(Reel, rec_id)
    if reel:
        thumb_path = os.path.join(app.config['UPLOAD_FOLDER'], rec_id, "thumbnail.jpg")
        reel.has_thumbnail = os.path.exists(thumb_path)
        reel.video_file    = "reel.mp4"
        db.session.commit()
        return {"status": "updated"}, 200
    return {"error": "Not found"}, 404


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)