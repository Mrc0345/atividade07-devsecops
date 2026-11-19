"""Adaptador explícito: Docker Compose YAML -> políticas Python da API Checkov.

Checkov não possui framework docker_compose nativo. Não alegamos que o CLI
checkov -f docker-compose.yml analisa os serviços: usamos BaseCheck.run.
"""
import argparse
import json
from pathlib import Path
import yaml
from checkov.common.checks.base_check import BaseCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class ComposeCheck(BaseCheck):
    def __init__(self, number, name, predicate):
        super().__init__(name, f"CKV_COMPOSE_{number}", [CheckCategories.GENERAL_SECURITY], ["service"], "services")
        self.predicate = predicate

    def scan_entity_conf(self, conf, entity_type):
        return CheckResult.PASSED if self.predicate(conf) else CheckResult.FAILED


CHECKS = [
    ComposeCheck(1, "Nao permitir modo privilegiado", lambda c: c.get("privileged", False) is False),
    ComposeCheck(2, "Usuario explicitamente nao root", lambda c: str(c.get("user", "")).split(":")[0] not in {"", "0", "root"}),
    ComposeCheck(3, "Sistema de arquivos somente leitura", lambda c: c.get("read_only") is True),
    ComposeCheck(4, "Remover todas as capabilities", lambda c: "ALL" in c.get("cap_drop", []) and not c.get("cap_add")),
    ComposeCheck(5, "Impedir ganho de privilegios", lambda c: "no-new-privileges:true" in c.get("security_opt", [])),
    ComposeCheck(6, "Nao compartilhar namespaces do host", lambda c: all(c.get(k) != "host" for k in ["network_mode", "pid", "ipc"])),
    ComposeCheck(7, "Nao montar sockets Docker nem dispositivos", lambda c: not c.get("devices") and not c.get("volumes")),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?", default="docker-compose.yml")
    parser.add_argument("--output", default="reports/checkov-compose.json")
    args = parser.parse_args()
    document = yaml.safe_load(Path(args.file).read_text(encoding="utf-8"))
    services = document.get("services") if isinstance(document, dict) else None
    if not isinstance(services, dict) or not services:
        raise ValueError("Compose sem servicos: nao aceitar scan vazio")
    results = []
    for name, conf in services.items():
        if not isinstance(conf, dict):
            raise ValueError(f"Servico invalido: {name}")
        for check in CHECKS:
            result = check.run(args.file, conf, name, "service", {})["result"]
            entry = dict(check_id=check.id, service=name, result=result.name, description=check.name)
            results.append(entry)
            print(f"{result.name:6} {check.id} services.{name}: {check.name}")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    return 1 if any(r["result"] != "PASSED" for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
