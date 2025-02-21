using Q_verify_2025.Services;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;

namespace Q_verify_2025.Controllers
{
    public class AnomalyController : Controller
    {
        private readonly AnomalyService _anomalyService;

        public AnomalyController()
        {
            _anomalyService = new AnomalyService(); // Skapa instans av AnomalyService
        }

        public IActionResult Index()
        {
            return View();
        }

        [HttpPost]
        public async Task<ActionResult> Predict(int employees, double revenue, double profitMargin, double creditRating, int yearsInBusiness)
        {
            try
            {
                // Skapa inputdata för Flask API
                var inputData = new Dictionary<string, string>
        {
            { "employees", employees.ToString() },
            { "revenue", revenue.ToString() },
            { "profit_margin", profitMargin.ToString() },
            { "credit_rating", creditRating.ToString() },
            { "years_in_business", yearsInBusiness.ToString() }
        };

                // Anropa API-tjänsten
                var analysisResults = await _anomalyService.PredictAsync(inputData); // Använd rätt service här

                // Skicka tillbaka analysresultaten till vyn
                return View(analysisResults);
            }
            catch (Exception ex)
            {
                // Hantera fel
                return View("Error");
            }
        }
    }
}
