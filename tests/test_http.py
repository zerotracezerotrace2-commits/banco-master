import urllib.request
import urllib.parse
import http.cookiejar


BASE = "http://127.0.0.1:5000"


def teste_login_valido():
    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookies)
    )

    dados = urllib.parse.urlencode({
        "username": "cliente01",
        "password": "Master@01"
    }).encode()

    resposta = opener.open(
        urllib.request.Request(
            BASE + "/",
            data=dados,
            method="POST"
        )
    )

    if resposta.geturl() != BASE + "/dashboard":
        raise AssertionError("Login válido não abriu o dashboard")

    print("✅ teste_login_valido")


def teste_login_invalido():
    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookies)
    )

    dados = urllib.parse.urlencode({
        "username": "cliente01",
        "password": "senha_errada"
    }).encode()

    resposta = opener.open(
        urllib.request.Request(
            BASE + "/",
            data=dados,
            method="POST"
        )
    )

    if resposta.geturl() != BASE + "/":
        raise AssertionError("Login inválido foi aceito")

    print("✅ teste_login_invalido")


def teste_dashboard_sem_login():
    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookies)
    )

    resposta = opener.open(BASE + "/dashboard")

    if resposta.geturl() != BASE + "/":
        raise AssertionError("Dashboard acessível sem login")

    print("✅ teste_dashboard_sem_login")


def teste_pix_sem_login():
    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookies)
    )

    dados = urllib.parse.urlencode({
        "destination": "100002",
        "amount": "10,00",
        "description": "Teste"
    }).encode()

    resposta = opener.open(
        urllib.request.Request(
            BASE + "/pix",
            data=dados,
            method="POST"
        )
    )

    if resposta.geturl() != BASE + "/":
        raise AssertionError("Pix acessível sem login")

    print("✅ teste_pix_sem_login")


def teste_logout():
    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookies)
    )

    dados = urllib.parse.urlencode({
        "username": "cliente01",
        "password": "Master@01"
    }).encode()

    resposta = opener.open(
        urllib.request.Request(
            BASE + "/",
            data=dados,
            method="POST"
        )
    )

    if resposta.geturl() != BASE + "/dashboard":
        raise AssertionError("Login necessário para teste de logout falhou")

    opener.open(BASE + "/logout")

    resposta = opener.open(BASE + "/dashboard")

    if resposta.geturl() != BASE + "/":
        raise AssertionError("Logout não protegeu o dashboard")

    print("✅ teste_logout")


def main():
    testes = [
        teste_login_valido,
        teste_login_invalido,
        teste_dashboard_sem_login,
        teste_pix_sem_login,
        teste_logout,
    ]

    passou = 0

    for teste in testes:
        try:
            teste()
            passou += 1
        except Exception as e:
            print(f"❌ {teste.__name__}: {e}")

    print("\n===== RESULTADO =====")
    print(f"{passou}/{len(testes)} testes passaram")

    if passou != len(testes):
        raise SystemExit("❌ ALGUNS TESTES FALHARAM")

    print("✅ TODOS OS TESTES HTTP PASSARAM")


if __name__ == "__main__":
    main()
