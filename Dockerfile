# Steg 1: Förbered Python-miljön
FROM python:3.13.2-slim AS python

# Skapa ett virtuellt miljö
RUN python -m venv /venv

# Kopiera requirements.txt och installera beroenden
COPY Python/requirements.txt .
RUN /venv/bin/python -m pip install -r requirements.txt

# Steg 2: Bygg .NET-applikationen
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build

# Sätt arbetskatalogen för .NET-projektet
WORKDIR /src

# Kopiera .NET-projektfilen från root
COPY Q-verify-2025.csproj ./Q-verify-2025.csproj
RUN dotnet restore Q-verify-2025.csproj

# Kopiera resten av koden och bygg projektet
COPY . .
WORKDIR /src
RUN dotnet publish Q-verify-2025.csproj -c Release -o /app/publish

# Steg 3: Bygg den slutgiltiga containern
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final

# Sätt arbetskatalogen
WORKDIR /app

# Kopiera den publicerade .NET-applikationen
COPY --from=build /app/publish .

# Kopiera Python-virtuella miljön
COPY --from=python /venv /python

# Exponera porten för .NET-applikationen
EXPOSE 80

# Starta .NET-applikationen
ENTRYPOINT ["dotnet", "Q-verify-2025.dll"]
