
using Backend.Interfaces;
using Backend.Services;
using Microsoft.AspNetCore.DataProtection;
using Newtonsoft.Json;
using Serilog;
using Serilog.Core;



var builder = WebApplication.CreateBuilder(args);

var logger = new LoggerConfiguration()
    .WriteTo.File("Logs/log-.txt", rollingInterval: RollingInterval.Day)
    .CreateLogger();

builder.Host.UseSerilog(logger);
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddOpenApi();
builder.Services.AddSwaggerGen();

builder.Services.AddDataProtection()
    .PersistKeysToFileSystem(new DirectoryInfo("/keys")).SetApplicationName("AIAPI");

builder.Services.AddControllers().
    AddNewtonsoftJson(options =>
    {
        options.SerializerSettings.ReferenceLoopHandling = ReferenceLoopHandling.Ignore;
    });


builder.Services.AddHttpClient<IRagService, RagService>(client =>
{
    client.BaseAddress = new Uri("http://localhost:8000");
});

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
app.MapControllers();

app.Run();

