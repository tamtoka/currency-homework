from decimal import Decimal, DecimalException
import sys

from api_client import CurrencyAPIError, get_currency_rates
from storage import read_fresh_rates, save_to_file


def convert(amount: str, source: str, target: str, rates: dict) -> Decimal:
    for code in (source, target):
        if code not in rates:
            raise ValueError(f"Валюта {code or '(пустой код)'} отсутствует в списке.")
    try:
        value = Decimal(amount.replace(",", "."))
        if not value.is_finite():
            raise ValueError("Введите конечную числовую сумму, например 10,50.")
        source_rate = Decimal(str(rates[source]))
        target_rate = Decimal(str(rates[target]))
        return value * target_rate / source_rate
    except DecimalException as error:
        raise ValueError("Не удалось выполнить пересчёт. Проверьте введённую сумму.") from error


def main() -> int:
    try:
        base = input("Базовая валюта [USD]: ").strip().upper() or "USD"
        data = read_fresh_rates(base)
        if data is None:
            data = get_currency_rates(base)
            try:
                save_to_file(data)
            except OSError as error:
                print(f"Не удалось сохранить кэш: {error}", file=sys.stderr)
            print("Источник: API")
        else:
            print("Источник: кэш")

        rates = data["rates"]
        for code in ("RUB", "EUR", "GBP"):
            if code in rates:
                print(f"1 {base} = {rates[code]} {code}")
            else:
                print(f"Курс {code} недоступен.")
        print("Курсы предоставлены ExchangeRate-API: https://www.exchangerate-api.com")

        source = input("Из какой валюты перевести? Enter — выход: ").strip().upper()
        if not source:
            return 0
        if source == "?":
            print("Доступные валюты: " + ", ".join(sorted(rates.keys())))
            source = input("Из какой валюты перевести? ").strip().upper()
        target = input("В какую валюту перевести? ").strip().upper()
        amount = input("Сумма: ").strip()
        result = convert(amount, source, target, rates)
        print(f"{amount} {source} = {result:.4f} {target}")
    except (CurrencyAPIError, ValueError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nВвод завершён.")
    return 0
