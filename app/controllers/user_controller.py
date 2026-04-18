import math
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user import User
from app.models.transaction import Transaction

user_bp = Blueprint("users", __name__)

VALID_TYPES = ["courant", "epargne", "entreprise"]


# ════════════════════════════════════════════════
# POST /api/users/        — Ajouter un utilisateur
# ════════════════════════════════════════════════
@user_bp.route("/", methods=["POST"])
def add_user():
    """
    Ajouter un nouvel utilisateur
    ---
    tags:
      - Utilisateurs
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [nom, prenom, email, telephone]
          properties:
            nom:
              type: string
              example: Dupont
            prenom:
              type: string
              example: Jean
            email:
              type: string
              example: jean.dupont@email.com
            telephone:
              type: string
              example: "+237612345678"
            type_compte:
              type: string
              enum: [courant, epargne, entreprise]
              example: courant
    responses:
      201:
        description: Utilisateur créé avec succès
      400:
        description: Données invalides
      500:
        description: Erreur serveur
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Corps JSON manquant"}), 400

        # Vérification des champs obligatoires
        manquants = [f for f in ["nom", "prenom", "email", "telephone"] if not data.get(f)]
        if manquants:
            return jsonify({"success": False, "message": f"Champs manquants : {', '.join(manquants)}"}), 400

        # Email unique
        if User.query.filter_by(email=data["email"].strip().lower()).first():
            return jsonify({"success": False, "message": "Cet email est déjà utilisé"}), 400

        # Type de compte
        type_compte = data.get("type_compte", "courant")
        if type_compte not in VALID_TYPES:
            return jsonify({"success": False, "message": f"type_compte invalide. Valeurs acceptées : {VALID_TYPES}"}), 400

        user = User(
            nom=data["nom"].strip(),
            prenom=data["prenom"].strip(),
            email=data["email"].strip().lower(),
            telephone=data["telephone"].strip(),
            type_compte=type_compte,
        )
        db.session.add(user)
        db.session.commit()

        return jsonify({"success": True, "message": "Utilisateur créé avec succès", "data": user.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ════════════════════════════════════════════════
# GET /api/users/         — Liste des utilisateurs
# ════════════════════════════════════════════════
@user_bp.route("/", methods=["GET"])
def get_users():
    """
    Lister tous les utilisateurs
    ---
    tags:
      - Utilisateurs
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: limit
        type: integer
        default: 10
      - in: query
        name: type_compte
        type: string
        enum: [courant, epargne, entreprise]
    responses:
      200:
        description: Liste retournée avec succès
    """
    try:
        page  = max(1, int(request.args.get("page", 1)))
        limit = min(100, max(1, int(request.args.get("limit", 10))))
        query = User.query

        if request.args.get("type_compte"):
            query = query.filter_by(type_compte=request.args.get("type_compte"))

        total = query.count()
        users = query.offset((page - 1) * limit).limit(limit).all()

        return jsonify({
            "success": True,
            "total":   total,
            "page":    page,
            "limit":   limit,
            "pages":   math.ceil(total / limit) if total > 0 else 1,
            "data":    [u.to_dict() for u in users],
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ════════════════════════════════════════════════
# GET /api/users/<id>     — Détail d'un utilisateur
# ════════════════════════════════════════════════
@user_bp.route("/<user_id>", methods=["GET"])
def get_user(user_id):
    """
    Obtenir un utilisateur par son ID
    ---
    tags:
      - Utilisateurs
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
    responses:
      200:
        description: Utilisateur trouvé
      404:
        description: Utilisateur introuvable
    """
    try:
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"success": False, "message": "Utilisateur introuvable"}), 404
        return jsonify({"success": True, "data": user.to_dict()}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ════════════════════════════════════════════════
# PUT /api/users/<id>     — Modifier un utilisateur
# ════════════════════════════════════════════════
@user_bp.route("/<user_id>", methods=["PUT"])
def update_user(user_id):
    """
    Modifier un utilisateur
    ---
    tags:
      - Utilisateurs
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            nom:
              type: string
            prenom:
              type: string
            telephone:
              type: string
            type_compte:
              type: string
              enum: [courant, epargne, entreprise]
    responses:
      200:
        description: Utilisateur mis à jour
      404:
        description: Utilisateur introuvable
    """
    try:
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"success": False, "message": "Utilisateur introuvable"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Corps JSON manquant"}), 400

        for champ in ["nom", "prenom", "telephone"]:
            if champ in data:
                setattr(user, champ, data[champ])

        if "type_compte" in data:
            if data["type_compte"] not in VALID_TYPES:
                return jsonify({"success": False, "message": "type_compte invalide"}), 400
            user.type_compte = data["type_compte"]

        db.session.commit()
        return jsonify({"success": True, "message": "Utilisateur mis à jour", "data": user.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ════════════════════════════════════════════════
# DELETE /api/users/<id>  — Suppression définitive (admin)
# ════════════════════════════════════════════════
@user_bp.route("/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    """
    Supprimer définitivement un utilisateur (admin uniquement)
    ---
    tags:
      - Utilisateurs
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
      - in: header
        name: X-Admin-Key
        type: string
        required: true
        description: Clé secrète administrateur
    responses:
      200:
        description: Utilisateur supprimé définitivement
      401:
        description: Clé admin invalide
      404:
        description: Utilisateur introuvable
    """
    try:
        # Vérification clé admin dans le header
        admin_key = request.headers.get("X-Admin-Key", "")
        if admin_key != "admin-secret-2024":
            return jsonify({"success": False, "message": "Accès refusé. Clé administrateur invalide"}), 401

        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"success": False, "message": "Utilisateur introuvable"}), 404

        # Suppression des transactions liées puis de l'utilisateur
        Transaction.query.filter_by(user_id=user_id).delete()
        db.session.delete(user)
        db.session.commit()

        return jsonify({"success": True, "message": f"Utilisateur {user.prenom} {user.nom} supprimé définitivement"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ════════════════════════════════════════════════
# POST /api/users/<id>/depot   — Dépôt
# ════════════════════════════════════════════════
@user_bp.route("/<user_id>/depot", methods=["POST"])
def depot(user_id):
    """
    Effectuer un dépôt sur le compte d'un utilisateur
    ---
    tags:
      - Transactions
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [montant]
          properties:
            montant:
              type: number
              example: 50000
            description:
              type: string
              example: "Dépôt espèces guichet"
    responses:
      200:
        description: Dépôt effectué avec succès
      400:
        description: Montant invalide
      404:
        description: Utilisateur introuvable
    """
    try:
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"success": False, "message": "Utilisateur introuvable"}), 404

        if not user.actif:
            return jsonify({"success": False, "message": "Compte désactivé"}), 400

        data = request.get_json()
        montant = data.get("montant") if data else None

        if montant is None or montant <= 0:
            return jsonify({"success": False, "message": "Le montant doit être supérieur à 0"}), 400

        solde_avant  = user.solde
        user.solde  += montant
        solde_apres  = user.solde

        transaction = Transaction(
            user_id=user_id,
            type_op="depot",
            montant=montant,
            solde_avant=solde_avant,
            solde_apres=solde_apres,
            description=data.get("description", "Dépôt"),
        )
        db.session.add(transaction)
        db.session.commit()

        return jsonify({
            "success":     True,
            "message":     f"Dépôt de {montant} effectué avec succès",
            "solde_avant": solde_avant,
            "solde_apres": solde_apres,
            "transaction": transaction.to_dict(),
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ════════════════════════════════════════════════
# POST /api/users/<id>/retrait — Retrait
# ════════════════════════════════════════════════
@user_bp.route("/<user_id>/retrait", methods=["POST"])
def retrait(user_id):
    """
    Effectuer un retrait sur le compte d'un utilisateur
    ---
    tags:
      - Transactions
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [montant]
          properties:
            montant:
              type: number
              example: 10000
            description:
              type: string
              example: "Retrait GAB"
    responses:
      200:
        description: Retrait effectué avec succès
      400:
        description: Solde insuffisant ou montant invalide
      404:
        description: Utilisateur introuvable
    """
    try:
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"success": False, "message": "Utilisateur introuvable"}), 404

        if not user.actif:
            return jsonify({"success": False, "message": "Compte désactivé"}), 400

        data = request.get_json()
        montant = data.get("montant") if data else None

        if montant is None or montant <= 0:
            return jsonify({"success": False, "message": "Le montant doit être supérieur à 0"}), 400

        if montant > user.solde:
            return jsonify({
                "success": False,
                "message": f"Solde insuffisant. Solde disponible : {round(user.solde, 2)}"
            }), 400

        solde_avant  = user.solde
        user.solde  -= montant
        solde_apres  = user.solde

        transaction = Transaction(
            user_id=user_id,
            type_op="retrait",
            montant=montant,
            solde_avant=solde_avant,
            solde_apres=solde_apres,
            description=data.get("description", "Retrait"),
        )
        db.session.add(transaction)
        db.session.commit()

        return jsonify({
            "success":     True,
            "message":     f"Retrait de {montant} effectué avec succès",
            "solde_avant": solde_avant,
            "solde_apres": solde_apres,
            "transaction": transaction.to_dict(),
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ════════════════════════════════════════════════
# GET /api/users/<id>/transactions — Historique
# ════════════════════════════════════════════════
@user_bp.route("/<user_id>/transactions", methods=["GET"])
def get_transactions(user_id):
    """
    Historique des transactions d'un utilisateur
    ---
    tags:
      - Transactions
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
    responses:
      200:
        description: Historique retourné
      404:
        description: Utilisateur introuvable
    """
    try:
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"success": False, "message": "Utilisateur introuvable"}), 404

        transactions = Transaction.query.filter_by(user_id=user_id)\
                                        .order_by(Transaction.date_op.desc()).all()

        return jsonify({
            "success": True,
            "total":   len(transactions),
            "data":    [t.to_dict() for t in transactions],
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
