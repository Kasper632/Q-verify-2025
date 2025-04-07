using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Primitives;
using Newtonsoft.Json;
using Q_verify_2025.Models;
using Microsoft.EntityFrameworkCore;

namespace Q_verify_2025.Controllers
{
    public class AnomalyController : Controller
    {
        private readonly HttpClient _httpClient;
        private readonly string _uploadPath;
        private readonly string _flaskUrl;

        private readonly ApplicationDbContext _db;

        public AnomalyController(HttpClient httpClient, IConfiguration configuration, ApplicationDbContext db)
        {
            _httpClient = httpClient;
            _uploadPath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "uploads");
            _flaskUrl = configuration["ApiUrl:FlaskUrl"] ?? throw new ArgumentNullException("FlaskUrl is not configured in appsettings.json");
            _db = db;

            if (!Directory.Exists(_uploadPath))
            {
                Directory.CreateDirectory(_uploadPath);
            }
        }

        public IActionResult PersonalData() => View();

        public IActionResult MaximoData() => View();

        public async Task<IActionResult> MaximoDatabase()
        {
            var result = await GetAllMaximoDataAsync();
            return View(result);
        }

        public async Task<MaximoDataResult> GetAllMaximoDataAsync()
        {
            return new MaximoDataResult
            {
                Corrects = await _db.Corrects.Select(c => new CorrectModel
                {
                    Id = c.Id,
                    Competences = c.Competences,
                    Pmnum = c.Pmnum,
                    Cxlineroutenr = c.Cxlineroutenr,
                    Location = c.Location,
                    Description = c.Description,
                    Status = c.Status
                }).ToListAsync(),

                Errors = await _db.Errors.Select(e => new ErrorModel
                {
                    Id = e.Id,
                    Competences = e.Competences,
                    Pmnum = e.Pmnum,
                    Cxlineroutenr = e.Cxlineroutenr,
                    Location = e.Location,
                    Description = e.Description,
                    AnomalyFields = e.AnomalyFields,
                    Status = e.Status
                }).ToListAsync()
            };
        }

        [HttpPost]
        public IActionResult UploadFile(IFormFile file, string view)
        {
            if (file == null || file.Length == 0)
            {
                ViewData["Message"] = "No file selected.";
                return View(view);
            }

            try
            {
                var filePath = Path.Combine(_uploadPath, file.FileName);
                using (var stream = new FileStream(filePath, FileMode.Create))
                {
                    file.CopyTo(stream);
                }

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
                ViewData["FileInfo"] = fileInfoModel;
            }
            catch (Exception ex)
            {
                ViewData["Message"] = $"Error uploading file: {ex.Message}";
            }

            return View(view);
        }

        [HttpPost]
        public async Task<IActionResult> Analyze(string view, string route)
        {
            try
            {
                string apiUrl = $"{_flaskUrl}/{route}";

                var uploadedFiles = Directory.GetFiles(_uploadPath);
                if (uploadedFiles.Length == 0)
                {
                    ViewData["Message"] = "No uploaded file found.";
                    return View(view);
                }

                string uploadedFilePath = uploadedFiles.OrderByDescending(f => new FileInfo(f).LastWriteTime).First();
                string uploadedFileName = Path.GetFileName(uploadedFilePath);

                var fileInfo = new FileInfo(uploadedFilePath);
                var fileInfoModel = new FileInfoModel
                {
                    FileName = uploadedFileName,
                    FileSize = Math.Round(fileInfo.Length / 1024.0, 2),
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

                                var errorEntities = new List<ErrorModel>();
                                var correctEntities = new List<CorrectModel>();

                                foreach (var anomaly in anomalies)
                                {
                                    var anomalyFields = anomaly["anomaly_fields"] as Newtonsoft.Json.Linq.JArray;
                                    var input = anomaly["input"];

                                    if (anomalyFields != null && anomalyFields.Count > 0)
                                    {
                                        errorEntities.Add(new ErrorModel
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
                                        correctEntities.Add(new CorrectModel
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

                                if (errorEntities.Count > 0)
                                {
                                    _db.Errors.AddRange(errorEntities);
                                }

                                if (correctEntities.Count > 0)
                                {
                                    _db.Corrects.AddRange(correctEntities);
                                }

                                if (errorEntities.Count > 0 || correctEntities.Count > 0)
                                {
                                    await _db.SaveChangesAsync();
                                }
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

            return View(view);
        }

        [HttpPost]
        public async Task<IActionResult> AnalyzePersonalData()
        {
            try
            {
                string apiUrl = $"{_flaskUrl}/analyze-personal-data";

                var uploadedFiles = Directory.GetFiles(_uploadPath);
                if (uploadedFiles.Length == 0)
                {
                    ViewData["Message"] = "No uploaded file found.";
                    return View("PersonalData");
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

            return View("PersonalData");
        }

        public async Task<IActionResult> Delete(int id, string table)
        {
            if (table.Equals("corrects"))
            {
                var correctItem = await _db.Corrects.FindAsync(id);

                if (correctItem != null) _db.Corrects.Remove(correctItem);

            }
            else
            {
                var errorItem = await _db.Errors.FindAsync(id);
                if (errorItem != null) _db.Errors.Remove(errorItem);

            }

            await _db.SaveChangesAsync();

            return RedirectToAction("MaximoDatabase");
        }

        public async Task<IActionResult> Edit(int id, string competences, string pmnum, string cxlineroutenr, string location, string description)
        {
            var item = await _db.Errors.FindAsync(id);
            if (item != null) _db.Errors.Remove(item);

            var newMaximomodel = new MaximoDataModel
            {
                Competences = competences,
                Pmnum = pmnum,
                Cxlineroutenr = cxlineroutenr,
                Location = location,
                Description = description
            };

            _db.maximo_data.Add(newMaximomodel);

            await _db.SaveChangesAsync();

            return RedirectToAction("MaximoDatabase");
        }
    }
}
