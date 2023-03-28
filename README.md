# Heirloom Database

This software is a simple CRUD Webapp written in Python. Its purpose is to make it easy for families
to document their important physical objects so that their family history is not lost.

I built this software because someone in my family has a lot of important family artifacts in their
home, but the younger members of my family (including me) don't know about these artifacts or why
they're special. Someday, after everyone who currently knows about these artifacts has died, those
of us who remain alive will want to have a record of the most important items and their stories.

The design of the software is as simple as I could reasonably imagine. The Python Web server has
several pages and endpoints for creating, viewing, editing, and deleting Heirlooms. An Heirloom is
simply a directory on the server's filesystem containing a single image and a text file with a
description. There is no database or cache. The frontend uses almost no JavaScript and does not
require it in order to operate. When opened on a phone or tablet, the frontend supports photo
capture from the device's camera. A `Dockerfile` is available for easy deployment, but the server
runs in practically any environment with a Python interpreter. User authentication is provided with
HTTP Basic Auth, although only one user account is configurable, and the credentials must be shared
among users. This is a simple protection against low-effort attacks and provides a small amount of
privacy. The server does not keep any activity records for individual users.

## Installation

1. `pip install -r requirements.txt`
2. `cp auth.example.txt auth.txt` and edit `auth.txt` to contain your desired username and password

Then, either run on the host OS with:

3. `./main.py` (the server binds to port 8080)

Or run under Docker with:

3. `docker build -t heirloom-db .`
4. `docker run --name heirloom-db -v heirlooms:/app/heirlooms -p 8080:8080 heirloom-db:latest`

This server does not provide TLS. I recommend configuring a proper Web server as a reverse proxy in
front of `heirloom-db` for public-facing deployments.