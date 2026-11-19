"""Gate adicional: qualquer risco HIGH reprova, mesmo regra não listada no TSV."""
import json
import sys
from pathlib import Path

report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
sites = report.get("site")
if not sites:
    raise SystemExit("Relatorio ZAP sem sites: nao aceitar scan vazio")
alerts = [a for site in sites for a in site.get("alerts", [])]
for alert in alerts:
    print(f"risk={alert.get('riskcode')} rule={alert.get('pluginid')} {alert.get('name')}")
raise SystemExit(1 if any(int(a["riskcode"]) >= 3 for a in alerts) else 0)
