import sqlite3

DB = "banco.db"

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def teste_estrutura():
    c = db()

    clientes = c.execute(
        "SELECT COUNT(*) FROM clients"
    ).fetchone()[0]

    contas = c.execute(
        "SELECT COUNT(*) FROM accounts"
    ).fetchone()[0]

    usuarios = c.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    assert clientes == 50
    assert contas == 51
    assert usuarios == 51

    c.close()


def teste_admin():
    c = db()

    admin = c.execute(
        "SELECT account_id FROM users WHERE username='admin'"
    ).fetchone()

    assert admin is not None
    assert admin["account_id"] == 51

    conta = c.execute(
        "SELECT account_number, agency, balance_cents "
        "FROM accounts WHERE account_number='000001'"
    ).fetchone()

    assert conta is not None
    assert conta["agency"] == "0001"
    assert conta["balance_cents"] == 0

    c.close()


def teste_patrimonio():
    c = db()

    total = c.execute(
        "SELECT SUM(balance_cents) FROM accounts"
    ).fetchone()[0]

    assert total == 10_000_000

    c.close()


def teste_integridade():
    c = db()

    resultado = c.execute(
        "PRAGMA integrity_check"
    ).fetchone()[0]

    assert resultado == "ok"

    c.close()


def teste_foreign_keys():
    c = db()

    erros = c.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    assert len(erros) == 0

    c.close()


def teste_pix_registrados():
    c = db()

    pix = c.execute(
        "SELECT COUNT(*) FROM pix_transactions"
    ).fetchone()[0]

    assert pix == 2

    c.close()


def main():
    testes = [
        teste_estrutura,
        teste_admin,
        teste_patrimonio,
        teste_integridade,
        teste_foreign_keys,
        teste_pix_registrados,
    ]

    passou = 0

    print("\n===== TESTES BANCO MASTER =====\n")

    for teste in testes:
        try:
            teste()
            print(f"✅ {teste.__name__}")
            passou += 1
        except Exception as e:
            print(f"❌ {teste.__name__}: {e}")

    print("\n===== RESULTADO =====")
    print(f"{passou}/{len(testes)} testes passaram")

    if passou == len(testes):
        print("✅ TODOS OS TESTES PASSARAM")
    else:
        print("❌ EXISTEM TESTES COM FALHA")


if __name__ == "__main__":
    main()
