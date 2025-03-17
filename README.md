# Subway Locator
This is a project of a chatbot that help to get information of a Subway outlets in Kuala Lumpur.

# Requirements
- Python version 3.10.*. To download Python, go to official [website](https://www.python.org/downloads/) or download Conda.
- Docker. For installation, [click here](https://www.docker.com/get-started/).

# Get started
## 1. Git clone
- Git clone this repo:
- 
## 2. Running Ollama Docker Image
- To run Ollama image in CPU. This should also create a new container:
```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```
- Next, download Llama 3.2 model by:
```bash
docker exec -it ollama ollama pull llama3.2:1b
```
- To run Ollama in GPU, follow [this](https://hub.docker.com/r/ollama/ollama)

## 3. Install Python libraries
- To install Python libraries:
```bash
cd backend
pip install -r requirements.txt
```
