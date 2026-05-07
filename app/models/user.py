import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id            = db.Column(db.String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    nom           = db.Column(db.String(100), nullable=False)
    prenom        = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(150), nullable=False, unique=True, index=True)
    telephone     = db.Column(db.String(20),  nullable=False)
    type_compte   = db.Column(db.String(20),  nullable=False, default="courant")
    banque        = db.Column(db.String(50),  nullable=False, default="UBA")
    solde         = db.Column(db.Float,       nullable=False, default=0.0)
    numero_compte = db.Column(db.String(30),  nullable=False, unique=True,
                              default=lambda: f"BK{datetime.utcnow().strftime('%Y')}{str(uuid.uuid4().int)[:8]}")
    password_hash = db.Column(db.String(256), nullable=True)
    date_creation = db.Column(db.DateTime,    nullable=False, default=datetime.utcnow)
    actif         = db.Column(db.Boolean,     nullable=False, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id":            self.id,
            "nom":           self.nom,
            "prenom":        self.prenom,
            "email":         self.email,
            "telephone":     self.telephone,
            "type_compte":   self.type_compte,
            "banque":        self.banque,
            "solde":         round(self.solde, 2),
            "numero_compte": self.numero_compte,
            "date_creation": self.date_creation.isoformat(),
            "actif":         self.actif,
        }
