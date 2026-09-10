output "instance_id" {
  value       = aws_instance.k3s_node.id
  description = "EC2 Instance unique identifier."
}

output "ec2_public_ip" {
  value       = aws_instance.k3s_node.public_ip
  description = "Public IPv4 address assigned to the host."
}

output "ssh_command" {
  value       = "ssh -i ~/.ssh/id_rsa ubuntu@${aws_instance.k3s_node.public_ip}"
  description = "Administrative SSH access command."
}