# Web-based Platform for Automated Web User Interfaces Evaluation

***

## Description
This project aims to facilitate an easier use of WUI metrics and assessment models for automated UI evaluation through a single, unifying web-based platform.

## Installation
* Backend: conda (env. x86-64, version 24.1.2) is used as the virtual environment. You can install the dependencies with conda with this command:
`conda env create -f environment.yaml`
  * If you don't have conda installed in your device, please refer to this documentation: https://conda.io/projects/conda/en/latest/user-guide/install/index.html


* Frontend: pnpm is used as the package manager. After navigating to the frontend directory, install the dependency modules with this command:
`pnpm install`. 
  * If you don't have pnpm installed in your device, please refer to this link: https://pnpm.io/installation


* Other dependencies: 
1. **Tesseract**, required for image segmentation.
  * On linux, for example: 

    `sudo apt install tesseract-ocr`
    `sudo apt install libtesseract-dev`

2. **Chrome executable**, for running selenium to capture screenshots.


3. To be added as I notice them. Let me know if you find more!

* Proxy server (for load balancing, connection limit, rate limit): NGINX is used. Please refer to this documentation for its installation: https://docs.nginx.com/nginx/admin-guide/installing-nginx/installing-nginx-open-source/.
  * A sample `nginx.conf` for load balancing with least connections with 2 servers running can be found inside the nginx directory. For security reasons, the actually used nginx.conf is not provided in this repository.
  * Read on this guide on how to set up and run nginx: https://nginx.org/en/docs/beginners_guide.html#control

## Usage
* Preliminary preparation: 
  * Supabase is used as the database and file storage provider. Inside the root of the backend package, You should create an .env file containing your `SUPABASE_URL` and `SUPABASE_KEY`. Alternatively, you could use the default database by copying the environment values provided in `.env.example`.
  * You can find more information about Supabase in this link: https://supabase.com/docs

* Backend:
  * Activate your virtual environment as specified in previous <b>Installation</b> section.
  * Run this following command in your terminal: `uvicorn server:app --host 0.0.0.0 --port <port number> --reload`
  * The backend server is now running!
  * Alternatively, you can containerize the backend with the provided Dockerfile, and then run the backend with the command `docker-compose up`. Pre-requisite: you need to have Docker & docker-compose installed in your machine.
  * If you run it with docker-compose, 4 instances of the backend will be created, they are listening to port 8000, 8001, 8002, and 8003. Feel free to configure it yourself!

* Frontend:
  * In the root frontend directory, create an .env file, following the example given in its corresponding `.env.example`. The env value of `VITE_PREFIX_URL` depends on where the server is currently running.
  * For instance, if the server is run locally and on port 8000, the value of `VITE_PREFIX_URL` should be `http://localhost:8000/`.
  * To run the frontend in dev mode, use this following command: `pnpm run dev` while you are in the frontend directory
  * Alternatively, you can first build the frontend: `pnpm run build` and then run `pnpm run preview`.

## Support
You can write to `liusnandoc@gmail.com` for any questions pertaining to this project.

## Authors and acknowledgment
This work was carried out by Calvin Liusnando under the supervision of Dr.-Ing. Sebastian Heil as part of his Master's thesis in Web Engineering at TU Chemnitz. The research was published at the 25th International Conference on Web Engineering (ICWE 2025):

```
 Heil, S., Liusnando, C., & Gaedke, M. (2025). UIQLab: Automatic Web User Interface Assessment. 25th ICWE2025, Delft, Netherlands.
```

The official replication package for the published paper can be found [here](https://zenodo.org/records/15920095). 

Please note that any updates to this repository made after August 11th, 2025 are solely the work of Calvin Liusnando.

