using Backend.Dtos;
using Backend.Interfaces;
using Backend.Services;
using Microsoft.AspNetCore.Mvc;

namespace Backend.Controllers;

[ApiController]
[Route("rag")]
public class RagController(IRagService ragService, ILogger<RagController> logger) : ControllerBase
{
    private readonly IRagService _ragService = ragService;
    private readonly ILogger<RagController> _logger = logger;

    [HttpGet]
    public IActionResult Get()
    {
        _logger.LogInformation("GET request received at /rag");
        return Ok("Hello World");
    }
    [HttpPost]
    [Route("query")]
    public async Task<IActionResult> PostQuery([FromBody] PromptDto prompt)
    {
        var res = await _ragService.Query(prompt);
        _logger.LogInformation("Query received: {Prompt}", prompt.Content);
        if (res.IsSuccess)
        {
            _logger.LogInformation("Query successful, returning data. Data: {data}", res.Data);
            return Ok(res.Data);
        }
        else
        {
            _logger.LogError("Query failed: {ErrorMessage}", res.ErrorMessage);
            return BadRequest(res.ErrorMessage);
        }
    }

    [HttpPost]
    [Route("add")]
    public async Task<IActionResult> PostAdd([FromBody] PromptDto prompt)
    {
        var res = await _ragService.Add(prompt);
        _logger.LogInformation("Add request received: {Prompt}", prompt.Content);
        if (res.IsSuccess)
        {
            _logger.LogInformation("Add successful, returning OK.");
            return Ok();
        }
        else
        {
            _logger.LogError("Add failed: {ErrorMessage}", res.ErrorMessage);
            return BadRequest(res.ErrorMessage);
        }
    }
}