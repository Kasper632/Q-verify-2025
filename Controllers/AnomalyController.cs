using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Http;
using System;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Q_verify_2025.Models;

namespace Q_verify_2025.Controllers
{
    public class AnomalyController : Controller
    {
        private readonly HttpClient _httpClient;
        private readonly string _uploadPath;

        public AnomalyController(HttpClient httpClient)
        {
            _httpClient = httpClient;
            _uploadPath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "uploads");

            if (!Directory.Exists(_uploadPath))
            {
                Directory.CreateDirectory(_uploadPath);
            }
        }

        public IActionResult Index()
        {
            return View();
        }

        [HttpPost]
        public IActionResult UploadFile(IFormFile file)
        {
            if (file == null || file.Length == 0)
            {
                ViewData["Message"] = "No file selected.";
                return View("Index");
            }

            try
            {
                var filePath = Path.Combine(_uploadPath, file.FileName);
                using (var stream = new FileStream(filePath, FileMode.Create))
                {
                    file.CopyTo(stream);
                }

                // Skapa en FileInfoModel och skicka den till vyn
                var fileInfo = new FileInfo(filePath);
                var fileInfoModel = new FileInfoModel
                {
                    FileName = file.FileName,
                    FileSize = Math.Round(file.Length / 1024.0, 2),
                    FileFormat = Path.GetExtension(file.FileName).ToUpper(),
                    UploadTime = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")
                };

                ViewData["Message"] = $"File '{file.FileName}' uploaded successfully!";
                ViewData["Uploaded"] = true;
                ViewData["FileInfo"] = fileInfoModel; // Skicka filinformationen till vyn
            }
            catch (Exception ex)
            {
                ViewData["Message"] = $"Error uploading file: {ex.Message}";
            }

            return View("Index");
        }


        [HttpPost]
        public async Task<IActionResult> Analyze()
        {
            try
            {
                string apiUrl = "http://localhost:5000/process-file";

                var uploadedFiles = Directory.GetFiles(_uploadPath);
                if (uploadedFiles.Length == 0)
                {
                    ViewData["Message"] = "No uploaded file found.";
                    return View("Index");
                }

                string uploadedFilePath = uploadedFiles.OrderByDescending(f => new FileInfo(f).LastWriteTime).First();
                string uploadedFileName = Path.GetFileName(uploadedFilePath);

               
                var fileInfo = new FileInfo(uploadedFilePath);
                var fileInfoModel = new FileInfoModel
                {
                    FileName = uploadedFileName,
                    FileSize = Math.Round(fileInfo.Length / 1024.0, 2),  // Storlek i KB
                    FileFormat = Path.GetExtension(uploadedFileName).ToUpper(),
                    UploadTime = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")
                };

                ViewData["FileInfo"] = fileInfoModel;

                using (var fileStream = new FileStream(uploadedFilePath, FileMode.Open, FileAccess.Read))
                using (var content = new MultipartFormDataContent())
                {
                    content.Add(new StreamContent(fileStream), "file", uploadedFileName);

                    var response = await _httpClient.PostAsync(apiUrl, content);
                    var responseString = await response.Content.ReadAsStringAsync();

                    if (response.IsSuccessStatusCode)
                    {
                        var jsonResponse = JsonConvert.DeserializeObject<Dictionary<string, object>>(responseString);

                        if (jsonResponse != null)
                        {
                            var anomalies = jsonResponse["anomalies"] as Newtonsoft.Json.Linq.JArray;

                            if (anomalies != null)
                            {
                                ViewData["AnalysisResult"] = anomalies;
                                ViewData["Message"] = "Analysis completed successfully!";
                            }
                            else
                            {
                                ViewData["Message"] = "No anomalies found.";
                            }
                        }
                    }
                    else
                    {
                        ViewData["Message"] = $"Error during analysis: {responseString}";
                    }
                }
            }
            catch (Exception ex)
            {
                ViewData["Message"] = $"Error analyzing file: {ex.Message}";
            }

            return View("Index");
        }
    }
}
