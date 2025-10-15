
output "instance_public_ip" {
  description = "Public IP of EC2 instance"
  value       = aws_instance.api.public_ip
}

output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.api.id
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "api_url" {
  description = "API URL"
  value       = "http://${aws_instance.api.public_ip}:8000"
}

output "api_health_check" {
  description = "Health check URL"
  value       = "http://${aws_instance.api.public_ip}:8000/health"
}

output "api_docs" {
  description = "API documentation URL"
  value       = "http://${aws_instance.api.public_ip}:8000/docs"
}

output "ssh_command" {
  description = "SSH command to connect"
  value       = "ssh -i ~/.ssh/id_rsa ubuntu@${aws_instance.api.public_ip}"
}
