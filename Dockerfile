FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app

# Copy the .NET project file and restore dependencies
COPY Q-verify-2025.csproj ./
RUN dotnet restore

# Copy the rest of the .NET project files and build the application
COPY . ./
RUN dotnet publish -c Release -o /app/publish

# Use a runtime image for the final stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app

# Copy the published files from the build stage
COPY --from=build /app/publish .

# Expose the .NET app port
EXPOSE 5161

# Run the .NET app
CMD ["dotnet", "Q-verify-2025.dll"]