#!/bin/bash

# Start the first process
python manage.py runserver 0.0.0.0:8000 &

sleep 5

# Start the second process
python zulip_listener.py &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?