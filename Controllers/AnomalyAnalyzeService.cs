using System.Text;
using Microsoft.EntityFrameworkCore;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Q_verify_2025.Controllers
{
    public class DbAnalyzerService : BackgroundService
{
    private readonly IServiceProvider _services;
    private readonly ILogger<DbAnalyzerService> _logger;
    private readonly IHttpClientFactory _httpClientFactory;

    public DbAnalyzerService(IServiceProvider services, ILogger<DbAnalyzerService> logger, IHttpClientFactory httpClientFactory)
    {
        _services = services;
        _logger = logger;
        _httpClientFactory = httpClientFactory;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
{
    _logger.LogInformation("DbAnalyzerService har startat.");
    
    while (!stoppingToken.IsCancellationRequested)
    {
        using var scope = _services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
        var httpClient = _httpClientFactory.CreateClient();

        var maximoRows = db.maximo_data.ToList();
        _logger.LogInformation($"Hämtade {maximoRows.Count} rader från maximo_data-tabellen.");

        if (maximoRows.Any())
        {
            var payload = JsonConvert.SerializeObject(maximoRows);
            var content = new StringContent(payload, Encoding.UTF8, "application/json");
            var response = await httpClient.PostAsync("http://localhost:5000//analyze-maximo-data", content);

            _logger.LogInformation($"Skickade POST-förfrågan. Statuskod: {response.StatusCode}");

            if (response.IsSuccessStatusCode)
            {
                var result = await response.Content.ReadAsStringAsync();
                _logger.LogInformation($"Svar från API: {result}");

                var json = JsonConvert.DeserializeObject<Dictionary<string, object>>(result);

                if (json?["anomalies"] is JArray anomalies)
                {
                    _logger.LogInformation($"Hittade {anomalies.Count} anomalier.");

                    var errors = new List<ErrorModel>();
                    var correct = new List<CorrectModel>();

                    foreach (var row in anomalies)
                    {
                        var anomalyFields = row["anomaly_fields"] as JArray;
                        var input = row["input"];

                        if (anomalyFields != null && anomalyFields.Count > 0)
                        {
                            errors.Add(new ErrorModel
                            {
                                Competences = input["competences"]?.ToString(),
                                Pmnum = input["pmnum"]?.ToString(),
                                Cxlineroutenr = input["cxlineroutenr"]?.ToString(),
                                Location = input["location"]?.ToString(),
                                Description = input["description"]?.ToString(),
                                AnomalyFields = string.Join(", ", anomalyFields.Select(f => f.ToString())),
                                UploadTime = DateTime.Now,
                                Status = false
                            });
                        }
                        else
                        {
                            correct.Add(new CorrectModel
                            {
                                Competences = input["competences"]?.ToString(),
                                Pmnum = input["pmnum"]?.ToString(),
                                Cxlineroutenr = input["cxlineroutenr"]?.ToString(),
                                Location = input["location"]?.ToString(),
                                Description = input["description"]?.ToString(),
                                UploadTime = DateTime.Now,
                                Status = true
                            });
                        }
                    }

                    if (errors.Count > 0)
                    {
                        db.Errors.AddRange(errors);
                        _logger.LogInformation($"Lade till {errors.Count} rader i Errors-tabellen.");
                    }

                    if (correct.Count > 0)
                    {
                        db.Corrects.AddRange(correct);
                        _logger.LogInformation($"Lade till {correct.Count} rader i Corrects-tabellen.");
                    }

                    await db.SaveChangesAsync();

                }
            }
            
            else
            {
                _logger.LogError($"API-anrop misslyckades med statuskod: {response.StatusCode}");
            }
            
        }
        
        db.Database.ExecuteSqlRaw("TRUNCATE TABLE [dbo].[maximo_data]");
        
        db.SaveChanges();

        _logger.LogInformation("Tömde maximo_data-tabellen.");
        
        _logger.LogInformation("Väntar i 5 minuter innan nästa körning...");
        
        await Task.Delay(TimeSpan.FromMinutes(5), stoppingToken);
    }
}
}
}