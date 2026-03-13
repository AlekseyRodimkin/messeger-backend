# Переменные
PYTHON=python
ALEMBIC=alembic

# Запуск сервера FastAPI (через uvicorn)
run:
	$(PYTHON) -m uvicorn messeger.app:app --reload

alembic-init:
	alembic init alembic

migrate:
	$(ALEMBIC) revision --autogenerate -m "$(name)"

show:
	alembic current

# Применить все миграции
upgrade:
	$(ALEMBIC) upgrade head

# Первый запуск создаст таблицы, помечает миграцию как примененную (база уже в этом состоянии)
first_migration:
	$(ALEMBIC) stamp head

# Откатить последнюю миграцию
downgrade:
	$(ALEMBIC) downgrade -1