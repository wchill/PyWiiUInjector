FROM mcr.microsoft.com/dotnet/sdk:6.0

RUN apt-get update && apt-get install -y python3 build-essential git libncurses5-dev openjdk-17-jdk-headless maven

WORKDIR /project