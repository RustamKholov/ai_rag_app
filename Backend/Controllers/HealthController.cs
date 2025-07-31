using Microsoft.AspNetCore.Mvc;

namespace Backend.Controllers;

[ApiController]
[Route("health")]
public class HealthController(ILogger<HealthController> logger) : ControllerBase
{
    private readonly ILogger<HealthController> _logger = logger;

    [HttpGet]
    public IActionResult Get()
    {
        _logger.LogInformation("Health check");
        return Ok("Application is healthy and running.");
    }
    
}