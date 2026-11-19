# Atividade 07 - Pipeline DevSecOps

API de tarefas em Java 21 / Spring Boot 4.1.2, com armazenamento em memória e esteira GitHub Actions. Projeto acadêmico independente, sem frontend, banco externo, autenticação complexa ou infraestrutura paga. Professora: Ramyres Pereira Aquino.

**Apresentação sem notebook configurado:** use somente navegador, internet e acesso à conta GitHub. Os runners executam Java, Docker e scanners. Veja [o roteiro pelo navegador](docs/APRESENTACAO.md). Publicação e execuções no GitHub ainda dependem da autorização do proprietário.

## Executar localmente

Pré-requisitos: Java 21 e Docker Desktop com contêineres Linux. Maven é baixado pelo Wrapper, com checksum fixado.

```powershell
.\mvnw.cmd -B verify
java -jar target/tasks-api.jar
```

Ou somente Docker:

```powershell
docker compose -p atividade07 up -d --build
python scripts/smoke.py
docker compose -p atividade07 logs
docker compose -p atividade07 down
```

A API usa `http://127.0.0.1:8080`. Para outra porta no Compose: `$env:PORT='18088'`. Na execução Java: `java -jar target/tasks-api.jar --server.port=18088`. O Compose publica apenas no loopback. A porta interna permanece 8080. O script smoke aceita a URL como primeiro argumento.

| Método | Endpoint | Resultado |
|---|---|---|
| GET | /api/health | 200, status UP |
| GET | /api/tasks | 200, lista |
| POST | /api/tasks | 201, tarefa criada e Location |
| GET | /api/tasks/{id} | 200 ou 404 |
| DELETE | /api/tasks/{id} | 204 ou 404 |

```powershell
Invoke-RestMethod http://127.0.0.1:8080/api/health
$task = Invoke-RestMethod http://127.0.0.1:8080/api/tasks -Method Post -ContentType application/json -Body '{"title":"Apresentar pipeline","description":"Atividade 07"}'
Invoke-RestMethod "http://127.0.0.1:8080/api/tasks/$($task.id)"
Invoke-RestMethod "http://127.0.0.1:8080/api/tasks/$($task.id)" -Method Delete
```

Título obrigatório, máximo 160 caracteres; descrição até 1.024; UUID validado; limite de 1.000 tarefas; erros sem stack trace. Dados são voláteis e perdidos ao reiniciar. Cabeçalhos: CSP restritiva, nosniff, DENY, no-referrer, Permissions-Policy e no-store. **A API não autentica usuários**: é uma demonstração local/efêmera, não um serviço pronto para exposição pública.

## Pipeline e gates

```text
Gitleaks -----+
Semgrep ------+--> Maven/testes/SBOM --> Trivy SCA ---+
Checkov ------+                    --> Docker/Trivy -+--> ZAP --> entrega temporária
```

| Controle | Ferramenta e critério |
|---|---|
| Segredos | Gitleaks no histórico Git, com redação; qualquer achado reprova |
| SAST | Semgrep CE, quatro regras Java locais em severity ERROR; findings ou erro de análise reprovam |
| SCA | Trivy sobre SBOM CycloneDX, CVEs HIGH/CRITICAL reprovam, inclusive sem correção disponível |
| SBOM | CycloneDX Maven Plugin, JSON 1.6, dependências de produção; artefato `sbom-cyclonedx` |
| Contêiner | Build multi-stage, Java 21, usuário 10001, healthcheck; Trivy HIGH/CRITICAL |
| IaC | `docker compose config`, sete políticas Checkov para Compose; Dockerfile com CKV_DOCKER_2 e CKV_DOCKER_3 |
| DAST | ZAP API Scan ativo a partir do OpenAPI; regras críticas configuradas como FAIL e gate adicional para qualquer risco HIGH |
| Entrega | Só depois de todos os gates: carrega a mesma imagem analisada, inicia Compose e executa smoke HTTP |

O Checkov **não oferece framework nativo Docker Compose**. `security/check_compose.py` é um adaptador versionado que interpreta o YAML e usa `BaseCheck.run` da API Checkov. Seus IDs `CKV_COMPOSE_1` a `7` são políticas **personalizadas**, não regras nativas anunciadas pelo fornecedor. O teste de regressão verifica que cada configuração insegura é bloqueada. O scanner nativo de Dockerfile cobre explicitamente usuário não root e healthcheck; não alegamos cobertura de todas as políticas do Checkov.

As regras Semgrep locais bloqueiam execução de comandos, desserialização Java nativa, concatenação em consultas SQL e hashes fracos. Isso é SAST com escopo explícito, não auditoria completa ou análise interprocedural paga. As quatro regras e a versão do scanner ficam no Git.

ZAP: `-I` permite WARN sem esconder FAIL nem falha operacional. `zap_gate.py` ainda reprova qualquer alerta HIGH. Alertas médios não explicitamente bloqueantes permanecem visíveis nos relatórios para triagem; INFO não reprova. HSTS não é imposto no laboratório HTTP local, pois exige HTTPS real. Não usamos `continue-on-error` nem neutralizamos scanners com `|| true`.

