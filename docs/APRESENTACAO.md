# Apresentação de 10 a 15 minutos - somente navegador

Não depende de Java, Maven, Docker, VS Code ou terminal no notebook da sala. Precisa de navegador atualizado, internet, conta GitHub e acesso ao segundo fator. Entre na conta antes da aula sem salvar credenciais em computador compartilhado; encerre a sessão ao sair.

## Preparar antes da aula

1. Abrir https://github.com/Mrc0345/atividade07-devsecops, já publicado com autorização.
2. Executar `demo/vulneravel` e `demo/corrigido` no GitHub Actions e resolver erros reais.
3. Salvar os links das execuções em `VALIDACAO.md`. As execuções reais aprovadas e reprovadas já estão vinculadas no README; confira sua disponibilidade antes da aula.
4. Rodar novamente a versão segura perto da apresentação. CVEs e disponibilidade de scanners mudam.
5. Deixar abertas cinco abas: README, workflow, execução vulnerável, execução corrigida e SBOM/relatório ZAP.
6. Baixar antecipadamente SBOM e relatórios **reais**. São contingência de execução/internet, não substituem a demonstração exigida. Combine a contingência com a professora se a rede da sala falhar.

## Roteiro oficial e cliques - alteração real ao vivo

O enunciado original exige push ou PR com falha grave e depois um novo push com a correção. Rodar somente workflow_dispatch em branches já prontas serve para ensaiar, mas não substitui essa dinâmica.

### Preparar a branch da apresentação

Antes da aula, crie uma branch `demo/ao-vivo` a partir da `main` segura pelo seletor de branches no GitHub. Valide previamente o acesso ao editor e aos Actions. Mantenha `main` intacta e não faça merge da falha.

| Tempo | Ação no navegador | O que explicar |
|---|---|---|
| 0-2 min | Mostrar API, Dockerfile, Compose e workflow | Visão geral das etapas e dependências entre jobs |
| 2-3 min | Selecionar `demo/ao-vivo`, abrir docker-compose.yml e clicar no lápis | A alteração é real e controlada |
| 3-4 min | Trocar `privileged: false` por `privileged: true`; Commit changes na própria branch | O commit feito pelo navegador gera evento push e dispara a esteira automaticamente |
| 4-7 min | Actions -> execução do novo commit -> iac | Mostrar FAILED CKV_COMPOSE_1, workflow reprovado e jobs posteriores bloqueados |
| 7-8 min | Voltar ao Compose da mesma branch e corrigir para `privileged: false`; fazer novo commit | Corrigir a causa, sem desativar o scanner |
| 8-12 min | Abrir a execução automática do commit corrigido | Mostrar aprovação dos gates, entrega temporária e artefato sbom-cyclonedx |
| 12-15 min | Arguição | Explicar ferramentas, critérios e limitações |

Nunca inicie um contêiner com a configuração vulnerável. A pipeline faz análise estática antes do build e da entrega.

Se preferir usar um PR, na primeira alteração escolha criar uma nova branch, abra o PR para main e depois faça o commit de correção na mesma branch do PR. Os eventos push e pull_request podem produzir duas execuções; apresente uma delas e identifique o commit correto. Não use pull_request_target para executar código não confiável.

Uma edição no GitHub não exige Git instalado no notebook. Requer permissão de escrita na branch. Não faça a demonstração numa branch protegida que impeça os commits necessários.

A execução segura pode demorar mais do que a janela da aula. Ensaie antes e use resultados anteriores reais apenas como contingência claramente identificada; a exigência de disparar a falha e a correção ao vivo permanece. Se o tempo ou a rede impedirem a conclusão, alinhe a contingência com a professora.

As branches `demo/vulneravel` e `demo/corrigido` e o botão Run workflow ficam como apoio para ensaios, não como substitutos dos novos commits ao vivo.

Referências: [editar arquivos pelo GitHub](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files) e [eventos que disparam workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).

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
