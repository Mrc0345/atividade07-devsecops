"""Altera exclusivamente privileged; nunca inicia containers."""
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("state", choices=["vulneravel", "corrigido"])
args = parser.parse_args()
path = Path(__file__).resolve().parents[1] / "docker-compose.yml"
text = path.read_text(encoding="utf-8")
old = "privileged: false" if args.state == "vulneravel" else "privileged: true"
new = "privileged: true" if args.state == "vulneravel" else "privileged: false"
if text.count(old) != 1:
    raise SystemExit("Estado inesperado: esperado exatamente um " + old)
path.write_text(text.replace(old, new), encoding="utf-8")
print(f"Estado {args.state}: {new}. Apenas YAML alterado; nenhum container executado.")
