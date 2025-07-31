using Backend.Dtos;
using Backend.Helpers;

namespace Backend.Interfaces;

public interface IRagService
{
    Task<ApiResult<string?>> Query(PromptDto prompt);
    Task<ApiResult> Add(PromptDto prompt);
}