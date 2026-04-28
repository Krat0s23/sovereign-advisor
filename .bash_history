sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ubuntu
sudo apt install -y ubuntu-drivers-common
sudo ubuntu-drivers autoinstall
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker
nvidia-smi
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update
sudo rm /etc/apt/sources.list.d/nvidia-container-toolkit.list
# Add the GPG key
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
# Add the repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list |   sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' |   sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update
sudo rm /etc/apt/sources.list.d/nvidia-container-toolkit.list
# Add GPG key (if you haven't already)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
# Add the generic repository list
echo 'deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://nvidia.github.io/libnvidia-container/stable/deb/ /' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update
sudo rm /etc/apt/sources.list.d/nvidia-container-toolkit.list
echo 'deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://nvidia.github.io/libnvidia-container/stable/deb/amd64/ /' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update
sudo apt install -y nvidia-container-toolkit
nvidia-smi
sudo reboot
nvidia-smi
ls
cd sovereign-advisor/
ls
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
docker run -d   --name ollama   --gpus all   -p 11434:11434   -v ollama_data:/root/.ollama   ollama/ollama
vi resize-root-ebs.sh
ls
chmod +x resize-root-ebs.sh
sudo ./resize-root-ebs.sh
docker run -d   --name ollama   --gpus all   -p 11434:11434   -v ollama_data:/root/.ollama   ollama/ollama
docker compose up -d --build
docker compose version
sudo apt update
sudo apt install -y docker-compose-plugin
docker compose version
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
python3 --version
pip3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install fastapi uvicorn langchain openai streamlit faiss-cpu
docker compose up -d --build
docker compose
docker
docker compose up -d --build
sudo apt install -y docker-compose-plugin
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-compose-plugin
docker compose up -d --build
ls
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
vi docker-compose.yaml
ls
docker compose up -d --build
sudo lsof -i :11434
docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Ports}}"
docker stop ollama
docker rm ollama
docker compose up -d --build
docker exec -it ollama ollama pull llama3
docker compose exec ollama ollama pull llama3
docker exec -it sovereign-advisor-ollama-1 ollama pull llama3
resolvectl status
sudo mkdir -p /etc/docker
cat <<'EOF' | sudo tee /etc/docker/daemon.json
{
  "dns": ["8.8.8.8", "1.1.1.1"]
}
EOF

sudo systemctl restart docker
getent hosts registry.ollama.ai
docker run --rm alpine nslookup registry.ollama.ai
docker compose exec ollama ollama pull llama3
docker exec -it sovereign-advisor-ollama-1 ollama pull llama3
docker ps -a
docker start sovereign-advisor-ollama-1
docker exec -it sovereign-advisor-ollama-1 ollama pull llama3
docker compose down
docker compose up -d --build
docker compose exec ollama ollama pull llama3
docker ps
docker compose up -d --build
cat docker-compose.yml
ls
cat docker-compose.yaml
vi docker-compose.yaml 
cat docker-compose.yaml 
vi Dockerfile.api
vi Dockerfile.ui
ls
cat app.pdf 
ls
vi app.py
rm app.pdf 
ls
vi frontend.py
vi recommend.py
rm frontend.pdf 
rm recommend.pdf 
ls
vi ollama_client.py
vi requirements.txt
ls
docker compose down
docker compose up -d --build
docker ps
docker exec -it sovereign-advisor-api-1 curl http://ollama:11434/api/tags
curl -X POST http://localhost:8000/recommend -H "Content-Type: application/json" -d '{
  "geo":"India",
  "compliance":"High",
  "workload":"Banking",
  "ownership":"Customer Managed",
  "growth":"Startup Scale",
  "data_residency":"Strict"
}'
vi frontend.py 
docker compose down
docker compose up -d --build
git init
nano .gitignore
ls
nano .gitignore
cat .gitignore
git status
git add .
git commit -m "Initial working prototype"
cd ~/sovereign-advisor
git remote -v
git remote add origin https://github.com/Krat0s23/sovereign-advisor.git
git add .
git commit -m "Initial commit"
git branch
git push -u origin master
