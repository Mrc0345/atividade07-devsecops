# Apresentação de 10 a 15 minutos - somente navegador

Não depende de Java, Maven, Docker, VS Code ou terminal no notebook da sala. Precisa de navegador atualizado, internet, conta GitHub e acesso ao segundo fator. Entre na conta antes da aula sem salvar credenciais em computador compartilhado; encerre a sessão ao sair.

## Preparar antes da aula

1. Publicar o repositório **apenas depois da autorização**.
2. Executar `demo/vulneravel` e `demo/corrigido` no GitHub Actions e resolver erros reais.
3. Salvar os links das execuções em `VALIDACAO.md`. Não há execuções GitHub anteriores prontas enquanto o repositório não for publicado.
4. Rodar novamente a versão segura perto da apresentação. CVEs e disponibilidade de scanners mudam.
5. Deixar abertas cinco abas: README, workflow, execução vulnerável, execução corrigida e SBOM/relatório ZAP.
6. Baixar antecipadamente SBOM e relatórios **reais**. São contingência de execução/internet, não substituem a demonstração exigida. Combine a contingência com a professora se a rede da sala falhar.

## Roteiro e cliques

| Tempo | Ação no navegador | O que explicar |
|---|---|---|
| 0-2 min | Abrir README, controlador Java e Dockerfile | API pequena, validação, memória, usuário não root |
| 2-4 min | Abrir `.github/workflows/devsecops.yml` | Gatilhos, scanners, `needs`, permissões read-only, SHA/digest |
| 4-6 min | Actions -> DevSecOps -> Run workflow -> branch `demo/vulneravel` -> Run | Mostrar única alteração `privileged: true`; nenhum contêiner inseguro é iniciado |
| 6-8 min | Abrir job IaC e log Checkov | `FAILED CKV_COMPOSE_1`, workflow Failure; jobs dependentes pulados |
| 8-10 min | Abrir comparação das branches e disparar `demo/corrigido` | Correção explícita para false, sem desativar scanner |
| 10-12 min | Abrir execução corrigida real anterior enquanto a nova roda | Testes, SCA, imagem, ZAP e entrega aprovada; dizer que é uma execução anterior |
| 12-14 min | Artifacts -> sbom-cyclonedx; abrir bom.json | Mostrar inventário de componentes; mostrar também relatório ZAP e smoke da entrega |
| 14-15 min | Conferir nova execução e responder perguntas | Distinguir resultado ao vivo, resultado anterior e limitações |

Não prometa que uma pipeline completa fria termina em 2 minutos. O estado vulnerável deve falhar cedo; a execução segura pode ultrapassar a janela. As execuções anteriores precisam ser autênticas e identificadas como anteriores.

## Frases de apoio

- “O segredo não está em executar scanners; está em impedir a entrega quando o gate falha.”
- “Essa política Compose é personalizada usando a API do Checkov, porque não existe framework Compose nativo.”
- “Aqui está a imagem aprovada iniciando depois dos controles, com requisições HTTP reais.”
- “A API está no runner temporário, não em um site público. O log comprova a execução.”
- “Este SBOM descreve dependências; o Trivy cruza esse inventário com a base de CVEs.”

## Cinco perguntas prováveis

1. **Qual a diferença entre SAST, SCA e DAST?** SAST analisa código; SCA procura vulnerabilidades nas dependências; DAST testa a aplicação em execução.
2. **O que impede um deploy inseguro?** Os scanners retornam código diferente de zero e os jobs de entrega dependem de todos os gates pelo `needs`.
3. **Por que gerar SBOM?** Para saber quais componentes e versões compõem o software e permitir rastrear vulnerabilidades e atualizações.
4. **Por que `privileged: true` é grave?** Amplia fortemente o acesso do contêiner ao host; é desnecessário para uma API HTTP. A demonstração só analisa esse YAML, não o executa.
5. **Passar na pipeline prova que não há vulnerabilidades?** Não. Prova que os controles configurados passaram com as regras e bases daquele momento. Existem limites de cobertura e necessidade de manutenção.

## Se quiser usar terminal no seu próprio PC

```powershell
git switch demo/vulneravel
docker run --rm --entrypoint python -v "${PWD}:/src" -w /src bridgecrew/checkov:3.4.5 security/check_compose.py
# Não executar docker compose up nesta branch.
git switch demo/corrigido
docker run --rm --entrypoint python -v "${PWD}:/src" -w /src bridgecrew/checkov:3.4.5 security/check_compose.py
.\mvnw.cmd -B verify
docker compose -p atividade07 up -d --build
python scripts/smoke.py
docker compose -p atividade07 down
git switch main
```
