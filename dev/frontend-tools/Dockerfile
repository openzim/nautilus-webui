# not using 20.3 since it has a bug on Macs : https://github.com/nodejs/docker-node/issues/1912
FROM node:20.2.0-slim

WORKDIR /src
COPY . /src
RUN yarn
ENV NODE_ENV=dev
ENV NAUTILUS_WEB_API http://localhost:8080/v1
CMD ["yarn", "dev", "--host", "0.0.0.0", "--port", "80"]
