using System.Net;

namespace Backend.Helpers;

public class ApiResult
{
    public bool IsSuccess { get; set; }
    public string? ErrorMessage { get; set; }
    public HttpStatusCode StatusCode { get; set; }
    
    protected ApiResult(){}
    
    public static ApiResult Success() => new ApiResult {IsSuccess = true};

    public static ApiResult Error(string errorMessage) =>
        new ApiResult { IsSuccess = false, ErrorMessage = errorMessage };

    public static ApiResult Error(HttpStatusCode statusCode) => new ApiResult
        { IsSuccess = false, ErrorMessage = "Unknown error", StatusCode = statusCode };

    public static ApiResult Error(string errorMessage, HttpStatusCode statusCode) => new ApiResult
        { IsSuccess = false, ErrorMessage = errorMessage, StatusCode = statusCode };

    public static ApiResult Error() => new ApiResult
        { IsSuccess = false, ErrorMessage = "Unknown error", StatusCode = HttpStatusCode.InternalServerError };
    
}

public class ApiResult<TSuccessData> : ApiResult
{
    public TSuccessData? Data { get; set; }
    public static ApiResult<TSuccessData> Success(TSuccessData data, HttpStatusCode statusCode)
    {
        return new ApiResult<TSuccessData>{IsSuccess = true, Data = data, StatusCode = statusCode};
    }
    public new static ApiResult<TSuccessData> Error(string errorMessage, HttpStatusCode statusCode)
    {
        return new ApiResult<TSuccessData>{IsSuccess = false, ErrorMessage = errorMessage, StatusCode = statusCode};
    }
    public new static ApiResult<TSuccessData> Error(HttpStatusCode statusCode)
    {
        return new ApiResult<TSuccessData>{IsSuccess = false, ErrorMessage = "Unknown error", StatusCode = statusCode};
    }
    public static ApiResult<TSuccessData> Error(Exception ex)
    {
        return new ApiResult<TSuccessData>{IsSuccess = false, ErrorMessage = ex.Message, StatusCode = HttpStatusCode.InternalServerError};
    }
    public new static ApiResult<TSuccessData> Error(string errorMessage)
    {
        return new ApiResult<TSuccessData>{IsSuccess = false, ErrorMessage = errorMessage, StatusCode = HttpStatusCode.InternalServerError};
    }
    public new static ApiResult<TSuccessData> Error()
    {
        return new ApiResult<TSuccessData>{IsSuccess = false, ErrorMessage = "Unknown error", StatusCode = HttpStatusCode.InternalServerError};
    }
    public static ApiResult<TSuccessData> Success(HttpStatusCode statusCode)
    {
        return new ApiResult<TSuccessData>{IsSuccess = true, Data = default, StatusCode = statusCode};
    }
    public new static ApiResult<TSuccessData> Success()
    {
        return new ApiResult<TSuccessData>{IsSuccess = true, Data = default, StatusCode = HttpStatusCode.OK};
    }
}