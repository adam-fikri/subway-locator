# Subway Locator
This is a project of a chatbot that help to get information of a Subway outlets in Kuala Lumpur.

# Requirements
- Python version 3.10.*. To download Python, go to official [website](https://www.python.org/downloads/) or download Conda.
- Docker. For installation, [click here](https://www.docker.com/get-started/).

# Get started
## 1. Git clone
- Git clone this repo:
```bash
git clone https://github.com/adam-fikri/subway-locator.git
```
  
## 2. Running Ollama Docker Image
- To run Ollama image in CPU. This should also create a new container:
```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```
- To run Ollama in GPU, follow [this](https://hub.docker.com/r/ollama/ollama)
- Next, download Llama 3.2 model by:
```bash
docker exec -it ollama ollama pull llama3.2:1b
```

## 3. Install Python libraries
- To install Python libraries:
```bash
cd backend
pip install -r requirements.txt
```

## 4. Run the program
### a. Run Ollama Docker container 
- Make sure the Docker container that just created is running:
```bash
docker ps -a
```
- To run Docker container:
```bash
docker run <container_id or container_name>
```

### b. Run API
- First, make sure subway_store.db is available in backend folder else:
```bash
cd backend
python createDB.py
```
- Before scraping, make sure to get Google geocoding API by following steps in https://developers.google.com/maps/documentation/geocoding/cloud-setup#console.
- Next,  scrape from https://www.subway.com.my/find-a-subway by:
```bash
python scrape.py
```
- Finally, run the API
```bash
uvicorn main:app --reload
```
### c. Run the web app
- Open another terminal and run:
```bash
cd ui
python app.py
```

# All done 🎉
