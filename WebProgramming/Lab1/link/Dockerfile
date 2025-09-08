FROM ubuntu:latest
LABEL authors="26771"

FROM gradle:8.10-jdk17 AS build
COPY --chown=gradle:gradle .. /home/gradle/src
WORKDIR /home/gradle/src
RUN gradle jar --no-daemon

FROM eclipse-temurin:17-jre
# 端口无意义，记得换
EXPOSE 1337
RUN mkdir /app
WORKDIR /app
COPY --from=build /home/gradle/src/build/libs/*.jar /app/app.jar
ENTRYPOINT ["java", "-DFCGI_PORT=1337", "-jar", "app.jar"]

ENTRYPOINT ["top", "-b"]