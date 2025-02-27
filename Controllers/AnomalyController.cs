using Q_verify_2025.Services;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using System.Net.Http;
using System.IO;

namespace Q_verify_2025.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AnomalyController : Controller
    {
        private readonly AnomalyService _anomalyService;
        private readonly HttpClient _httpClient;

        public AnomalyController()
        {
            _anomalyService = new AnomalyService();
            _httpClient = new HttpClient(); // Create instance of AnomalyService
        }
        [HttpGet("index")]
        public IActionResult Index()
        {
            return View("Predict");
        }

        [HttpPost("detect-anomalies")]
        public async Task<IActionResult> DetectAnomalies(IFormFile file)
        {
            if (file == null || file.Length == 0)
            {
                return BadRequest("File is empty.");
            }

            var result = await _anomalyService.GetAnomalyPredictionAsync(file);

            if (result != null)
            {
                return Json(new
                {
                    success = true,
                    prediction = result.Predictions,
                    accuracy = result.Accuracy,
                    modelAccuracy = result.ModelAccuracy
                });
            
            }
            return BadRequest("Prediction failed.");
        }

    }
}
