# Java Adapter

The Java adapter detects Java projects and generates reproduction plans.

## Detection

Files detected:
- `pom.xml`, `build.gradle`, `build.gradle.kts`, `settings.gradle`, `gradlew`
- `src/main/java/**/*.java`

## Planning

Maven projects:
- Install: `mvn package -DskipTests`
- Test: `mvn test`

Gradle projects:
- Install: `gradle build -x test` (or `./gradlew`)
- Test: `gradle test`

## Runtime

Requires: `java`

Support level: **execute-if-runtime-present**

## Limitations

- Java runtime must be installed separately
- Maven/Gradle build may download many dependencies
