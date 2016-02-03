===============================
food_ratings_demo
===============================


Quickstart
----------

Install Python3 e.g.

```
brew install python3
```

Install virtualenv e.g.
```
pip3 install virtualenv
```

Create the virtualenv using python3 in directory venv
```
virtualenv --python python3 venv
```

Activate virtualenv and install python requirements
```
source venv/bin/activate
pip install -r requirements/dev.txt
```

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
