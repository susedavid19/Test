#!/bin/bash

cd /data
gunicorn config.wsgi:application
