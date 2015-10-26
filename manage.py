#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from flask.ext.script import Shell, Server, Manager

from food_ratings import app

app.debug = True
port = os.environ.get('PORT', 8000)

manager = Manager(app)
manager.add_command('server', Server(host="0.0.0.0", port=port))

if __name__ == '__main__':
    manager.run()
