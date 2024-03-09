#!/bin/bash

# SPDX-FileCopyrightText: © 2024 Stacey Adams <stacey.belle.rose@gmail.com>
# SPDX-License-Identifier: MIT

mkdir -p /tmp/temp-monitor/
cd "$HOME"/projects/temp-monitor || exit
"$HOME"/projects/venv/bin/python3 ./main.py &
disown
echo $! > /tmp/temp-monitor/temp-monitor.pid

exit 0
