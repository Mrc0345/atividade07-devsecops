# BuildKit: cache Maven local ao build, sem frontend remoto mutavel.
# Builder: Maven 3.9.11 / Java 21, pinned by manifest digest.
FROM maven@sha256:3175c44b207d6698aecb9bbb5bf285b5b4efcf7f567d6f65d88cd218276a6ab2 AS build
WORKDIR /build
COPY pom.xml ./
COPY src ./src
RUN --mount=type=cache,target=/root/.m2 mvn -B -ntp package

FROM eclipse-temurin@sha256:ac05c3c42b7c2f1a52c9bd52f01041fa1958231b15ebeae7420429cbc5baf474 AS base
WORKDIR /app
ENV PORT=8080
USER 10001:10001
EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=3s --start-period=30s --retries=12 CMD wget --spider -q http://127.0.0.1:${PORT}/api/health || exit 1
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=70", "-jar", "/app/tasks-api.jar"]

# CI: empacota exatamente o JAR aprovado no job Maven, sem compilar duas vezes.
FROM base AS ci
COPY --chown=10001:10001 target/tasks-api.jar /app/tasks-api.jar

# Padrao local: build completo a partir do codigo-fonte.
FROM base AS runtime
COPY --from=build --chown=10001:10001 /build/target/tasks-api.jar /app/tasks-api.jar
