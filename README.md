![Workflow Status](https://github.com/RH1532/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)  
[Посмотреть проект на IP-адресе](http://84.252.131.20)  

# Foodrgam  

 «Продуктовый помощник»: сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 

## Развертывание проекта
1. Скопировать проект на сервер
2. Скопировать файлы docker-compose и nginx
 scp docker-compose.yml danila@84.252.131.20:/home/danila/docker-compose.yml  
 scp nginx.conf danila@84.252.131.20:/home/danila/nginx.conf  
3. Выполните команды:
 `docker-compose up -d --build`  
 `/docker-compose exec backend python manage.py makemigrations`  
 `docker-compose exec backend python manage.py migrate`  
 `docker-compose exec backend python manage.py collectstatic --no-input`  
 `docker-compose exec backend python manage.py createsuperuser`  
