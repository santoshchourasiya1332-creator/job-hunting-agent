terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # GitLab Managed HTTP State Backend
  backend "http" {}
}

# AWS Provider automatically picks AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY from GitLab CI/CD
provider "aws" {
  region = var.aws_region
}

# Network Topology Configuration
resource "aws_vpc" "job_agent_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "job-agent-vpc"
    Environment = var.environment
  }
}

resource "aws_subnet" "job_agent_subnet" {
  vpc_id                  = aws_vpc.job_agent_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "${var.aws_region}a"

  tags = {
    Name = "job-agent-public-subnet"
  }
}

resource "aws_internet_gateway" "job_agent_igw" {
  vpc_id = aws_vpc.job_agent_vpc.id

  tags = {
    Name = "job-agent-igw"
  }
}

resource "aws_route_table" "job_agent_route_table" {
  vpc_id = aws_vpc.job_agent_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.job_agent_igw.id
  }
}

resource "aws_route_table_association" "job_agent_rta" {
  subnet_id      = aws_subnet.job_agent_subnet.id
  route_table_id = aws_route_table.job_agent_route_table.id
}

# Security Group
resource "aws_security_group" "job_agent_sg" {
  name        = "job-agent-sg"
  description = "Allow inbound SSH, HTTP, and HTTPS traffic"
  vpc_id      = aws_vpc.job_agent_vpc.id

  ingress {
    description = "SSH Access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP Traffic"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS Traffic"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# SSH Key Pair
resource "aws_key_pair" "deployer_key" {
  key_name   = "job-agent-deployer-key"
  public_key = var.public_key_data
}

# Ubuntu 22.04 AMI Lookup
data "aws_ami" "ubuntu_2204" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# EC2 Compute Provisioning
resource "aws_instance" "k3s_node" {
  ami                    = data.aws_ami.ubuntu_2204.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.job_agent_subnet.id
  vpc_security_group_ids = [aws_security_group.job_agent_sg.id]
  key_name               = aws_key_pair.deployer_key.key_name

  root_block_device {
    volume_size           = 20
    volume_type           = "gp3"
    delete_on_termination = true
    encrypted             = false
  }

  user_data = file("${path.module}/user_data.sh")

  tags = {
    Name        = "k3s-autonomous-agent-node"
    Role        = "Kubernetes-Control-Plane"
    Environment = var.environment
  }
}