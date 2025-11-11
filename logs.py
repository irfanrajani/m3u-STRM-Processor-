WARN[0000] /Users/irfanrajani/Documents/GitHub/m3u-STRM-Processor-/docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion 
redis-1  | 1:C 11 Nov 2025 19:00:41.517 * oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
redis-1  | 1:C 11 Nov 2025 19:00:41.517 * Redis version=7.4.7, bits=64, commit=00000000, modified=0, pid=1, just started
redis-1  | 1:C 11 Nov 2025 19:00:41.517 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
redis-1  | 1:M 11 Nov 2025 19:00:41.517 * monotonic clock: POSIX clock_gettime
redis-1  | 1:M 11 Nov 2025 19:00:41.519 * Running mode=standalone, port=6379.
redis-1  | 1:M 11 Nov 2025 19:00:41.519 * Server initialized
redis-1  | 1:M 11 Nov 2025 19:00:41.519 * Ready to accept connections tcp
db-1     | 
db-1     | PostgreSQL Database directory appears to contain a database; Skipping initialization
db-1     | 
db-1     | 2025-11-11 19:00:41.557 UTC [1] LOG:  starting PostgreSQL 15.14 on aarch64-unknown-linux-musl, compiled by gcc (Alpine 14.2.0) 14.2.0, 64-bit
db-1     | 2025-11-11 19:00:41.557 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
db-1     | 2025-11-11 19:00:41.557 UTC [1] LOG:  listening on IPv6 address "::", port 5432
db-1     | 2025-11-11 19:00:41.564 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
db-1     | 2025-11-11 19:00:41.572 UTC [29] LOG:  database system was shut down at 2025-11-11 19:00:31 UTC
db-1     | 2025-11-11 19:00:41.577 UTC [1] LOG:  database system is ready to accept connections
backend-1  | 🚀 Starting IPTV Stream Manager...
backend-1  | Running database migrations...
backend-1  | Traceback (most recent call last):
backend-1  |   File "/usr/local/bin/alembic", line 8, in <module>
backend-1  |     sys.exit(main())
backend-1  |              ^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 1033, in main
backend-1  |     CommandLine(prog=prog).main(argv=argv)
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 1023, in main
backend-1  |     self.run_cmd(cfg, options)
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 957, in run_cmd
backend-1  |     fn(
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/command.py", line 483, in upgrade
backend-1  |     script.run_env()
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/script/base.py", line 545, in run_env
backend-1  |     util.load_python_file(self.dir, "env.py")
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/util/pyfiles.py", line 116, in load_python_file
backend-1  |     module = load_module_py(module_id, path)
backend-1  |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/util/pyfiles.py", line 136, in load_module_py
backend-1  |     spec.loader.exec_module(module)  # type: ignore
backend-1  |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
backend-1  |   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
backend-1  |   File "/app/backend/alembic/env.py", line 82, in <module>
backend-1  |     run_migrations_online()
backend-1  |   File "/app/backend/alembic/env.py", line 76, in run_migrations_online
backend-1  |     asyncio.run(run_async_migrations())
backend-1  |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
backend-1  |     return runner.run(main)
backend-1  |            ^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
backend-1  |     return self._loop.run_until_complete(task)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/asyncio/base_events.py", line 654, in run_until_complete
backend-1  |     return future.result()
backend-1  |            ^^^^^^^^^^^^^^^
backend-1  |   File "/app/backend/alembic/env.py", line 62, in run_async_migrations
backend-1  |     connectable = async_engine_from_config(
backend-1  |                   ^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 146, in async_engine_from_config
backend-1  |     return create_async_engine(url, **options)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 121, in create_async_engine
backend-1  |     return AsyncEngine(sync_engine)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 1035, in __init__
backend-1  |     raise exc.InvalidRequestError(
backend-1  | sqlalchemy.exc.InvalidRequestError: The asyncio extension requires an async driver to be used. The loaded 'psycopg2' is not async.
backend-1  | Warning: Alembic upgrade failed. Database may need manual setup.
backend-1  | Database models not loaded yet
backend-1  | Traceback (most recent call last):
backend-1  |   File "/usr/local/bin/uvicorn", line 8, in <module>
backend-1  |     sys.exit(main())
backend-1  |              ^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1462, in __call__
backend-1  |     return self.main(*args, **kwargs)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1383, in main
backend-1  |     rv = self.invoke(ctx)
backend-1  |          ^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1246, in invoke
backend-1  |     return ctx.invoke(self.callback, **ctx.params)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 814, in invoke
backend-1  |     return callback(*args, **kwargs)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/main.py", line 423, in main
backend-1  |     run(
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/main.py", line 593, in run
backend-1  |     server.run()
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 67, in run
backend-1  |     return asyncio_run(self.serve(sockets=sockets), loop_factory=self.config.get_loop_factory())
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/_compat.py", line 30, in asyncio_run
backend-1  |     return runner.run(main)
backend-1  |            ^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
backend-1  |     return self._loop.run_until_complete(task)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 71, in serve
backend-1  |     await self._serve(sockets)
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 78, in _serve
backend-1  |     config.load()
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/config.py", line 439, in load
backend-1  |     self.loaded_app = import_from_string(self.app)
backend-1  |                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
backend-1  |     module = importlib.import_module(module_str)
backend-1  |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
backend-1  |     return _bootstrap._gcd_import(name[level:], package, level)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
backend-1  |   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
backend-1  |   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
backend-1  |   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
backend-1  |   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
backend-1  |   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
backend-1  |   File "/app/backend/app/main.py", line 31, in <module>
backend-1  |     logging.FileHandler(settings.LOG_FILE),
backend-1  |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/logging/__init__.py", line 1181, in __init__
backend-1  |     StreamHandler.__init__(self, self._open())
backend-1  |                                  ^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/logging/__init__.py", line 1213, in _open
backend-1  |     return open_func(self.baseFilename, self.mode,
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  | FileNotFoundError: [Errno 2] No such file or directory: '/app/logs/app.log'
backend-1  | 🚀 Starting IPTV Stream Manager...
backend-1  | Running database migrations...
backend-1  | Traceback (most recent call last):
backend-1  |   File "/usr/local/bin/alembic", line 8, in <module>
backend-1  |     sys.exit(main())
backend-1  |              ^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 1033, in main
backend-1  |     CommandLine(prog=prog).main(argv=argv)
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 1023, in main
backend-1  |     self.run_cmd(cfg, options)
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 957, in run_cmd
backend-1  |     fn(
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/command.py", line 483, in upgrade
backend-1  |     script.run_env()
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/script/base.py", line 545, in run_env
backend-1  |     util.load_python_file(self.dir, "env.py")
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/util/pyfiles.py", line 116, in load_python_file
backend-1  |     module = load_module_py(module_id, path)
backend-1  |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/util/pyfiles.py", line 136, in load_module_py
backend-1  |     spec.loader.exec_module(module)  # type: ignore
backend-1  |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
backend-1  |   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
backend-1  |   File "/app/backend/alembic/env.py", line 82, in <module>
backend-1  |     run_migrations_online()
backend-1  |   File "/app/backend/alembic/env.py", line 76, in run_migrations_online
backend-1  |     asyncio.run(run_async_migrations())
backend-1  |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
backend-1  |     return runner.run(main)
backend-1  |            ^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
backend-1  |     return self._loop.run_until_complete(task)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/asyncio/base_events.py", line 654, in run_until_complete
backend-1  |     return future.result()
backend-1  |            ^^^^^^^^^^^^^^^
backend-1  |   File "/app/backend/alembic/env.py", line 62, in run_async_migrations
backend-1  |     connectable = async_engine_from_config(
backend-1  |                   ^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 146, in async_engine_from_config
backend-1  |     return create_async_engine(url, **options)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 121, in create_async_engine
backend-1  |     return AsyncEngine(sync_engine)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 1035, in __init__
backend-1  |     raise exc.InvalidRequestError(
backend-1  | sqlalchemy.exc.InvalidRequestError: The asyncio extension requires an async driver to be used. The loaded 'psycopg2' is not async.
backend-1  | Warning: Alembic upgrade failed. Database may need manual setup.
backend-1  | Database models not loaded yet
backend-1  | Traceback (most recent call last):
backend-1  |   File "/usr/local/bin/uvicorn", line 8, in <module>
backend-1  |     sys.exit(main())
backend-1  |              ^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1462, in __call__
backend-1  |     return self.main(*args, **kwargs)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1383, in main
backend-1  |     rv = self.invoke(ctx)
backend-1  |          ^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1246, in invoke
backend-1  |     return ctx.invoke(self.callback, **ctx.params)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 814, in invoke
backend-1  |     return callback(*args, **kwargs)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/main.py", line 423, in main
backend-1  |     run(
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/main.py", line 593, in run
backend-1  |     server.run()
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 67, in run
backend-1  |     return asyncio_run(self.serve(sockets=sockets), loop_factory=self.config.get_loop_factory())
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/_compat.py", line 30, in asyncio_run
backend-1  |     return runner.run(main)
backend-1  |            ^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
backend-1  |     return self._loop.run_until_complete(task)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 71, in serve
backend-1  |     await self._serve(sockets)
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 78, in _serve
backend-1  |     config.load()
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/config.py", line 439, in load
backend-1  |     self.loaded_app = import_from_string(self.app)
backend-1  |                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
backend-1  |     module = importlib.import_module(module_str)
backend-1  |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
backend-1  |     return _bootstrap._gcd_import(name[level:], package, level)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
backend-1  |   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
backend-1  |   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
backend-1  |   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
backend-1  |   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
backend-1  |   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
backend-1  |   File "/app/backend/app/main.py", line 31, in <module>
backend-1  |     logging.FileHandler(settings.LOG_FILE),
backend-1  |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/logging/__init__.py", line 1181, in __init__
backend-1  |     StreamHandler.__init__(self, self._open())
backend-1  |                                  ^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/logging/__init__.py", line 1213, in _open
backend-1  |     return open_func(self.baseFilename, self.mode,
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  | FileNotFoundError: [Errno 2] No such file or directory: '/app/logs/app.log'
backend-1  | 🚀 Starting IPTV Stream Manager...
backend-1  | Running database migrations...
backend-1  | Traceback (most recent call last):
backend-1  |   File "/usr/local/bin/alembic", line 8, in <module>
backend-1  |     sys.exit(main())
backend-1  |              ^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 1033, in main
backend-1  |     CommandLine(prog=prog).main(argv=argv)
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 1023, in main
backend-1  |     self.run_cmd(cfg, options)
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 957, in run_cmd
backend-1  |     fn(
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/command.py", line 483, in upgrade
backend-1  |     script.run_env()
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/script/base.py", line 545, in run_env
backend-1  |     util.load_python_file(self.dir, "env.py")
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/util/pyfiles.py", line 116, in load_python_file
backend-1  |     module = load_module_py(module_id, path)
backend-1  |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/util/pyfiles.py", line 136, in load_module_py
backend-1  |     spec.loader.exec_module(module)  # type: ignore
backend-1  |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
backend-1  |   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
backend-1  |   File "/app/backend/alembic/env.py", line 82, in <module>
backend-1  |     run_migrations_online()
backend-1  |   File "/app/backend/alembic/env.py", line 76, in run_migrations_online
backend-1  |     asyncio.run(run_async_migrations())
backend-1  |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
backend-1  |     return runner.run(main)
backend-1  |            ^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
backend-1  |     return self._loop.run_until_complete(task)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/asyncio/base_events.py", line 654, in run_until_complete
backend-1  |     return future.result()
backend-1  |            ^^^^^^^^^^^^^^^
backend-1  |   File "/app/backend/alembic/env.py", line 62, in run_async_migrations
backend-1  |     connectable = async_engine_from_config(
backend-1  |                   ^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 146, in async_engine_from_config
backend-1  |     return create_async_engine(url, **options)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 121, in create_async_engine
backend-1  |     return AsyncEngine(sync_engine)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 1035, in __init__
backend-1  |     raise exc.InvalidRequestError(
backend-1  | sqlalchemy.exc.InvalidRequestError: The asyncio extension requires an async driver to be used. The loaded 'psycopg2' is not async.
backend-1  | Warning: Alembic upgrade failed. Database may need manual setup.
backend-1  | Database models not loaded yet
backend-1  | Traceback (most recent call last):
backend-1  |   File "/usr/local/bin/uvicorn", line 8, in <module>
backend-1  |     sys.exit(main())
backend-1  |              ^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1462, in __call__
backend-1  |     return self.main(*args, **kwargs)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1383, in main
backend-1  |     rv = self.invoke(ctx)
backend-1  |          ^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1246, in invoke
backend-1  |     return ctx.invoke(self.callback, **ctx.params)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 814, in invoke
backend-1  |     return callback(*args, **kwargs)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/main.py", line 423, in main
backend-1  |     run(
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/main.py", line 593, in run
backend-1  |     server.run()
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 67, in run
backend-1  |     return asyncio_run(self.serve(sockets=sockets), loop_factory=self.config.get_loop_factory())
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/_compat.py", line 30, in asyncio_run
backend-1  |     return runner.run(main)
backend-1  |            ^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
backend-1  |     return self._loop.run_until_complete(task)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 71, in serve
backend-1  |     await self._serve(sockets)
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 78, in _serve
backend-1  |     config.load()
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/config.py", line 439, in load
backend-1  |     self.loaded_app = import_from_string(self.app)
backend-1  |                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
backend-1  |     module = importlib.import_module(module_str)
backend-1  |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
backend-1  |     return _bootstrap._gcd_import(name[level:], package, level)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
backend-1  |   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
backend-1  |   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
backend-1  |   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
backend-1  |   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
backend-1  |   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
backend-1  |   File "/app/backend/app/main.py", line 31, in <module>
backend-1  |     logging.FileHandler(settings.LOG_FILE),
backend-1  |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/logging/__init__.py", line 1181, in __init__
backend-1  |     StreamHandler.__init__(self, self._open())
backend-1  |                                  ^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/logging/__init__.py", line 1213, in _open
backend-1  |     return open_func(self.baseFilename, self.mode,
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  | FileNotFoundError: [Errno 2] No such file or directory: '/app/logs/app.log'
backend-1  | 🚀 Starting IPTV Stream Manager...
backend-1  | Running database migrations...
backend-1  | Traceback (most recent call last):
backend-1  |   File "/usr/local/bin/alembic", line 8, in <module>
backend-1  |     sys.exit(main())
backend-1  |              ^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 1033, in main
backend-1  |     CommandLine(prog=prog).main(argv=argv)
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 1023, in main
backend-1  |     self.run_cmd(cfg, options)
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 957, in run_cmd
backend-1  |     fn(
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/command.py", line 483, in upgrade
backend-1  |     script.run_env()
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/script/base.py", line 545, in run_env
backend-1  |     util.load_python_file(self.dir, "env.py")
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/util/pyfiles.py", line 116, in load_python_file
backend-1  |     module = load_module_py(module_id, path)
backend-1  |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/util/pyfiles.py", line 136, in load_module_py
backend-1  |     spec.loader.exec_module(module)  # type: ignore
backend-1  |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
backend-1  |   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
backend-1  |   File "/app/backend/alembic/env.py", line 82, in <module>
backend-1  |     run_migrations_online()
backend-1  |   File "/app/backend/alembic/env.py", line 76, in run_migrations_online
backend-1  |     asyncio.run(run_async_migrations())
backend-1  |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
backend-1  |     return runner.run(main)
backend-1  |            ^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
backend-1  |     return self._loop.run_until_complete(task)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/asyncio/base_events.py", line 654, in run_until_complete
backend-1  |     return future.result()
backend-1  |            ^^^^^^^^^^^^^^^
backend-1  |   File "/app/backend/alembic/env.py", line 62, in run_async_migrations
backend-1  |     connectable = async_engine_from_config(
backend-1  |                   ^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 146, in async_engine_from_config
backend-1  |     return create_async_engine(url, **options)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 121, in create_async_engine
backend-1  |     return AsyncEngine(sync_engine)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 1035, in __init__
backend-1  |     raise exc.InvalidRequestError(
backend-1  | sqlalchemy.exc.InvalidRequestError: The asyncio extension requires an async driver to be used. The loaded 'psycopg2' is not async.
backend-1  | Warning: Alembic upgrade failed. Database may need manual setup.
backend-1  | Database models not loaded yet
backend-1  | Traceback (most recent call last):
backend-1  |   File "/usr/local/bin/uvicorn", line 8, in <module>
backend-1  |     sys.exit(main())
backend-1  |              ^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1462, in __call__
backend-1  |     return self.main(*args, **kwargs)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1383, in main
backend-1  |     rv = self.invoke(ctx)
backend-1  |          ^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1246, in invoke
backend-1  |     return ctx.invoke(self.callback, **ctx.params)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 814, in invoke
backend-1  |     return callback(*args, **kwargs)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/main.py", line 423, in main
backend-1  |     run(
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/main.py", line 593, in run
backend-1  |     server.run()
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 67, in run
backend-1  |     return asyncio_run(self.serve(sockets=sockets), loop_factory=self.config.get_loop_factory())
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/_compat.py", line 30, in asyncio_run
backend-1  |     return runner.run(main)
backend-1  |            ^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
backend-1  |     return self._loop.run_until_complete(task)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 71, in serve
backend-1  |     await self._serve(sockets)
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 78, in _serve
backend-1  |     config.load()
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/config.py", line 439, in load
backend-1  |     self.loaded_app = import_from_string(self.app)
backend-1  |                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
backend-1  |     module = importlib.import_module(module_str)
backend-1  |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
backend-1  |     return _bootstrap._gcd_import(name[level:], package, level)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
backend-1  |   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
backend-1  |   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
backend-1  |   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
backend-1  |   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
backend-1  |   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
backend-1  |   File "/app/backend/app/main.py", line 31, in <module>
backend-1  |     logging.FileHandler(settings.LOG_FILE),
backend-1  |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/logging/__init__.py", line 1181, in __init__
backend-1  |     StreamHandler.__init__(self, self._open())
backend-1  |                                  ^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/logging/__init__.py", line 1213, in _open
backend-1  |     return open_func(self.baseFilename, self.mode,
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  | FileNotFoundError: [Errno 2] No such file or directory: '/app/logs/app.log'
backend-1  | 🚀 Starting IPTV Stream Manager...
backend-1  | Running database migrations...
backend-1  | Traceback (most recent call last):
backend-1  |   File "/usr/local/bin/alembic", line 8, in <module>
backend-1  |     sys.exit(main())
backend-1  |              ^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 1033, in main
backend-1  |     CommandLine(prog=prog).main(argv=argv)
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 1023, in main
backend-1  |     self.run_cmd(cfg, options)
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 957, in run_cmd
backend-1  |     fn(
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/command.py", line 483, in upgrade
backend-1  |     script.run_env()
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/script/base.py", line 545, in run_env
backend-1  |     util.load_python_file(self.dir, "env.py")
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/util/pyfiles.py", line 116, in load_python_file
backend-1  |     module = load_module_py(module_id, path)
backend-1  |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/util/pyfiles.py", line 136, in load_module_py
backend-1  |     spec.loader.exec_module(module)  # type: ignore
backend-1  |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
backend-1  |   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
backend-1  |   File "/app/backend/alembic/env.py", line 82, in <module>
backend-1  |     run_migrations_online()
backend-1  |   File "/app/backend/alembic/env.py", line 76, in run_migrations_online
backend-1  |     asyncio.run(run_async_migrations())
backend-1  |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
backend-1  |     return runner.run(main)
backend-1  |            ^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
backend-1  |     return self._loop.run_until_complete(task)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/asyncio/base_events.py", line 654, in run_until_complete
backend-1  |     return future.result()
backend-1  |            ^^^^^^^^^^^^^^^
backend-1  |   File "/app/backend/alembic/env.py", line 62, in run_async_migrations
backend-1  |     connectable = async_engine_from_config(
backend-1  |                   ^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 146, in async_engine_from_config
backend-1  |     return create_async_engine(url, **options)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 121, in create_async_engine
backend-1  |     return AsyncEngine(sync_engine)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 1035, in __init__
backend-1  |     raise exc.InvalidRequestError(
backend-1  | sqlalchemy.exc.InvalidRequestError: The asyncio extension requires an async driver to be used. The loaded 'psycopg2' is not async.
backend-1  | Warning: Alembic upgrade failed. Database may need manual setup.
backend-1  | Database models not loaded yet
backend-1  | Traceback (most recent call last):
backend-1  |   File "/usr/local/bin/uvicorn", line 8, in <module>
backend-1  |     sys.exit(main())
backend-1  |              ^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1462, in __call__
backend-1  |     return self.main(*args, **kwargs)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1383, in main
backend-1  |     rv = self.invoke(ctx)
backend-1  |          ^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1246, in invoke
backend-1  |     return ctx.invoke(self.callback, **ctx.params)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 814, in invoke
backend-1  |     return callback(*args, **kwargs)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/main.py", line 423, in main
backend-1  |     run(
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/main.py", line 593, in run
backend-1  |     server.run()
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 67, in run
backend-1  |     return asyncio_run(self.serve(sockets=sockets), loop_factory=self.config.get_loop_factory())
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/_compat.py", line 30, in asyncio_run
backend-1  |     return runner.run(main)
backend-1  |            ^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
backend-1  |     return self._loop.run_until_complete(task)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 71, in serve
backend-1  |     await self._serve(sockets)
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 78, in _serve
backend-1  |     config.load()
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/config.py", line 439, in load
backend-1  |     self.loaded_app = import_from_string(self.app)
backend-1  |                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
backend-1  |     module = importlib.import_module(module_str)
backend-1  |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
backend-1  |     return _bootstrap._gcd_import(name[level:], package, level)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
backend-1  |   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
backend-1  |   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
backend-1  |   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
backend-1  |   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
backend-1  |   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
backend-1  |   File "/app/backend/app/main.py", line 31, in <module>
backend-1  |     logging.FileHandler(settings.LOG_FILE),
backend-1  |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/logging/__init__.py", line 1181, in __init__
backend-1  |     StreamHandler.__init__(self, self._open())
backend-1  |                                  ^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/logging/__init__.py", line 1213, in _open
backend-1  |     return open_func(self.baseFilename, self.mode,
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  | FileNotFoundError: [Errno 2] No such file or directory: '/app/logs/app.log'
backend-1  | 🚀 Starting IPTV Stream Manager...
backend-1  | Running database migrations...
backend-1  | Traceback (most recent call last):
backend-1  |   File "/usr/local/bin/alembic", line 8, in <module>
backend-1  |     sys.exit(main())
backend-1  |              ^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 1033, in main
backend-1  |     CommandLine(prog=prog).main(argv=argv)
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 1023, in main
backend-1  |     self.run_cmd(cfg, options)
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 957, in run_cmd
backend-1  |     fn(
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/command.py", line 483, in upgrade
backend-1  |     script.run_env()
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/script/base.py", line 545, in run_env
backend-1  |     util.load_python_file(self.dir, "env.py")
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/util/pyfiles.py", line 116, in load_python_file
backend-1  |     module = load_module_py(module_id, path)
backend-1  |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/util/pyfiles.py", line 136, in load_module_py
backend-1  |     spec.loader.exec_module(module)  # type: ignore
backend-1  |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
backend-1  |   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
backend-1  |   File "/app/backend/alembic/env.py", line 82, in <module>
backend-1  |     run_migrations_online()
backend-1  |   File "/app/backend/alembic/env.py", line 76, in run_migrations_online
backend-1  |     asyncio.run(run_async_migrations())
backend-1  |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
backend-1  |     return runner.run(main)
backend-1  |            ^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
backend-1  |     return self._loop.run_until_complete(task)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/asyncio/base_events.py", line 654, in run_until_complete
backend-1  |     return future.result()
backend-1  |            ^^^^^^^^^^^^^^^
backend-1  |   File "/app/backend/alembic/env.py", line 62, in run_async_migrations
backend-1  |     connectable = async_engine_from_config(
backend-1  |                   ^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 146, in async_engine_from_config
backend-1  |     return create_async_engine(url, **options)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 121, in create_async_engine
backend-1  |     return AsyncEngine(sync_engine)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 1035, in __init__
backend-1  |     raise exc.InvalidRequestError(
backend-1  | sqlalchemy.exc.InvalidRequestError: The asyncio extension requires an async driver to be used. The loaded 'psycopg2' is not async.
backend-1  | Warning: Alembic upgrade failed. Database may need manual setup.
backend-1  | Database models not loaded yet
backend-1  | Traceback (most recent call last):
backend-1  |   File "/usr/local/bin/uvicorn", line 8, in <module>
backend-1  |     sys.exit(main())
backend-1  |              ^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1462, in __call__
backend-1  |     return self.main(*args, **kwargs)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1383, in main
backend-1  |     rv = self.invoke(ctx)
backend-1  |          ^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1246, in invoke
backend-1  |     return ctx.invoke(self.callback, **ctx.params)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 814, in invoke
backend-1  |     return callback(*args, **kwargs)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/main.py", line 423, in main
backend-1  |     run(
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/main.py", line 593, in run
backend-1  |     server.run()
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 67, in run
backend-1  |     return asyncio_run(self.serve(sockets=sockets), loop_factory=self.config.get_loop_factory())
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/_compat.py", line 30, in asyncio_run
backend-1  |     return runner.run(main)
backend-1  |            ^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
backend-1  |     return self._loop.run_until_complete(task)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 71, in serve
backend-1  |     await self._serve(sockets)
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 78, in _serve
backend-1  |     config.load()
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/config.py", line 439, in load
backend-1  |     self.loaded_app = import_from_string(self.app)
backend-1  |                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
backend-1  |     module = importlib.import_module(module_str)
backend-1  |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
backend-1  |     return _bootstrap._gcd_import(name[level:], package, level)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
backend-1  |   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
backend-1  |   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
backend-1  |   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
backend-1  |   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
backend-1  |   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
backend-1  |   File "/app/backend/app/main.py", line 31, in <module>
backend-1  |     logging.FileHandler(settings.LOG_FILE),
backend-1  |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/logging/__init__.py", line 1181, in __init__
backend-1  |     StreamHandler.__init__(self, self._open())
backend-1  |                                  ^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/logging/__init__.py", line 1213, in _open
backend-1  |     return open_func(self.baseFilename, self.mode,
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  | FileNotFoundError: [Errno 2] No such file or directory: '/app/logs/app.log'
backend-1  | 🚀 Starting IPTV Stream Manager...
backend-1  | Running database migrations...
backend-1  | Traceback (most recent call last):
backend-1  |   File "/usr/local/bin/alembic", line 8, in <module>
backend-1  |     sys.exit(main())
backend-1  |              ^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 1033, in main
backend-1  |     CommandLine(prog=prog).main(argv=argv)
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 1023, in main
backend-1  |     self.run_cmd(cfg, options)
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 957, in run_cmd
backend-1  |     fn(
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/command.py", line 483, in upgrade
backend-1  |     script.run_env()
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/script/base.py", line 545, in run_env
backend-1  |     util.load_python_file(self.dir, "env.py")
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/util/pyfiles.py", line 116, in load_python_file
backend-1  |     module = load_module_py(module_id, path)
backend-1  |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/alembic/util/pyfiles.py", line 136, in load_module_py
backend-1  |     spec.loader.exec_module(module)  # type: ignore
backend-1  |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
backend-1  |   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
backend-1  |   File "/app/backend/alembic/env.py", line 82, in <module>
backend-1  |     run_migrations_online()
backend-1  |   File "/app/backend/alembic/env.py", line 76, in run_migrations_online
backend-1  |     asyncio.run(run_async_migrations())
backend-1  |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
backend-1  |     return runner.run(main)
backend-1  |            ^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
backend-1  |     return self._loop.run_until_complete(task)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/asyncio/base_events.py", line 654, in run_until_complete
backend-1  |     return future.result()
backend-1  |            ^^^^^^^^^^^^^^^
backend-1  |   File "/app/backend/alembic/env.py", line 62, in run_async_migrations
backend-1  |     connectable = async_engine_from_config(
backend-1  |                   ^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 146, in async_engine_from_config
backend-1  |     return create_async_engine(url, **options)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 121, in create_async_engine
backend-1  |     return AsyncEngine(sync_engine)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 1035, in __init__
backend-1  |     raise exc.InvalidRequestError(
backend-1  | sqlalchemy.exc.InvalidRequestError: The asyncio extension requires an async driver to be used. The loaded 'psycopg2' is not async.
backend-1  | Warning: Alembic upgrade failed. Database may need manual setup.
backend-1  | Database models not loaded yet
backend-1  | Traceback (most recent call last):
backend-1  |   File "/usr/local/bin/uvicorn", line 8, in <module>
backend-1  |     sys.exit(main())
backend-1  |              ^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1462, in __call__
backend-1  |     return self.main(*args, **kwargs)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1383, in main
backend-1  |     rv = self.invoke(ctx)
backend-1  |          ^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1246, in invoke
backend-1  |     return ctx.invoke(self.callback, **ctx.params)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 814, in invoke
backend-1  |     return callback(*args, **kwargs)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/main.py", line 423, in main
backend-1  |     run(
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/main.py", line 593, in run
backend-1  |     server.run()
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 67, in run
backend-1  |     return asyncio_run(self.serve(sockets=sockets), loop_factory=self.config.get_loop_factory())
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/_compat.py", line 30, in asyncio_run
backend-1  |     return runner.run(main)
backend-1  |            ^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
backend-1  |     return self._loop.run_until_complete(task)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 71, in serve
backend-1  |     await self._serve(sockets)
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 78, in _serve
backend-1  |     config.load()
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/config.py", line 439, in load
backend-1  |     self.loaded_app = import_from_string(self.app)
backend-1  |                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
backend-1  |     module = importlib.import_module(module_str)
backend-1  |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
backend-1  |     return _bootstrap._gcd_import(name[level:], package, level)
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
backend-1  |   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
backend-1  |   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
backend-1  |   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
backend-1  |   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
backend-1  |   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
backend-1  |   File "/app/backend/app/main.py", line 31, in <module>
backend-1  |     logging.FileHandler(settings.LOG_FILE),
backend-1  |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/logging/__init__.py", line 1181, in __init__
backend-1  |     StreamHandler.__init__(self, self._open())
backend-1  |                                  ^^^^^^^^^^^^
backend-1  |   File "/usr/local/lib/python3.11/logging/__init__.py", line 1213, in _open
backend-1  |     return open_func(self.baseFilename, self.mode,
backend-1  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
backend-1  | FileNotFoundError: [Errno 2] No such file or directory: '/app/logs/app.log'
