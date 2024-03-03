# Построение системы для обучения
 Реализована система для обучения студентов на курсах.
 
## Архитектура
 - Сущность **продукта (курса)** описывается 
таблицей **Product** с полями:

   + *title* - *Название*
   + *start_date* - *Дата и время начала*
   + *price* - *Цена*
   + *min_group_students_qty* - *Минимальное количество студентов в группе*
   + *max_group_students_qty* - *Максимальное количество студентов в группе*
   + *author* - *Автор* (внешний ключ, ссылается на таблицу *User*)
   + *students* - *Студенты* (связь с таблицей *User* через промежуточную *Enrollment*)
   + *rule* - *Правило распределения по группам*

 - Сущность **пользователя** описывается 
таблицей **User**, в которой есть поля:

   + *username* - *Логин*
   + *status* - *Статус* (преподаватель или студент)

 - Промежуточная таблица **Enrollment** связывает таблицы **User**
и **Product** и описывает поступление студента на курс, в ней определены поля:

   + *product* - *Курс* (внешний ключ)
   + *student* - *Студент* (внешний ключ)
   + *permission* - *Разрешение на доступ к курсу*
   + *is_reserved* - *В запасе ли студент*
   + *date* - *Дата поступления на курс*

- Сущность **урока** описывает таблица **Lesson** с полями:

  + *product* - *Курс* (внешний ключ)
  + *title* - *Название* 
  + *video* - *Ссылка на видео*

- Сущность **группы курса** описывает таблица **Group** с полями:

  + *product* - *Курс* (внешний ключ)
  + *title* - *Название* 
  + *students* - *Студенты* (тип - json array (список id студентов))
  + *is_full* - *Заполнена ли группа*
  + *reserved_group* - *Резервная ли группа*

## Написание запросов и реализация логики распределения
 
Реализованы маршруты:
- `/api/v1/register/` - для добавления (регистрации) пользователя
- `/api/v1/auth/login/` - для авторизации пользователя
- `/api/v1/auth/logout/` - для деавторизации пользователя
- `/api/v1/product/create/` - для создания продукта (права только у преподавателя)
- `/api/v1/product/{pk}/update/` - для обновления информации о продукте (права только у автора продукта)
- `/api/v1/product/` - для просмотра списка продуктов

    формат представления:
  ```
  [
      {
          "title": "Django",
          "start_date": "2024-03-05T18:00:00+03:00",
          "price": "3000.00",
          "lessons": 5,
          "author__username": "root"
      },
      {
          "title": "Высшая математика",
          "start_date": "2024-03-08T00:28:00+03:00",
          "price": "2999.99",
          "lessons": 0,
          "author__username": "root"
      },
      {
          "title": "Группы и теория гомотопий",
          "start_date": "2024-03-02T00:44:00+03:00",
          "price": "5.00",
          "lessons": 10,
          "author__username": "root"
      },
      ...
  ]
- `/api/v1/product/{pk}/` - для отображения информации по конкретному продукту
- `/api/v1/product/{pk}/lessons/` - для отображения уроков в курсе (права у автора или допущенного пользователя)

  формат представления:
  ```
  {
      "lessons": [
          {
              "title": "Введение",
              "video": "http://127.0.0.1:8000/videos/?product_id=2&lesson_id=1"
          },
          {
              "title": "Типы данных",
              "video": "http://127.0.0.1:8000/videos/?product_id=2&lesson_id=2"
          }
      ]
    
  }
  ```

- `/api/v1/product/{pk}/get-access/` - ссылка для получения доступа авторизованного пользователя к конкретному продукту

    При получении доступа пользователь сразу же распределяется в одну из групп курса. 
Если курс уже начался, то группы заполняются до максимума, если же курс ещё не начался,
то группы заново собираются согласно правилу распределения, указанному в описании продукта.
Пусть `n - количество студентов на курсе`, `a - минимальное количество студентов в группе`, 
- `b - максимальное количество студентов в группе`.
Сначала студенты на курсе разбиваются на `n // a` групп по `a` человек.
Если правило распределения установлено по умолчанию, то оставшиеся студенты
распределяются в сформированные группы с заполнением до максимума, 
если же правило распределения другое, 
то студенты последовательно добавляются по одному в каждую группу.
При этом ясно, что если `n // a * (b - a) >= n % a`, то разбиение возможно, а иначе нет.
Именно поэтому пока курс не начался, при любом правиле распределения студенты сначала разбиваются 
на группы по минимуму человек, чтобы никто не оказался вне группы при возможности быть в ней.
Если условие `n // a * (b - a) >= n % a` не выполняется, то формируется резервная группа, 
а в таблице **Enrollment** в поле **is_reserved** записывается информация о том,
что студент в запасе. Также отмечу, что пересобираются группы из студентов в порядке их
поступления на курс. 
После получения доступа к курсу пользователь получает ответ о том, 
в какой группе он состоит, в формате:
  ```
  {
      "user_group": {
          "id": 76,
          "product": 5,
          "students": [
              {
                  "username": "root"
              },
              {
                  "username": "user2"
              },
              {
                  "username": "user3"
              }
          ],
          "title": "group_76",
          "is_full": false,
          "reserved_group": false
      }
  }
  ```

  - `/api/v1/all-products-statistics/` - путь для получения статистики по всем курсам (права только и администратора)

    Ответ в формате (*num_students* - число, допущенных к курсу студентов,
                     *occupancy* - процент заполненности групп на курсе,
                     *acquisition* - процент приобретения продукта):
    ```
    [
        {
            "id": 1,
            "title": "Теоретическая физика: квантовая механика",
            "start_date": "2024-04-01T10:00:00+03:00",
            "num_students": 1,
            "occupancy": 100.0,
            "acquisition": 16.67
        },
        {
            "id": 2,
            "title": "Курс по языку программирования Python",
            "start_date": "2024-03-05T18:00:00+03:00",
            "num_students": 6,
            "occupancy": 75.0,
            "acquisition": 100.0
        },
        {
            "id": 3,
            "title": "Теория игр",
            "start_date": "2024-03-05T18:00:00+03:00",
            "num_students": 2,
            "occupancy": 100.0,
            "acquisition": 33.33
        },
        ...
    ]
    ```