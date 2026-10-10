"""Narzedzie do kluczy API serwisu glosowego.

  uv run python genkey.py create gra-prod    # tworzy klucz i wypisuje go JEDEN raz
  uv run python genkey.py list               # nazwy i daty utworzenia
  uv run python genkey.py revoke gra-prod    # odwoluje klucz (bez restartu serwisu)

Gra wysyla klucz w naglowku:  X-API-Key: vs_...
"""
import argparse
import sys

import keys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("create", help="utworz klucz").add_argument("name")
    sub.add_parser("list", help="pokaz klucze")
    sub.add_parser("revoke", help="odwolaj klucz").add_argument("name")
    args = parser.parse_args()

    if args.cmd == "create":
        try:
            key = keys.create(args.name)
        except ValueError as e:
            print(e, file=sys.stderr)
            return 1
        print(f"Klucz '{args.name}' (zapisz go teraz, nie da sie go odczytac pozniej):\n\n  {key}\n")
    elif args.cmd == "list":
        for name, created in keys.listing() or []:
            print(f"{name}\t{created}")
    else:
        if not keys.revoke(args.name):
            print(f"Nie ma klucza '{args.name}'.", file=sys.stderr)
            return 1
        print(f"Odwolano '{args.name}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
