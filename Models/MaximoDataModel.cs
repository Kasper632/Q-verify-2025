using System.ComponentModel.DataAnnotations;

public class MaximoDataModel
{
    [Key]
    public int Id { get; set; }
    public string? Competences { get; set; }
    public string? Pmnum { get; set; }
    public string? Cxlineroutenr { get; set; }
    public string? Location { get; set; }
    public string? Description { get; set; }
    public bool? Status { get; set; } // true for correct, false for error
}