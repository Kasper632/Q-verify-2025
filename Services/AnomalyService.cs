using System.Net.Http;
using System.Threading.Tasks;
using Newtonsoft.Json;
using System.Collections.Generic;
using Microsoft.AspNetCore.ResponseCompression;

namespace Q_verify_2025.Services
{
    public class AnomalyService
    {
        private readonly HttpClient _httpClient;

        public AnomalyService()
        {
            _httpClient = new HttpClient();
        }

        public async Task<PredictionResult> GetAnomalyPredictionAsync(IFormFile file)
        {
            var formData = new MultipartFormDataContent();
            var fileContent = new StreamContent(file.OpenReadStream());
            fileContent.Headers.Add("Content-Type", "application/octet-stream");
            formData.Add(fileContent, "file", file.FileName);

            var response = await _httpClient.PostAsync("http://localhost:5000/predict", formData);

            if (response.IsSuccessStatusCode)
            {
                var result = await response.Content.ReadAsStringAsync();
                var prediction = JsonConvert.DeserializeObject<PredictionResult>(result);

                if (prediction == null)
                {
                    throw new InvalidOperationException("Failed to deserialize API response.");
                }

                return prediction;
            }
            else
            {
                throw new HttpRequestException($"API request failed with status code {response.StatusCode}.");
            }
        }

        public class PredictionResult
        {
            public List<int>? Predictions { get; set; }
            public List<float>? Accuracy { get; set; }
            public float ModelAccuracy { get; set; }
        }
    }
}