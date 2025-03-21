namespace Q_verify_2025.Models
{
    public class FileInfoModel
    {
        public string FileName { get; set; }
        public double FileSize { get; set; }
        public string FileFormat { get; set; }
        public string UploadTime { get; set; }
        public int AnomalyCount { get; set; } = 0;
    }
}
