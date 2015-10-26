===============================
food_ratings_demo
===============================


Quickstart
----------

Then run the following commands to bootstrap your environment.

```
mkvirtualenv --python=/path/to/required/python/version [appname]
```

Install python requirements.
```
pip install -r requirements/dev.txt
```

Set some environment variables are already set in environment.sh e.g.

```
export SETTINGS='config.DevelopmentConfig'
```

If you need more add to the environment.sh file.

Once that this all done you can:

```
./run.sh
```

Deployment
----------

In your production environment, make sure the ``SETTINGS`` environment variable is set to ``config.Config``.


Shell
-----

To open the interactive shell, run ::

```
python manage.py shell
```
