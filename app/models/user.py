import uuid
from datetime import datetime
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id            = db.Column(db.String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    nom           = db.Column(db.String(100), nullable=False)
    prenom        = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(150), nullable=False, unique=True, index=True)
    telephone     = db.Column(db.String(20),  nullable=False)
    type_compte   = db.Column(db.String(20),  nullable=False, default="courant")
    solde         = db.Column(db.Float,       nullable=False, default=0.0)
    numero_compte = db.Column(db.String(30),  nullable=False, unique=True,
                              default=lambda: f"BK{datetime.utcnow().strftime('%Y')}{str(uuid.uuid4().int)[:8]}")
    date_creation = db.Column(db.DateTime,    nullable=False, default=datetime.utcnow)
    actif         = db.Column(db.Boolean,     nullable=False, default=True)

    def to_dict(self):
        return {
            "id":            self.id,
            "nom":           self.nom,
            "prenom":        self.prenom,
            "email":         self.email,
            "telephone":     self.telephone,
            "type_compte":   self.type_compte,
            "solde":         round(self.solde, 2),
            "numero_compte": self.numero_compte,
            "date_creation": self.date_creation.isoformat(),
            "actif":         self.actif,
        }
