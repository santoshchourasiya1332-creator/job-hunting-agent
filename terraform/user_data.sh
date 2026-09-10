#!/bin/bash
set -e

echo "===> [Phase 1/5]: Updating System Packages..."
apt-get update && apt-get upgrade -y
apt-get install -y curl htop git open-iscsi

echo "===> [Phase 2/5]: Configuring Swap Memory (2GB)..."
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab

echo "===> [Phase 3/5]: Tuning Kernel Parameters..."
sysctl -w vm.swappiness=10
sysctl -w vm.vfs_cache_pressure=50
echo 'vm.swappiness=10' >> /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' >> /etc/sysctl.conf

echo "===> [Phase 4/5]: Installing K3s Cluster..."
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--disable=servicelb --disable=traefik" sh -

echo "===> [Phase 5/5]: Validating System Readiness..."
systemctl enable k3s
systemctl restart k3s

until [ -f /etc/rancher/k3s/k3s.yaml ]; do
  echo "Waiting for K3s initialization..."
  sleep 3
done

chmod 644 /etc/rancher/k3s/k3s.yaml
echo "===> System Initialization Complete."