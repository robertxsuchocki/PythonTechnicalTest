# Origin Markets Backend Test

### Spec:

We would like you to implement an api to: ingest some data representing bonds, query an external api for some additional data, store the result, and make the resulting data queryable via api.
- Fork this hello world repo leveraging Django & Django Rest Framework. (If you wish to use something else like flask that's fine too.)
- Please pick and use a form of authentication, so that each user will only see their own data. ([DRF Auth Options](https://www.django-rest-framework.org/api-guide/authentication/#api-reference))
- We are missing some data! Each bond will have a `lei` field (Legal Entity Identifier). Please use the [GLEIF API](https://www.gleif.org/en/lei-data/gleif-lei-look-up-api/access-the-api) to find the corresponding `Legal Name` of the entity which issued the bond.
- If you are using a database, SQLite is sufficient.
- Please test any additional logic you add.

#### Project Quickstart

Inside a virtual environment running Python 3:
- `pip install -r requirement.txt`
- `./manage.py runserver` to run server.
- `./manage.py test` to run tests.

#### API

We should be able to send a request to:

`POST /bonds/`

to create a "bond" with data that looks like:
~~~
{
    "isin": "FR0000131104",
    "size": 100000000,
    "currency": "EUR",
    "maturity": "2025-02-28",
    "lei": "R0MUWSFPU8MPRO8K5P83"
}
~~~
---
We should be able to send a request to:

`GET /bonds/`

to see something like:
~~~
[
    {
        "isin": "FR0000131104",
        "size": 100000000,
        "currency": "EUR",
        "maturity": "2025-02-28",
        "lei": "R0MUWSFPU8MPRO8K5P83",
        "legal_name": "BNPPARIBAS"
    },
    ...
]
~~~
We would also like to be able to add a filter such as:
`GET /bonds/?legal_name=BNPPARIBAS`

to reduce down the results.

#### Implementation details

API was created with Django & Django Rest Framework as well as [django-filter](https://github.com/carltongibson/django-filter) (for parameter filtering) and [dj-rest-auth](https://github.com/jazzband/dj-rest-auth) (for authentication endpoints)

- Admin user can be created with `python manage.py createsuperuser` and all other users should be created via admin panel
- Token and session authentication are enabled:
  - Session authentication can be used with default REST GUI: head to `/auth/login/`, make a POST request and all following requests will be using this session
  - Token authentication can be used with `curl` as follows:
    ```
    curl --header "Content-Type: application/json" --request POST --data '{"username": "username", "password": "password"}' http://127.0.0.1:8000/auth/login/
    >>> {"key":"40484c9649b9376d34fa04aad31bfbd183f19f24"}
    curl --header "Authorization: Token 40484c9649b9376d34fa04aad31bfbd183f19f24" --request GET http://127.0.0.1:8000/bonds/
    >>> []
    ```
- Tests cover endpoints for API and authentication, as well as validation checks for model, run:
    ```
    python manage.py tests
    ```
