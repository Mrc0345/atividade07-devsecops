# ValidaÃ§Ã£o e pendÃªncias

ValidaÃ§Ã£o local em 18/11/2026 (America/Sao_Paulo), Windows com Docker Desktop Linux. Este arquivo nÃ£o Ã© um relatÃ³rio para a apresentaÃ§Ã£o: Ã© um registro tÃ©cnico do que foi realmente executado.

| VerificaÃ§Ã£o | Resultado local |
|---|---|
| Java 21 + Maven 3.9.11 | CompilaÃ§Ã£o e verify aprovados |
| Testes Java | 3 testes, zero falhas/erros; incluem ciclo CRUD e diversas entradas invÃ¡lidas |
| API Java fora do Docker | Smoke HTTP aprovado na porta 18087 na implementaÃ§Ã£o inicial |
| Docker multi-stage | Imagem final construÃ­da com testes no estÃ¡gio builder |
| Docker Compose | ConfiguraÃ§Ã£o vÃ¡lida, usuÃ¡rio nÃ£o root, readonly, API saudÃ¡vel na porta 18088 |
| HTTP na imagem final | GET health/list/get, POST, DELETE, 400/404 e cabeÃ§alhos aprovados |
| Gitleaks | HistÃ³rico local analisado; nenhum segredo encontrado |
| Semgrep | 4 arquivos Java, 4 regras, zero findings no cÃ³digo final |
| Semgrep - teste negativo | Fixture com Runtime.exec detectada, exit 1; cÃ³digo nunca executado |
| Checkov Dockerfile | CKV_DOCKER_2 e CKV_DOCKER_3 aprovadas |
| Checkov Compose corrigido | 7 polÃ­ticas aprovadas, exit 0 |
| Checkov Compose vulnerÃ¡vel | CKV_COMPOSE_1 reprovada, exit 1; YAML nunca iniciado |
| RegressÃ£o das polÃ­ticas | Baseline e sete mutaÃ§Ãµes inseguras testadas; duas funÃ§Ãµes de teste aprovadas |
| SBOM | CycloneDX JSON 1.6, 45 componentes, target/bom.json |
| Trivy SCA | Zero CVEs HIGH/CRITICAL na versÃ£o final |
| Trivy imagem | Zero CVEs HIGH/CRITICAL na versÃ£o final |
| Workflow | actionlint aprovado; execuÃ§Ã£o real no GitHub ainda pendente |
| ZAP | Ver resumo e evidÃªncias locais apÃ³s conclusÃ£o da Ãºltima rodada |

## Problemas encontrados e corrigidos

1. A base inicial Spring Boot 3.5.16 trouxe 13 achados HIGH/CRITICAL na imagem (Jackson, Tomcat e Spring MVC). O Trivy reprovou corretamente. Atualizamos para Spring Boot 4.1.2, adaptamos os testes para Jackson 3 e a organizaÃ§Ã£o de testes do Boot 4 e repetimos os scans. Nenhuma CVE foi ignorada.
2. A configuraÃ§Ã£o herdada de CycloneDX do parent Spring Boot desviava a saÃ­da para META-INF/sbom/application.cdx.json. Uma execuÃ§Ã£o com configuraÃ§Ã£o explÃ­cita agora tambÃ©m gera o artefato requerido em target/bom.json.
3. Durante a inicializaÃ§Ã£o do Compose, uma conexÃ£o pode ser aceita e encerrada antes de a API estar pronta. O smoke agora repete falhas de transporte por atÃ© 60 segundos, mantendo falhas de validaÃ§Ã£o como erros reais.
4. O ZAP inicial apontou ausÃªncia de Cross-Origin-Resource-Policy. Foi adicionado same-origin e um teste do cabeÃ§alho.
5. Maven clean no Windows nÃ£o remove um JAR aberto: o processo Java temporÃ¡rio foi encerrado antes de repetir o build. Isso nÃ£o afeta runners Linux efÃªmeros.

## Limites de comprovaÃ§Ã£o

- O pipeline completo **nÃ£o foi executado no GitHub Actions**. NÃ£o existem links de runs pÃºblicos nem contingÃªncias de Actions prontas, porque nÃ£o houve autorizaÃ§Ã£o de publicaÃ§Ã£o.
- AprovaÃ§Ã£o local dos scanners nÃ£o equivale a Build Passed do GitHub. PermissÃµes da conta, polÃ­ticas de Actions, download de imagens e comportamento dos runners ainda precisam ser validados no serviÃ§o real.
- Os testes locais de rede Docker Desktop usam host.docker.internal; no runner Ubuntu, o ZAP usa --network host e 127.0.0.1.
- Nenhum scanner garante ausÃªncia total de vulnerabilidades. Os critÃ©rios e escopos estÃ£o documentados no README.
- As bases de CVEs mudam. Executar novamente antes da aula e corrigir eventuais novos achados.

## Preencher somente com execuÃ§Ãµes reais apÃ³s autorizaÃ§Ã£o

- RepositÃ³rio pÃºblico: pendente.
- Run vulnerÃ¡vel (GitHub Failure): pendente.
- Run corrigido (GitHub Success): pendente.
- ContingÃªncia anterior aprovada e recente: pendente.
- SBOM baixado do Actions: pendente. O SBOM local jÃ¡ foi gerado.

## Triagem dos alertas ZAP finais

- **10106 / risco médio - HTTP Only Site:** esperado no runner local sem TLS. Não é uma autorização para expor a API na internet; uma implantação real exige HTTPS e autenticação adequada.
- **40014 / risco baixo - texto de teste persistido em resposta JSON:** a API armazena texto e devolve application/json, com nosniff e CSP. Não há renderização HTML ou frontend. Um consumidor futuro precisará manter encoding correto; não é seguro reaproveitar o texto como HTML.
- **100001 / risco baixo - Content-Type em requisições de fuzzing à raiz:** respostas de erro podem usar application/problem+json em vez do tipo inferido pelo scanner. Os endpoints válidos e os erros esperados são testados. Não foi acrescentada supressão de regra.

As três advertências permanecem visíveis no relatório. A regra CORP foi corrigida e passou. O ZAP importou cinco URLs/operações para exercitar a API.
