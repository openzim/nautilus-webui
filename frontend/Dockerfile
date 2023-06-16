FROM node:18-alpine as builder

RUN apk --no-cache add yarn
COPY . /src/
WORKDIR /src
RUN yarn install --frozen-lockfile && yarn build
RUN ls /src/dist

FROM library/nginx:mainline-alpine
LABEL org.opencontainers.image.source https://github.com/openzim/nautilus-webui

COPY --from=builder /src/dist /user/share/nginx/html
RUN ls /user/share/nginx/html
COPY nginx-default.conf /etc/nginx/conf.d/default.conf

ENV NAUTILUS_WEBUI_API https://localhost:8080/v1
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
