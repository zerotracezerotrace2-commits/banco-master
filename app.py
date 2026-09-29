from flask import Flask,render_template,request,redirect,session
import sqlite3
from werkzeug.security import check_password_hash
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import uuid
import os

app=Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave-local-desenvolvimento")

def db():
    c = sqlite3.connect("banco.db")
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    return c

@app.route("/",methods=["GET","POST"])
def login():
    if request.method=="POST":
        c=db()
        r=c.execute("""SELECT users.*,clients.name,accounts.agency,
        accounts.account_number,accounts.balance_cents
        FROM users LEFT JOIN accounts ON accounts.id=users.account_id
        LEFT JOIN clients ON clients.id=accounts.client_id
        WHERE users.username=?""",(request.form["username"].strip(),)).fetchone()
        c.close()
        if r and check_password_hash(r["password_hash"],request.form["password"]):
            session["user_id"]=r["id"]
            return redirect("/dashboard")
        return render_template("login.html",erro="Usuário ou senha inválidos")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    c = db()

    r = c.execute("""
        SELECT users.*, clients.name, accounts.agency,
               accounts.account_number, accounts.balance_cents
        FROM users
        LEFT JOIN accounts ON accounts.id = users.account_id
        LEFT JOIN clients ON clients.id = accounts.client_id
        WHERE users.id=?
    """, (session["user_id"],)).fetchone()

    ts = c.execute("""
        SELECT created_at, type, amount_cents, description
        FROM transactions
        WHERE account_id=?
        ORDER BY id DESC
    """, (r["account_id"],)).fetchall()

    c.close()

    trans = [
        dict(x, amount=f'{x["amount_cents"] / 100:.2f}')
        for x in ts
    ]

    return render_template(
        "dashboard.html",
        name=r["name"] or "Administrador",
        agency=r["agency"],
        account=r["account_number"],
        balance=f'{r["balance_cents"] / 100:.2f}',
        transactions=trans,
        erro=request.args.get("erro"),
        sucesso=request.args.get("sucesso")
    )


@app.route("/pix", methods=["POST"])
def pix():
    if "user_id" not in session:
        return redirect("/")

    dest = request.form.get("destination", "").strip()
    raw_amount = request.form.get("amount", "").strip()
    desc = request.form.get("description", "").strip()

    try:
        raw = raw_amount.strip()

        if "," in raw and "." in raw:
            raw = raw.replace(".", "").replace(",", ".")
        elif "," in raw:
            raw = raw.replace(",", ".")

        value = Decimal(raw)
        amount = int((value * 100).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP
        ))
    except (InvalidOperation, ValueError):
        return redirect("/dashboard?erro=Valor+invalido")

    if amount <= 0:
        return redirect("/dashboard?erro=O+valor+deve+ser+maior+que+zero")

    c = db()

    try:
        c.execute("BEGIN")

        sender_row = c.execute(
            "SELECT account_id FROM users WHERE id=?",
            (session["user_id"],)
        ).fetchone()

        if not sender_row:
            raise ValueError("Usuário inválido")

        sender = sender_row["account_id"]

        receiver = c.execute(
            "SELECT id FROM accounts WHERE account_number=?",
            (dest,)
        ).fetchone()

        if not receiver:
            raise ValueError("Conta destino não encontrada")

        if receiver["id"] == sender:
            raise ValueError("Não é possível transferir para a própria conta")

        balance = c.execute(
            "SELECT balance_cents FROM accounts WHERE id=?",
            (sender,)
        ).fetchone()["balance_cents"]

        if balance < amount:
            raise ValueError("Saldo insuficiente")

        now = datetime.now().isoformat(timespec="seconds")
        transaction_id = str(uuid.uuid4())

        c.execute(
            "UPDATE accounts SET balance_cents=balance_cents-? WHERE id=?",
            (amount, sender)
        )

        c.execute(
            "UPDATE accounts SET balance_cents=balance_cents+? WHERE id=?",
            (amount, receiver["id"])
        )

        c.execute(
            """INSERT INTO transactions
            (account_id,type,amount_cents,description,created_at)
            VALUES(?,?,?,?,?)""",
            (sender, "SAÍDA", amount, desc, now)
        )

        c.execute(
            """INSERT INTO transactions
            (account_id,type,amount_cents,description,created_at)
            VALUES(?,?,?,?,?)""",
            (receiver["id"], "ENTRADA", amount, desc, now)
        )

        c.execute(
            """INSERT INTO pix_transactions
            (transaction_id,sender_account_id,receiver_account_id,
             amount_cents,description,created_at)
            VALUES(?,?,?,?,?,?)""",
            (transaction_id, sender, receiver["id"], amount, desc, now)
        )

        c.commit()

    except ValueError as e:
        c.rollback()
        c.close()
        return redirect("/dashboard?erro=" + str(e).replace(" ", "+"))

    except Exception:
        c.rollback()
        c.close()
        return redirect("/dashboard?erro=Erro+ao+processar+Pix")

    c.close()
    return redirect("/dashboard?sucesso=Pix+enviado+com+sucesso")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)

