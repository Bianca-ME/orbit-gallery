# --------------------------------------------------------------
# 1  -----------  BUILD STAGE ---------------------------------
# --------------------------------------------------------------
#   Use a lightweight Node image that includes npm/yarn.
#   Alpine keeps the image small (~ 70 MB) and is sufficient for
#   compiling a Nuxt 3 app.
FROM node:20-alpine AS builder

# --------------------------------------------------------------
# 2  Set the working directory for the build.
# --------------------------------------------------------------
WORKDIR /app

# --------------------------------------------------------------
# 3  Copy only the package manifest files first.
# --------------------------------------------------------------
#   This enables Docker layer caching: if you only change source
#   code later, npm install won’t run again.
COPY package*.json ./

# --------------------------------------------------------------
# 4  Install JavaScript dependencies.
# --------------------------------------------------------------
#   `npm ci` installs exactly the versions listed in package-lock.json,
#   producing reproducible builds and being faster than `npm install`.
RUN npm ci

# --------------------------------------------------------------
# 5  Copy the remainder of the source tree.
# --------------------------------------------------------------
#   After dependencies are cached, we bring in the rest of the app
#   (pages, components, nuxt.config.ts, etc.).
COPY . .

# --------------------------------------------------------------
# 6  Build the Nuxt application for production.
# --------------------------------------------------------------
#   `npm run build` triggers `nuxt build`, which compiles Vue files,
#   generates the static assets, and places the result in `.output/`.
RUN npm run build

# --------------------------------------------------------------
# 7  -----------  RUNTIME STAGE -------------------------------
# --------------------------------------------------------------
#   Use a minimal web server (nginx) to serve the compiled assets.
#   The runtime stage does **not** contain Node or any dev tools,
#   keeping the final image tiny (~ 30 MB).
FROM nginx:stable-alpine

# --------------------------------------------------------------
# 8  Copy the built static site into nginx’s document root.
# --------------------------------------------------------------
#   Nuxt 3 outputs a ready‑to‑serve directory at
#   `.output/public`.  We copy that into `/usr/share/nginx/html`,
#   which is the default location nginx serves from.
COPY --from=builder /app/.output/public /usr/share/nginx/html

# --------------------------------------------------------------
# 9  Expose the HTTP port.
# --------------------------------------------------------------
EXPOSE 80
#   Standard web‑server port.  When you run the container you can
#   map it to any host port you like (e.g., `-p 3000:80`).

# --------------------------------------------------------------
# 10  No explicit CMD needed – the nginx base image already
#      defines `CMD ["nginx", "-g", "daemon off;"]`.
# --------------------------------------------------------------
