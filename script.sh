#!/bin/bash
# This script installs Docker and the GitLab Runner on a Linux machine.
# It takes three arguments: the GitLab Runner registration token, the GitLab Runner URL, and the GitLab Runner executor.
# The script installs Docker and the GitLab Runner, and then registers the GitLab Runner with the specified token, URL, and executor.
# The script also adds the GitLab Runner user to the docker group.


if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <GitLab Runner registration token> <GitLab Runner URL> <GitLab Runner executor>"
    exit 1
fi


# Install Docker
# This script installs Docker on a Linux machine.

echo "Installing Docker..."
sudo apt-get update
sudo apt-get install ca-certificates curl -y
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add the current user to the docker group
echo "Adding the current user to the docker group..."
sudo usermod -aG docker "$USER"

# Install GitLab Runner
# This script installs the GitLab Runner on a Linux machine.

# required command-line arguments
token=$1
url=$2
executor=$3

# Install the GitLab Runner
echo "Installing GitLab Runner..."
sudo curl -L --output /usr/local/bin/gitlab-runner https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-linux-amd64
sudo chmod +x /usr/local/bin/gitlab-runner

# Add the GitLab Runner user with a home directory
echo "add gitlab-runner user with home directory"
sudo useradd --comment 'GitLab Runner' --create-home gitlab-runner --shell /bin/bash

# Install the GitLab Runner service
echo "installing gitlab-runner service"
sudo gitlab-runner install --user=gitlab-runner --working-directory=/home/gitlab-runner

# Start the GitLab Runner service and register the GitLab Runner
echo "starting gitlab-runner service"
if sudo gitlab-runner start; then
    # Register the GitLab Runner
    echo "Registering GitLab Runner..."
    sudo gitlab-runner register --non-interactive --url "$url" --token "$token" --executor "$executor"
else
    echo "Failed to start GitLab Runner. Please check the logs and try again."
fi

# disable the GitLab Runner user's bash_logout file to prevent the GitLab Runner from being stopped when the user logs out.
echo "Disabling the GitLab Runner user's bash_logout file..."
sudo python -c "with open('/home/gitlab-runner/.bash_logout', 'r') as f: lines = f.readlines(); open('test.txt', 'w').writelines([f'# {line}' for line in lines])"

# Add the GitLab Runner user to the docker group
echo "Adding the GitLab Runner user to the docker group..."
sudo usermod -aG docker gitlab-runner
echo "GitLab Runner installation and registration completed successfully."

# Exit the script
exit