using System;
using System.ComponentModel.DataAnnotations;

namespace Q_verify_2025
{
    public class ErrorModel
    {
        [Key]
        public int Id { get; set; }
        public string? Competences { get; set; }
        public string? Pmnum { get; set; }
        public string? Cxlineroutenr { get; set; }
        public string? Location { get; set; }
        public string? Description { get; set; }
        public string? AnomalyFields { get; set; } // comma-separated
        public DateTime UploadTime { get; set; }
    }
}