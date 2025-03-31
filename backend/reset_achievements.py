from routes import create_app
from models import db, User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='jolivenc').first()
    user.achievements = None
    db.session.commit()
    print("✅ Achievements reset to NULL for jolivenc")

