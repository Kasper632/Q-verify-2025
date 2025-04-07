using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Q_verify_2025
{
    public class ErrorModel
    {
        [Key]
        public int Id { get; set; }
        public required string Competences { get; set; }
        public required string Pmnum { get; set; }
        public required string Cxlineroutenr { get; set; }
        public required string Location { get; set; }
        public required string Description { get; set; }
        public required string AnomalyFields { get; set; } // comma-separated
        public DateTime UploadTime { get; set; }

        [Column(TypeName = "bit")]
        public bool Status { get; set; } // true for correct, false for error
    }
}