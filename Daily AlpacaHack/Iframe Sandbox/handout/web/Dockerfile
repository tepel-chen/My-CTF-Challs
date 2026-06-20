FROM nginx:1.28.2

RUN rm -f /etc/nginx/conf.d/default.conf
COPY ./default.conf /etc/nginx/conf.d/default.conf

COPY files/ /usr/share/nginx/