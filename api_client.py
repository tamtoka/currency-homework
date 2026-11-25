import requests


class CurrencyAPIError(Exception):
    """Ошибка получения курсов, которую можно показать пользователю."""


def get_currency_rates(base: str) -> dict:
    base = base.strip().upper()
    if len(base) != 3 or not base.isascii() or not base.isalpha():
        raise CurrencyAPIError("Введите трёхбуквенный код валюты, например USD.")

    url = f"https://open.er-api.com/v6/latest/{base}"
    try:
        response = requests.get(url, timeout=10)
    except requests.Timeout as error:
        raise CurrencyAPIError("Сервис курсов не ответил вовремя.") from error
    except requests.RequestException as error:
        raise CurrencyAPIError("Не удалось подключиться к сервису курсов.") from error

    if response.status_code != 200 and response.status_code != 404:
        raise CurrencyAPIError(f"Сервис курсов вернул HTTP {response.status_code}.")

    try:
        data = response.json()
    except ValueError as error:
        raise CurrencyAPIError(
            f"Сервис курсов вернул некорректный ответ (HTTP {response.status_code})."
        ) from error

    if not isinstance(data, dict):
        raise CurrencyAPIError("Сервис курсов вернул данные в неизвестном формате.")
    if data.get("error-type") == "unsupported-code":
        raise CurrencyAPIError(f"Сервис не поддерживает валюту {base}.")
    if response.status_code != 200:
        raise CurrencyAPIError(f"Сервис курсов вернул HTTP {response.status_code}.")
    if data.get("result") != "success":
        raise CurrencyAPIError("Сервису не удалось получить курсы валют.")
    if data.get("base_code") != base or not isinstance(data.get("rates"), dict):
        raise CurrencyAPIError("В ответе сервиса отсутствуют запрошенные курсы.")
    return data
