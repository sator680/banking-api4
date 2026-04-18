import uuid
from datetime import datetime
from app.extensions import db


class Transaction(db.Model):
    __tablename__ = "transactions"

    id         = db.Column(db.String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id    = db.Column(db.String(36),  db.ForeignKey("users.id"), nullable=False, index=True)
    type_op    = db.Column(db.String(20),  nullable=False)   # "depot" ou "retrait"
    montant    = db.Column(db.Float,       nullable=False)
    solde_avant= db.Column(db.Float,       nullable=False)
    solde_apres= db.Column(db.Float,       nullable=False)
    description= db.Column(db.String(255), nullable=True)
    date_op    = db.Column(db.DateTime,    nullable=False, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("transactions", lazy=True))

    def to_dict(self):
        return {
            "id":          self.id,
            "user_id":     self.user_id,
            "type_op":     self.type_op,
            "montant":     round(self.montant, 2),
            "solde_avant": round(self.solde_avant, 2),
            "solde_apres": round(self.solde_apres, 2),
            "description": self.description,
            "date_op":     self.date_op.isoformat(),
        }
