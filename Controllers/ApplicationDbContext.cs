using Microsoft.EntityFrameworkCore;
using Q_verify_2025.Models;

namespace Q_verify_2025.Controllers
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options) { }

        public DbSet<ErrorModel> Errors { get; set; }
        public DbSet<CorrectModel> Corrects { get; set; }
        public DbSet<MaximoDataModel> maximo_data { get; set; }
    }
}