using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Http;
using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Threading.Tasks;

namespace Q_verify_2025.Controllers
{
    public class iForestController : Controller
    {
        private readonly HttpClient _httpClient;

        public iForestController(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        public IActionResult Index()
        {
            return View();
        }

        [HttpPost]
        public async Task<IActionResult> UploadFile(IFormFile file)
        {
            if (file == null || file.Length == 0)
            {
                ViewData["Message"] = "Please select a valid CSV file.";
                return View("Index");
            }

            using var content = new MultipartFormDataContent();
            using var fileStream = file.OpenReadStream();
            using var fileContent = new StreamContent(fileStream);

            // Sätter korrekt content-type för filen
            fileContent.Headers.ContentType = new MediaTypeHeaderValue("text/csv");
            content.Add(fileContent, "file", file.FileName ?? "uploaded_file.csv");

            try
            {
                // Skicka filen till Flask-API:t
                var response = await _httpClient.PostAsync("http://127.0.0.1:5000/process-file", content);
                var jsonResponse = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                {
                    ViewData["Message"] = $"Error processing file: {jsonResponse}";
                    return View("Index");
                }

                var result = JsonSerializer.Deserialize<Dictionary<string, object>>(jsonResponse);

                ViewData["Message"] = result["message"].ToString();
                ViewData["Anomalies"] = JsonSerializer.Deserialize<List<Dictionary<string, string>>>(result["anomalies"].ToString());
            }
            catch (Exception ex)
            {
                ViewData["Message"] = "Error processing file: " + ex.Message;
            }

            return View("Index");
        }
    }
}
