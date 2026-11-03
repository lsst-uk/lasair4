# Local Lasair-ZTF development stack. See dev/README.md.
# Run every target from this dev/ folder.

PYTHON_BIN    ?= /opt/homebrew/opt/python@3.11/bin/python3.11
VENV          := .venv
PY            := $(abspath $(VENV))/bin/python
override WEBSERVER := ../webserver
override SETTINGS  := $(WEBSERVER)/lasair/settings.py
# THE DATABASE AND CONTAINER NAMES CANNOT BE OVERRIDDEN, SO DESTRUCTIVE TARGETS ONLY HIT THE DEV STACK
override DEV_DB     := lasair_dev
# --no-defaults: IGNORE ~/.my.cnf AND MYSQL_* VARIABLES THAT COULD POINT THE CLIENT ELSEWHERE
override MYSQL      := mysql --no-defaults --protocol=TCP -h 127.0.0.1 -P 3306 -u lasair_dev_rw -plasair_dev_rw $(DEV_DB)
override CASS_NAME  := lasair-dev-cassandra
override CASS_LABEL := lasair-dev-stack
override CQLSH      := docker exec $(CASS_NAME) cqlsh
CASS_IMAGE    := cassandra:4.1
DJANGO_APPS_WITHOUT_MIGRATIONS := watchlist watchmap filter_query
PORT          ?= 8080
DEV_SETTINGS_MARKER := Django and Lasair settings for the local development stack.
GUARD         := $(PY) -m seed.guard
# manage.py PUTS lasair/ LAST ON sys.path, SO CLEAR PYTHONPATH: NO OTHER settings.py CAN THEN WIN `import settings`
MANAGE        := cd $(WEBSERVER) && env -u PYTHONPATH $(PY) manage.py
# FAILS UNLESS THE CONTAINER CALLED $(CASS_NAME) WAS CREATED BY THIS MAKEFILE
CHECK_CASS    := test "$$(docker inspect -f '{{index .Config.Labels "$(CASS_LABEL)"}}' $(CASS_NAME))" = 1 \
	|| (echo "Container $(CASS_NAME) was not made by dev/Makefile; refusing to use it" && exit 1)

# dev/settings.dev.py ONLY LOADS WHEN THIS IS SET
export LASAIR_DEV_STACK := 1
# manage.py ONLY SETS THIS IF IT IS UNSET, SO PIN IT TO THE DEV SETTINGS
# (MAKE 3.81 IGNORES `override export`, SO OVERRIDE AND EXPORT ARE SEPARATE LINES)
override DJANGO_SETTINGS_MODULE := settings
export DJANGO_SETTINGS_MODULE

SHELL := /bin/bash
.SHELLFLAGS := -eo pipefail -c
.NOTPARALLEL:

.PHONY: all venv settings db migrate cassandra-up cassandra-down cassandra-schema seed run reset smoke test

all: venv settings cassandra-up db migrate seed

venv: .venv/.installed

.venv/.installed: requirements-dev.txt
	test -d $(VENV) || $(PYTHON_BIN) -m venv $(VENV)
	PKG_CONFIG_PATH="$$(brew --prefix mariadb)/lib/pkgconfig" $(VENV)/bin/pip install -q -r requirements-dev.txt
	touch $@

settings:
	mkdir -p var/fits var/streams var/system_status var/media var/query_cache
	test -s var/secret_key || (umask 077; $(PY) -c "import secrets; print(secrets.token_urlsafe(50))" > var/secret_key)
	cp $(WEBSERVER)/staticfiles/build/img/default.jpg var/media/default.jpg
	@# BACK UP AN EXISTING settings.py UNLESS IT IS AN EARLIER COPY OF THE DEV SETTINGS
	@if [ -f $(SETTINGS) ] && ! grep -q "$(DEV_SETTINGS_MARKER)" $(SETTINGS); then \
		backup=$(SETTINGS).bak-$$(date +%Y%m%d%H%M%S); \
		echo "Moving existing settings.py to $$backup"; mv $(SETTINGS) $$backup; chmod 600 $$backup; \
	fi
	cp settings.dev.py $(SETTINGS)

db:
	$(GUARD)
	$(PY) db/make_schema.py | $(MYSQL)

migrate:
	$(GUARD)
	for app in $(DJANGO_APPS_WITHOUT_MIGRATIONS); do \
		mkdir -p var/dev_migrations/$$app && touch var/dev_migrations/$$app/__init__.py; \
	done
	touch var/dev_migrations/__init__.py
	$(MANAGE) makemigrations $(DJANGO_APPS_WITHOUT_MIGRATIONS)
	# THE OLD lasair APP MIGRATIONS CREATE, THEN DROP, THE TABLES THE NEWER APPS OWN, SO RUN THEM FIRST
	$(MANAGE) migrate lasair
	$(MANAGE) migrate

cassandra-up:
	@docker info >/dev/null 2>&1 || colima start --cpu 2 --memory 4
	@if docker container inspect $(CASS_NAME) >/dev/null 2>&1; then $(CHECK_CASS); docker start $(CASS_NAME) >/dev/null; \
	else docker run -d --name $(CASS_NAME) --label $(CASS_LABEL)=1 -p 127.0.0.1:9042:9042 \
		-e MAX_HEAP_SIZE=512M -e HEAP_NEWSIZE=128M -e CASSANDRA_CLUSTER_NAME=lasair-dev \
		-v $(CASS_NAME):/var/lib/cassandra $(CASS_IMAGE) >/dev/null; fi
	@echo "Waiting for Cassandra..."
	@for i in $$(seq 1 60); do $(CQLSH) -e "DESCRIBE KEYSPACES" >/dev/null 2>&1 && break; sleep 5; done
	@$(CQLSH) -e "DESCRIBE KEYSPACES" >/dev/null || (echo "Cassandra did not start" && exit 1)
	$(MAKE) cassandra-schema

cassandra-schema:
	@$(CHECK_CASS)
	docker exec -i $(CASS_NAME) cqlsh < cassandra/schema.cql

cassandra-down:
	@$(CHECK_CASS)
	docker stop $(CASS_NAME)

seed:
	$(GUARD)
	$(PY) -m seed.seed --reset

run:
	$(GUARD)
	$(MANAGE) runserver 127.0.0.1:$(PORT)

# DROPS EVERY TABLE IN THE LOCAL lasair_dev DATABASE AND THE lasair KEYSPACE, THEN REBUILDS THEM
reset:
	$(GUARD)
	@$(CHECK_CASS)
	$(MYSQL) -N -e "SELECT CONCAT('DROP TABLE IF EXISTS \`$(DEV_DB)\`.\`', table_name, '\`;') FROM information_schema.tables WHERE table_schema='$(DEV_DB)'" \
		| (echo "SET FOREIGN_KEY_CHECKS=0;"; cat) | $(MYSQL)
	$(CQLSH) -e "DROP KEYSPACE IF EXISTS lasair"
	rm -rf var/dev_migrations var/fits var/front_page_cache.json
	$(MAKE) settings cassandra-schema db migrate seed

smoke:
	$(GUARD)
	$(PY) smoke.py

test:
	$(PY) -m unittest discover -s tests -t .
