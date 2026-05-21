variable "bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "website_dir" {
  description = "Path to the local website directory to upload"
  type        = string
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}
