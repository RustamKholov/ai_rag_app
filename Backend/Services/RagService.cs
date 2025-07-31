using Backend.Dtos;
using Backend.Helpers;
using Backend.Interfaces;

namespace Backend.Services;

public class RagService(HttpClient client) : IRagService
{
    private readonly HttpClient _client = client;

    public async Task<ApiResult<string?>> Query(PromptDto prompt)
    {
        var res = await _client.PostAsJsonAsync("/query", prompt);
        return res.IsSuccessStatusCode ? ApiResult<string?>.Success(await res.Content.ReadAsStringAsync(), res.StatusCode) : ApiResult<string?>.Error(res.StatusCode);
    }

    public async Task<ApiResult> Add(PromptDto prompt)
    {
        var res = await _client.PostAsJsonAsync("/add", prompt);
        return res.IsSuccessStatusCode ? ApiResult.Success() : ApiResult.Error(res.StatusCode);
    }
}