using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("api/status")]
public class StatusController : ControllerBase
{
    private static string _latestMessage = "";

    [HttpGet]
    public IActionResult GetLatest()
    {
        return Ok(new { message = _latestMessage });
    }

    public static void UpdateMessage(string msg)
    {
        _latestMessage = msg;
    }
}
