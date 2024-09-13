FROM node:18-alpine as builder

RUN apk --no-cache add yarn
COPY . /src/
WORKDIR /src
RUN yarn install --frozen-lockfile && yarn build

FROM library/nginx:mainline-alpine
RUN apk --no-cache add python3
LABEL org.opencontainers.image.source https://github.com/openzim/nautilus-webui

COPY --from=builder /src/dist /user/share/nginx/html
COPY nginx-default.conf /etc/nginx/conf.d/default.conf
COPY entrypoint.sh /app/
RUN ls /app

ENV NAUTILUS_WEB_API http://localhost:8080/v1
ENV NAUTILUS_IS_SINGLE_USER ""
EXPOSE 80

ENTRYPOINT [ "/app/entrypoint.sh" ]
CMD ["nginx", "-g", "daemon off;"]
