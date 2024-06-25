FROM node:20.13.0

ENV NODE_ENV=dev
ENV NAUTILUS_WEB_API http://localhost:8080/v1

WORKDIR /work
COPY . /work/


RUN yarn \
    && printf "#!/bin/sh\n\
\n\
JS_PATH=/work/public/environ.json\n\
cp -v \"\${JS_PATH}\" \"\${JS_PATH}.orig\"\n\
echo \"dump NAUTILUS_* environ variables to \$JS_PATH\"\n\
\n\
python3 -c 'import os; import json; print(json.dumps({k: v for k, v in os.environ.items() if k.startswith(\"NAUTILUS_\")}, indent=2))' > \$JS_PATH\n\
\n\
cat \$JS_PATH\n\
echo \"-----\"\n\
\n\
exec \"\$@\"\n\
\n\
echo \"restore environ to \$JS_PATH\"\n\
cp -v \"\${JS_PATH}.orig\" \"\${JS_PATH}\"\n\
" > /usr/local/bin/entrypoint \
    && chmod +x /usr/local/bin/entrypoint

ENTRYPOINT ["/usr/local/bin/entrypoint"]
CMD ["yarn", "dev", "--host", "0.0.0.0", "--port", "80"]
