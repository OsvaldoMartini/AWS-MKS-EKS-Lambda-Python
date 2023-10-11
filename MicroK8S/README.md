#  MicroK8S config

```bash
  sudo microk8s kubectl get nodes

  alias k='microk8s kubectl'

  # Activation
  sudo rm -rf ~/.kube/
  # To Create a trusted Certificates
  mkdir -p $HOME/.kube/
  
  sudo mkdir kubectl config view --raw

  sudo microk8s kubectl config view --raw > ~/.kube/config

  # Using Oficial KUBECTL instead of microK8S
  sudo snap install kubectl --classic

  # Expected:
  apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUREekNDQWZlZ0F3SUJBZ0lVUmJKcGs5Rk9scGtPN2VycVRXZ1k3K3YvM1ZRd0RRWUpLb1pJaHZjTkFRRUwKQlFBd0Z6RVZNQk1HQTFVRUF3d01NVEF1TVRVeUxqRTRNeTR4TUI0WERUSXpNVEF4TVRFNE5EQTFNVm9YRFRNegpNVEF3T0RFNE5EQTFNVm93RnpFVk1CTUdBMVVFQXd3TU1UQXVNVFV5TGpFNE15NHhNSUlCSWpBTkJna3Foa2lHCjl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUFzTGJUL1ZNWDMrR1EwWW5vZFU5aVpqZjlLbHFlU3ZKbDg4QkUKZEZqekt5TmtQeHpoU3lpbVRWcVJKOHYzQ0lCOVNRNDFTeFRUYk8yd1hLYkpCYnpUTmY3R1dIUFB1QVgxdE0rdApXWHVFeG0raWFQenlkQWMvOTlXYm4zQ1c5SVpiUUdKMkFtYUxQdVdMSnR5c3g1RktPOVUvN2dBR2szYkNjOXBoCmNEUkZIUm84QmtuYkZmU3hmYzRiUCtKUGdkRzg4emJKOHE0bnhRc3kwdlp1b2ZySWJDcUdBOWdJemFNTXUzN0UKRGw0YjFsSUthd0RZRnJ1LzRBaG1vbnRsaU1na21KbWFoM3p0U2tWMjFLSTZubEUxZGFBUnVYaFFMZHZuWEsvMApFa1ZYNEZ1YnlCdWFTWUhYT3ovRGRvRHd1MUhxVC9BaUhSUXhLaTF4YVliYU9rT1pjUUlEQVFBQm8xTXdVVEFkCkJnTlZIUTRFRmdRVWtSNkdZcmdiYklqbE4zYWFLM2FmbmtOTjZHZ3dId1lEVlIwakJCZ3dGb0FVa1I2R1lyZ2IKYklqbE4zYWFLM2FmbmtOTjZHZ3dEd1lEVlIwVEFRSC9CQVV3QXdFQi96QU5CZ2txaGtpRzl3MEJBUXNGQUFPQwpBUUVBSzB5N3UvNFlicnFpSkhHYS9pR3RMQWhiWUFaVStEd2tuR1J0VTNrTExFdmFlSDFVczJsUjA2cE1IdStGCkp5QW1MYUlKeThkb1BGdE9oUXRNdlNRTklFTXd6KzU5WnU5QzVHMk9nT0R5VGU0YnZsSTVQMkROS0p4SjZ4N0kKZFhta2hGZ29icHJFQ0JBSW54eFg4eUdZdE5QOGJXdlpTNUFjeEU1cmV1L1lSNWx1bG0rWHY0ckhJOHFOby9aSgpaZ3FoUElNdGg2WVFramh3UE1UTDBMZTBWMDN1THpodktsb0k3QXA0dzd5Nll2cDFlWStGZGZiYmNBdFRZUTFrCnBWeVUyRkJOeUREaWRrMWw2Wjh2MjJVTTdXZGs4QkxzWklId0FIZ21hS3VBKzhtTEgzNHpsczc4Z0dYaDR5Y2MKeHJqaDBjYTRwVXRZSldJcHNuOUVFY2g1MXc9PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==
    server: https://127.0.0.1:16443
  name: microk8s-cluster
contexts:
- context:
    cluster: microk8s-cluster
    user: admin
  name: microk8s
current-context: microk8s
kind: Config
preferences: {}
users:
- name: admin
  user:
    token: b08zUlZBTnM4Q2cwV0dZaFZFWHR5dWRhL054Z2J5Tk1iU3FVU0wrRlVoYz0K

  
  sudo chown -R omartini ~/.kube



```