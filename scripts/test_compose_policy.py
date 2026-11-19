"""Teste de regressao de cada politica; nao executa infraestrutura insegura."""
import copy
import sys
from pathlib import Path
import unittest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "security"))
from check_compose import CHECKS, CheckResult


class ComposePolicyTest(unittest.TestCase):
    def setUp(self):
        self.conf = yaml.safe_load(Path("docker-compose.yml").read_text())["services"]["api"]

    def test_safe_compose_passes_all_checks(self):
        for check in CHECKS:
            self.assertEqual(CheckResult.PASSED, check.run("docker-compose.yml", self.conf, "api", "service", {})["result"])

    def test_each_security_regression_is_blocked(self):
        changes = [("privileged", True), ("user", "0:0"), ("read_only", False),
                   ("cap_add", ["SYS_ADMIN"]), ("security_opt", []),
                   ("network_mode", "host"), ("volumes", ["/var/run/docker.sock:/var/run/docker.sock"])]
        for check, (key, value) in zip(CHECKS, changes):
            conf = copy.deepcopy(self.conf)
            conf[key] = value
            with self.subTest(check=check.id):
                self.assertEqual(CheckResult.FAILED, check.run("docker-compose.yml", conf, "api", "service", {})["result"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
