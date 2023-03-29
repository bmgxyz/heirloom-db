#!/usr/bin/env python3

from aiohttp import web
from aiohttp_basicauth import BasicAuthMiddleware
import jinja2
import aiohttp_jinja2
import os
import sys
import random
import shutil

SCRIPT_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
HEIRLOOMS_DIR = os.path.join(SCRIPT_DIR, "heirlooms")
config = {}
with open(os.path.join(SCRIPT_DIR, "config.txt"), "r") as config_file:
    for line in config_file:
        key, value = line.rstrip().split("=")
        config[key] = value
USERNAME = config["username"]
PASSWORD = config["password"]
URL_SLUG = config["urlSlug"]
HOST = config["host"]
PORT = int(config["port"])


def heirloom_exists(heirloom_id: str):
    heirloom_path = os.path.join(HEIRLOOMS_DIR, heirloom_id)
    return os.path.isdir(heirloom_path)


async def index(request):
    heirlooms = os.listdir(HEIRLOOMS_DIR)
    heirlooms = list(filter(lambda h: os.path.isdir(
        os.path.join(HEIRLOOMS_DIR, h)), heirlooms))
    context = {"heirlooms": heirlooms, "urlSlug": URL_SLUG}
    response = aiohttp_jinja2.render_template(
        "index.html", request, context=context)
    return response


async def create_heirloom(request):
    if request.method == "GET":
        context = {"urlSlug": URL_SLUG}
        response = aiohttp_jinja2.render_template(
            "create_heirloom.html", request, context=context)
        return response
    elif request.method == "POST":
        post_data = await request.post()
        if "description" not in post_data.keys() or "image" not in post_data.keys():
            return web.HTTPBadRequest()
        description_data = post_data["description"]
        image_data = post_data["image"].file.read()
        new_heirloom_id = None
        while new_heirloom_id is None or os.path.isdir(os.path.join(new_heirloom_path)):
            new_heirloom_id = str(random.randint(1e9, 1e10))
            new_heirloom_path = os.path.join(HEIRLOOMS_DIR, new_heirloom_id)
        os.makedirs(new_heirloom_path)
        description_path = os.path.join(new_heirloom_path, "description")
        image_path = os.path.join(new_heirloom_path, "image")
        with open(description_path, "w") as description_file:
            description_file.write(description_data)
        with open(image_path, "wb") as image_file:
            image_file.write(image_data)
        return web.HTTPFound(f"{URL_SLUG}/view_heirloom?id={new_heirloom_id}")


async def view_heirloom(request):
    if "id" not in request.query.keys():
        return web.HTTPBadRequest()
    heirloom_id = request.query["id"]
    if not heirloom_exists(heirloom_id):
        return web.HTTPNotFound()
    description = open(os.path.join(
        HEIRLOOMS_DIR, heirloom_id, "description"), "r").read()
    context = {"id": heirloom_id,
               "description": description, "urlSlug": URL_SLUG}
    response = aiohttp_jinja2.render_template(
        "view_heirloom.html", request, context=context)
    return response


async def edit_heirloom(request):
    if request.method == "GET":
        if "id" not in request.query.keys():
            return web.HTTPBadRequest()
        heirloom_id = request.query["id"]
        if not heirloom_exists(heirloom_id):
            return web.HTTPNotFound()
        description = open(os.path.join(
            HEIRLOOMS_DIR, heirloom_id, "description"), "r").read()
        context = {"id": heirloom_id,
                   "description": description, "urlSlug": URL_SLUG}
        response = aiohttp_jinja2.render_template(
            "edit_heirloom.html", request, context=context)
        return response
    elif request.method == "POST":
        post_data = await request.post()
        if "id" not in post_data.keys() or "description" not in post_data.keys() or "image" not in post_data.keys():
            return web.HTTPBadRequest()
        heirloom_id = post_data["id"]
        if not heirloom_exists(heirloom_id):
            return web.HTTPNotFound()
        description_data = post_data["description"]
        image_data = None
        if post_data["image"] != bytearray(b''):
            image_data = post_data["image"].file.read()
        heirloom_path = os.path.join(HEIRLOOMS_DIR, heirloom_id)
        description_path = os.path.join(heirloom_path, "description")
        with open(description_path, "w") as description_file:
            description_file.write(description_data)
        if image_data is not None:
            image_path = os.path.join(heirloom_path, "image")
            with open(image_path, "wb") as image_file:
                image_file.write(image_data)
        return web.HTTPFound(f"{URL_SLUG}/view_heirloom?id={heirloom_id}")


async def delete_heirloom(request):
    if request.method == "GET":
        if "id" not in request.query.keys():
            return web.HTTPBadRequest()
        heirloom_id = request.query["id"]
        if not heirloom_exists(heirloom_id):
            return web.HTTPNotFound()
        context = {"id": heirloom_id, "urlSlug": URL_SLUG}
        response = aiohttp_jinja2.render_template(
            "delete_heirloom.html", request, context=context)
        return response
    elif request.method == "POST":
        post_data = await request.post()
        if "id" not in post_data.keys():
            return web.HTTPBadRequest()
        heirloom_id = post_data["id"]
        if not heirloom_exists(heirloom_id):
            return web.HTTPNotFound()
        heirloom_path = os.path.join(HEIRLOOMS_DIR, heirloom_id)
        shutil.rmtree(heirloom_path)
        return web.HTTPFound(f"{URL_SLUG}/")


async def image_handler(request):
    heirloom_id = request.match_info["image"]
    image_path = os.path.join(HEIRLOOMS_DIR, heirloom_id, "image")
    if os.path.isfile(image_path):
        return web.FileResponse(image_path, headers=[("Cache-Control", "no-cache")])
    else:
        return web.HTTPNotFound()

auth = BasicAuthMiddleware(username=USERNAME, password=PASSWORD)
app = web.Application(middlewares=[auth], client_max_size=16777216)
app.add_routes([web.get(URL_SLUG + "/create_heirloom", create_heirloom, allow_head=False),
                web.post(URL_SLUG + "/create_heirloom", create_heirloom),
                web.get(URL_SLUG + "/view_heirloom",
                        view_heirloom, allow_head=False),
                web.get(URL_SLUG + "/edit_heirloom",
                        edit_heirloom, allow_head=False),
                web.post(URL_SLUG + "/edit_heirloom", edit_heirloom),
                web.get(URL_SLUG + "/delete_heirloom",
                        delete_heirloom, allow_head=False),
                web.post(URL_SLUG + "/delete_heirloom", delete_heirloom),
                web.get(URL_SLUG + "/{image}",
                        image_handler, allow_head=False),
                web.get(URL_SLUG + "/", index),
                web.get(URL_SLUG, index)])
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(
    os.path.join(SCRIPT_DIR, "templates")))

if __name__ == "__main__":
    web.run_app(app, host=HOST, port=PORT)
