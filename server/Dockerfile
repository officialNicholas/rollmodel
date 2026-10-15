# syntax=docker/dockerfile:1
# The Roll Model game server as one small container. Fly.io runs it (fly.toml); any Docker host can.
FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY package.json package-lock.json ./
# (an optional build secret "npmca": an extra certificate authority for building behind a TLS-inspecting proxy; never in the image)
RUN --mount=type=secret,id=npmca,required=false sh -c '[ -f /run/secrets/npmca ] && export NODE_EXTRA_CA_CERTS=/run/secrets/npmca; npm ci --omit=dev && npm cache clean --force'
COPY src ./src
COPY client ./client
EXPOSE 8080
CMD ["node", "src/index.js"]
