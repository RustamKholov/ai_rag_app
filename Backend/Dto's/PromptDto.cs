using System.ComponentModel.DataAnnotations;

namespace Backend.Dtos;

public class PromptDto
{
    public string? Content { get; set; } = string.Empty;
    public string? Question { get; set; } = string.Empty;
}