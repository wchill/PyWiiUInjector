FROM mcr.microsoft.com/dotnet/sdk:6.0

RUN apt-get update && apt-get install -y python3 python3-pip build-essential git libncurses5-dev openjdk-17-jdk-headless maven
RUN pip install pillow requests jinja2

WORKDIR /project