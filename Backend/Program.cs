
var builder = WebApplication.CreateBuilder(args);


builder.Services.AddEndpointsApiExplorer();
builder.Services.AddOpenApi();
builder.Services.AddSwaggerGen();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "Backend API V1");
        c.RoutePrefix = "swagger";
    });
}

app.UseHttpsRedirection();

app.MapGet("/", () => "Welcome to Backend API! Visit /swagger for documentation.")
    .WithName("GetRoot")
    .WithSummary("API Root")
    .WithDescription("Returns a welcome message")
    .WithOpenApi();

app.MapGet("/api/health", () => new
{
    Status = "Healthy",
    Timestamp = DateTime.UtcNow,
    Version = "1.0.0"
})
    .WithName("GetHealth")
    .WithSummary("Health Check")
    .WithDescription("Returns the health status of the API")
    .WithOpenApi();


app.Run();

