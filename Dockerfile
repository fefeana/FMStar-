FROM nginx:alpine

# Copy static web assets
COPY index.html /usr/share/nginx/html/index.html
COPY FMStar-Studio /usr/share/nginx/html/FMStar-Studio
COPY public /usr/share/nginx/html/public

# Configure NGINX to listen on port 8080 (Google Cloud Run standard)
RUN sed -i 's/listen       80;/listen       8080;/g' /etc/nginx/conf.d/default.conf

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
