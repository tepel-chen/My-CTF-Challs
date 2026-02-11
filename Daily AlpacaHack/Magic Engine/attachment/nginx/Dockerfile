FROM nginx:stable

RUN rm -f /etc/nginx/conf.d/default.conf
COPY ./default.conf /etc/nginx/conf.d/default.conf

COPY html/ /usr/share/nginx/html/