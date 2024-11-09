# LlamaVision

A simple webapp which should show the usecase of data extraction with open source models.

The original creator of this full stack application is tiagolo

We stripped some services and added nextjs as a frontend application
You can run the application `docker compose up -w` everything should work out of the box on linux. On mac it seems that the extraction library `docling` seems not to work.

If you run it the first time you need to download the ollama model inside the docker container. For that you run `docker exec -it ollama ollama run llama3` on your host machine.

`uv` is used as a package manager. 
If you want to add a new package cd into the backend directory and run `uv add <your-library>`



## URLS

Next Frontend: http://localhost:3000

Frontend: http://localhost:5173

Backend: http://localhost:8000

Automatic Interactive Docs (Swagger UI): http://localhost:8000/docs

Automatic Alternative Docs (ReDoc): http://localhost:8000/redoc

Adminer: http://localhost:8080

Traefik UI: http://localhost:8090

MailCatcher: http://localhost:1080
