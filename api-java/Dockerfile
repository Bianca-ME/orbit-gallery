# --------------------------------------------------------------
# 1  Use the official Quarkus “micro‑image” as the *build* base.
# --------------------------------------------------------------
#   - Based on a minimal JDK 17 runtime (about 150 MB).
#   - Contains the native‑image toolchain that Quarkus needs for
#     fast container builds.
FROM quay.io/quarkus/quarkus-micro-image:2.16-java17

# --------------------------------------------------------------
# 2 Set the working directory where we will copy the source.
# --------------------------------------------------------------
WORKDIR /work/

# --------------------------------------------------------------
# 3 Copy the Maven source tree into the container.
# --------------------------------------------------------------
#   - `src/` holds all Java/Kotlin source files and resources.
#   - Keeping the directory structure identical to a normal Maven
#     project lets the Quarkus Maven plugin work unchanged.
COPY src/ src/

# --------------------------------------------------------------
# 4  Copy the Maven descriptor (pom.xml) next to the sources.
# --------------------------------------------------------------
#   The pom defines dependencies (Quarkus, Hibernate, etc.) and the
#   build plugins.  It must be present for the `mvn` command below.
COPY pom.xml .

# --------------------------------------------------------------
# 5 Build the application with Maven, skipping tests.
# --------------------------------------------------------------
#   - `./mvnw` invokes the Maven wrapper bundled with the project,
#     guaranteeing the correct Maven version.
#   - `package` compiles the code and creates the runnable jar
#     (`*-runner.jar`).  Skipping tests speeds up the container build
#     for a demo; you can drop `-DskipTests` when you want CI to run them.
RUN ./mvnw package -DskipTests

# --------------------------------------------------------------
# 6 Declare the port the Quarkus HTTP server will listen on.
# --------------------------------------------------------------
EXPOSE 8080
#   Quarkus defaults to port 8080.  `EXPOSE` is documentation for
#   anyone (or any orchestrator) that runs the container.

# --------------------------------------------------------------
# 7 Define the command that starts the service.
# --------------------------------------------------------------
#   The built jar lives under `target/` and follows the pattern
#   `<artifact>-runner.jar`.  Using a wildcard works because the
#   build produces exactly one such file.
CMD ["java","-jar","target/*-runner.jar"]
