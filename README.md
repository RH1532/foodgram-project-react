![Workflow Status](https://github.com/RH1532/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)  
[Посмотреть проект на IP-адресе](http://84.252.131.20)  

Foodrgam  

docker-compose up -d --build  
docker-compose exec backend python manage.py makemigrations  
docker-compose exec backend python manage.py migrate  
docker-compose exec backend python manage.py collectstatic --no-input  
docker-compose exec backend python manage.py createsuperuser  
scp docker-compose.yml danila@84.252.131.20:/home/danila/docker-compose.yml  
scp nginx.conf danila@84.252.131.20:/home/danila/nginx.conf  