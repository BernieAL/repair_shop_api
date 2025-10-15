
# SSH Key Pair
resource "aws_key_pair" "deployer" {
  key_name   = "${var.project_name}-key"
  public_key = file(pathexpand("~/.ssh/id_rsa.pub"))
}

# EC2 Instance (FREE TIER - t2.micro)
resource "aws_instance" "api" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.api.id]
  key_name                    = aws_key_pair.deployer.key_name
  associate_public_ip_address = true

  # Free tier: 30GB storage
  root_block_device {
    volume_size           = 20
    volume_type           = "gp3"
    delete_on_termination = true
  }

  # Startup script
user_data = templatefile("${path.module}/user-data.sh", {
  docker_username = var.docker_username
  docker_token    = var.docker_token
  db_password     = var.db_password
})

  tags = {
    Name = "${var.project_name}-instance"
  }
}
