# --------------------------------------------------------------
# 1  Choose a lightweight base image that already has Python.
# --------------------------------------------------------------
FROM python:3.11-slim
#   ^^^  "python:3.11‑slim" = official Python 3.11 built on Debian‑Slim.
#        It’s small (≈ 120 MB) but still contains the package manager (apt).

# --------------------------------------------------------------
# 2  Set the working directory inside the container.
# --------------------------------------------------------------
WORKDIR /app
#   All subsequent COPY, RUN, CMD … commands will be executed relative
#   to this directory. It also becomes the default directory when the
#   container starts.

# --------------------------------------------------------------
# 3  Copy only the dependency file(s) first.
# --------------------------------------------------------------
COPY requirements.txt .
#   We copy *just* requirements.txt so Docker can cache the next step.
#   If you change only your application code later, Docker will reuse the
#   already‑installed packages and rebuild much faster.

# --------------------------------------------------------------
# 4  Install Python dependencies.
# --------------------------------------------------------------
RUN pip install --no-cache-dir -r requirements.txt
#   `pip install` pulls the packages listed in requirements.txt.
#   `--no-cache-dir` tells pip not to keep the download cache inside the
#   image, keeping the final image size smaller.

# --------------------------------------------------------------
# 5  Copy the rest of the source code.
# --------------------------------------------------------------
COPY . .
#   Copies everything that lives next to the Dockerfile (your app folder)
#   into /app inside the container. At this point the image already has
#   all its dependencies, so only code changes trigger a new layer.

# --------------------------------------------------------------
# 6  Tell Docker which port the container will listen on.
# --------------------------------------------------------------
EXPOSE 8000
#   This is just documentation for people (and some orchestration tools)
#   that the service expects traffic on TCP 8000. It does NOT publish the
#   port automatically – you still need to map it when you run the
#   container (e.g. `docker run -p 8000:8000 …` or via docker‑compose).

# --------------------------------------------------------------
# 7  Define the command that runs when the container starts.
# --------------------------------------------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
#   `uvicorn` is an ASGI server that runs FastAPI apps.
#   - `app.main:app` means “import `app/main.py` and fetch the variable `app`”.
#   - `--host 0.0.0.0` makes the server listen on all network interfaces
#     inside the container (required for Docker networking).
#   - `--port 8000` matches the EXPOSE line above.
#   Using the JSON array syntax (`["executable","arg1",…]`) avoids the
#   shell‑parsing step and is the recommended way in Dockerfiles.
