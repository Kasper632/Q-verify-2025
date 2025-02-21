using System.Net.Http;
using System.Threading.Tasks;
using Newtonsoft.Json;
using System.Collections.Generic;

namespace Q_verify_2025.Services
{
    public class AnomalyService
    {
        private readonly HttpClient _httpClient;

        public AnomalyService()
        {
            _httpClient = new HttpClient();
        }

        public async Task<Dictionary<string, object>> PredictAsync(Dictionary<string, string> inputData)
        {
            try
            {
                // Skapa form-data från input
                var content = new FormUrlEncodedContent(inputData);

                // Skicka POST-anrop till Flask API
                var response = await _httpClient.PostAsync("http://127.0.0.1:5000/predict", content);

                if (response.IsSuccessStatusCode)
                {
                    // Läs JSON-svaret
                    var result = await response.Content.ReadAsStringAsync();
                    return JsonConvert.DeserializeObject<Dictionary<string, object>>(result);
                }
                else
                {
                    // Hantera fel
                    throw new Exception("API request failed.");
                }
            }
            catch (Exception ex)
            {
                throw new Exception($"Error calling API: {ex.Message}");
            }
        }
    }
}