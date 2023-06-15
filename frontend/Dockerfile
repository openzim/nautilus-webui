FROM node:18-alpine as builder

RUN apk --no-cache add yarn
WORKDIR /app
COPY package.json yarn.lock /app/
RUN yarn install
COPY *.html /app/
COPY *.json /app/
COPY *.ts /app/
COPY *.cjs /app/
COPY public /app/public
COPY src /app/src
RUN yarn build

FROM library/nginx:mainline-alpine
LABEL org.opencontainers.image.source https://github.com/openzim/nautilus-webui

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx-default.conf /etc/nginx/conf.d/default.conf

ENV NAUTILUS_WEBUI_API https://localhost:8080/v1
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