Actions são fixadas por SHA completo; imagens, por digest. Versões e digests: `security/versions.json` e `security/images.lock.json`. A base de CVEs é atualizada a cada execução: uma execução verde antiga não garante aprovação futura. Corrija dependências/imagens quando houver achados; não reduza o gate para obter verde.

## Falha controlada e correção

O único delta da demonstração é `privileged: false` -> `privileged: true`. **Nunca execute `docker compose up` no estado vulnerável**. A análise é estática, e `CKV_COMPOSE_1` retorna falha. Com `needs`, build e entrega não prosseguem.

```powershell
python scripts/demo.py vulneravel
# Execute apenas o scanner; não inicie a configuração vulnerável.
docker run --rm --entrypoint python -v "${PWD}:/src" -w /src bridgecrew/checkov:3.4.5 security/check_compose.py
# Saída esperada: FAILED CKV_COMPOSE_1; código 1.
python scripts/demo.py corrigido
docker run --rm --entrypoint python -v "${PWD}:/src" -w /src bridgecrew/checkov:3.4.5 security/check_compose.py
# Saída esperada: todos PASSED; código 0.
```

Para comandos com imagens exatamente fixadas, use os digests de `security/images.lock.json`; as tags acima são atalhos para uso interativo. A pipeline usa somente digests.

Estados Git: `main` e `demo/corrigido` representam o código seguro; `demo/vulneravel` representa a falha controlada. Esses estados são mantidos em branches locais, sem publicação automática. Para atender ao enunciado original, o roteiro principal faz dois commits reais pelo editor do GitHub na branch demo/ao-vivo: primeiro introduz privileged: true, depois corrige para false. Run workflow e as branches prontas servem somente para ensaio e contingência.

## Publicar - somente após autorização

Os comandos abaixo são instruções, não foram executados. Crie um repositório público **vazio**, sem README automático, com nome `atividade07-devsecops`. Não use um repositório do PI.

```powershell
git remote add origin https://github.com/SEU_USUARIO/atividade07-devsecops.git
git push -u origin main
git push origin demo/vulneravel demo/corrigido
```

Depois de publicar, abra Actions e valide execuções reais das duas branches. Não afirme Build Passed/Failed no GitHub com base apenas nos testes locais. Registre os links reais das execuções em `docs/VALIDACAO.md` e guarde-os como contingência. Se houver alerta de CVE, corrija e repita todos os gates antes da aula.

Na execução corrigida, abra **Artifacts -> sbom-cyclonedx -> Download** e extraia `bom.json`. Mostre `bomFormat`, `specVersion`, `components` e as versões de dependências. Relatórios de scanners e testes são artefatos separados, mantidos por 14 dias. A imagem aprovada é mantida por 2 dias para limitar armazenamento; rode a contingência novamente perto da apresentação.

## Estrutura

```text
.github/workflows/devsecops.yml    Jobs e gates
.github/dependabot.yml            Atualizações de dependências e Actions
src/main/java/...                 API, erros e cabeçalhos
src/main/resources/               Configuração e OpenAPI estático
src/test/java/...                 Testes HTTP com MockMvc
security/                        Políticas, versões e digests
scripts/                         Smoke, demonstração e gate ZAP
docs/                            Roteiro e validações reais
Dockerfile                       Build multi-stage
docker-compose.yml               Execução restrita
pom.xml, mvnw, mvnw.cmd           Build reproduzível
```

## Referências oficiais consultadas

- [Spring Boot e Java](https://docs.spring.io/spring-boot/system-requirements.html)
- [CycloneDX Maven Plugin](https://cyclonedx.github.io/cyclonedx-maven-plugin/)
- [Gitleaks](https://github.com/gitleaks/gitleaks)
- [Semgrep CLI](https://semgrep.dev/docs/cli-reference)
- [Trivy e códigos de saída](https://trivy.dev/docs/dev/guide/configuration/others/)
- [Checkov e frameworks](https://www.checkov.io/)
- [API BaseCheck do Checkov](https://github.com/bridgecrewio/checkov/blob/main/checkov/common/checks/base_check.py)
- [ZAP API Scan](https://www.zaproxy.org/docs/docker/api-scan/)

Runners Linux padrão em repositórios públicos têm computação gratuita; artefatos e cache possuem franquias próprias. Confira o uso e mantenha orçamento de gastos adequado à conta. Não são usados runners grandes ou serviços pagos. [Cobrança oficial do GitHub Actions](https://docs.github.com/en/billing/concepts/product-billing/github-actions).

No GitHub Actions, o job build disponibiliza application-jar e o job image usa o target Docker ci para empacotar exatamente esse JAR testado. O build multi-stage padrao continua disponivel para uso local. Isso evita uma segunda resolucao Maven dentro do Docker e vincula a imagem ao artefato aprovado.
