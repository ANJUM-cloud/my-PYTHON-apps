import os
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-this-secret"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///app.db").replace("postgres://", "postgresql://", 1),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
    )
    if test_config: app.config.update(test_config)
    db.init_app(app); login_manager.init_app(app); login_manager.login_view = "login"
    csrf.init_app(app)

    class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(255), unique=True, nullable=False, index=True)
        password_hash = db.Column(db.String(255), nullable=False)
        created_at = db.Column(db.DateTime, server_default=db.func.now())
        items = db.relationship("Application", backref="owner", lazy=True, cascade="all, delete-orphan")
        def set_password(self, password): self.password_hash = generate_password_hash(password)
        def check_password(self, password): return check_password_hash(self.password_hash, password)

    class Application(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(160), nullable=False)
        description = db.Column(db.Text, default="")
        company = db.Column(db.String(160), default="")
        status = db.Column(db.String(30), default="Applied")
        follow_up = db.Column(db.Date, nullable=True)
        user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
        created_at = db.Column(db.DateTime, server_default=db.func.now())

    @login_manager.user_loader
    def load_user(user_id): return db.session.get(User, int(user_id))

    @app.context_processor
    def globals_for_templates(): return {"app_title": "CareerTrack"}

    @app.route("/")
    def index():
        return redirect(url_for("dashboard")) if current_user.is_authenticated else render_template("landing.html")

    @app.route("/register", methods=["GET","POST"])
    def register():
        if current_user.is_authenticated: return redirect(url_for("dashboard"))
        if request.method == "POST":
            email = request.form.get("email","").strip().lower()
            password = request.form.get("password","")
            if len(password) < 10: flash("Password must contain at least 10 characters.", "error")
            elif not email or User.query.filter_by(email=email).first(): flash("Enter a valid, unused email.", "error")
            else:
                user = User(email=email); user.set_password(password); db.session.add(user); db.session.commit()
                login_user(user); return redirect(url_for("dashboard"))
        return render_template("auth.html", mode="Create account")

    @app.route("/login", methods=["GET","POST"])
    def login():
        if request.method == "POST":
            user = User.query.filter_by(email=request.form.get("email","").strip().lower()).first()
            if user and user.check_password(request.form.get("password","")):
                login_user(user); return redirect(url_for("dashboard"))
            flash("Email or password was not recognised.", "error")
        return render_template("auth.html", mode="Sign in")

    @app.post("/logout")
    @login_required
    def logout():
        logout_user(); return redirect(url_for("index"))

    @app.get("/dashboard")
    @login_required
    def dashboard():
        items = Application.query.filter_by(user_id=current_user.id).order_by(Application.created_at.desc()).all()
        return render_template("dashboard.html", items=items, total=len(items))

    @app.post("/items/create")
    @login_required
    def create_item():
        try:
            title = request.form.get("title", "").strip()
            if not title: flash("Role title is required.", "error"); return redirect(url_for("dashboard"))
            raw = request.form.get("follow_up", "").strip()
            item = Application(title=title, description=request.form.get("description","").strip(),
                               company=request.form.get("company","").strip(), status=request.form.get("status","Applied"),
                               follow_up=date.fromisoformat(raw) if raw else None, user_id=current_user.id)
            db.session.add(item); db.session.commit(); flash("Record created.", "success")
        except (ValueError, TypeError):
            db.session.rollback(); flash("Please check the values entered.", "error")
        return redirect(url_for("dashboard"))

    @app.post("/items/<int:item_id>/update")
    @login_required
    def update_item(item_id):
        item = db.session.get(Application, item_id)
        if not item or item.user_id != current_user.id: abort(404)
        try:
            item.title = request.form.get("title", "").strip()
            item.description = request.form.get("description", "").strip()
            item.company = request.form.get("company", "").strip()
            item.status = request.form.get("status", "Applied")
            raw = request.form.get("follow_up", "").strip()
            item.follow_up = date.fromisoformat(raw) if raw else None
            if not item.title: flash("Role title is required.", "error"); return redirect(url_for("dashboard"))
            db.session.commit(); flash("Record updated.", "success")
        except (ValueError, TypeError):
            db.session.rollback(); flash("Please check the values entered.", "error")
        return redirect(url_for("dashboard"))

    @app.post("/items/<int:item_id>/delete")
    @login_required
    def delete_item(item_id):
        item = db.session.get(Application, item_id)
        if not item or item.user_id != current_user.id: abort(404)
        db.session.delete(item); db.session.commit(); flash("Record deleted.", "success")
        return redirect(url_for("dashboard"))

    @app.get("/health")
    def health(): return {"status":"ok","application":"careertrack"}, 200

    with app.app_context(): db.create_all()
    return app

app = create_app()
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT",5000)), debug=os.environ.get("FLASK_DEBUG") == "1")
