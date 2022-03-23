from copyreg import constructor
import random
import json
import logging
import concurrent
import asyncio
import sys
from PIL import Image
from config import *


GENERATEDS = []
renderedCount = 0


def getWeights(attribute):
    weights = []
    for i in attribute:
        weights.append(i["weight"])
    return weights


def generateRandom():
    generated_attributes = {}
    for attribute in ASSETS:
        weights = getWeights(ASSETS[attribute])
        selected = random.choices(
            population=ASSETS[attribute], weights=weights, k=1)[0]
        generated_attributes[attribute] = selected
    return generated_attributes


def fillCollection():
    while len(GENERATEDS) < COLLECTION_SIZE:
        generated = generateRandom()
        print("generating:", str(len(GENERATEDS)))
        if generated in GENERATEDS:
            pass

        #################   RULES   #################
        # custom rules to fix asset conflicts

        # elif generated["Eyes"]["name"] == "x" and generated["Body"]["name"] == "x":
        #     pass
        # elif generated["Eyes"]["name"] == "x" and generated["Body"]["name"] == "x":
        #     pass
        # ...
        #################   /RULES  #################
        else:
            GENERATEDS.append(generated)


def generateMetadata(generated, id):
    attributes = []
    for trait in generated.keys():
        if(trait == "Background"):
            continue
        attributes.append({
            "trait_type": trait,
            "value": generated[trait]["name"],
        })

    metadata = {
        "name": NAME + " #" + str(id),
        "description": DESC,
        "image": str(id) + ".png",
        "attributes": attributes
    }
    return metadata


read_images = {}


def getImage(imagePath):
    image = Image.open(imagePath).convert(
        "RGBA").resize((WIDTH, HEIGHT), Image.ANTIALIAS)
    return image


def render(generated, id):
    global renderedCount
    log = logging.getLogger('run_blocking_tasks')
    main = getImage(generated["Background"]["file"])
    for i, trait in enumerate(generated.keys()):
        if(trait == "Background"):
            pass
        else:
            attr = getImage(generated[trait]["file"])
            main.paste(attr, (0, 0), attr)

    metadata = generateMetadata(generated, id)
    main.save("./OUT_PNG/" + str(id) + ".png", format="PNG")
    saveJson(metadata, "./OUT_JSON/" + str(id))
    log.info("Rendered: " + str(renderedCount))
    renderedCount += 1


def saveJson(data, out):
    metadataFile = open(out, "w+")
    metadataFile.write(json.dumps(data))
    metadataFile.close()


async def run(executor):
    log = logging.getLogger('run_blocking_tasks')
    log.info('starting')
    loop = asyncio.get_event_loop()
    blocking_tasks = []

    for i, generated in enumerate(GENERATEDS):
        # render(generated, i)
        blocking_tasks.append(loop.run_in_executor(
            executor, render, generated, i))

    log.info('waiting for executor tasks')
    completed, pending = await asyncio.wait(blocking_tasks)
    results = [t.result() for t in completed]
    log.info('results: {!r}'.format(results))


def runSync():
    for i, generated in enumerate(GENERATEDS):
        render(generated, i)


logging.basicConfig(
    level=logging.INFO,
    format='%(threadName)10s %(name)18s: %(message)s',
    stream=sys.stderr,
)

event_loop = asyncio.get_event_loop()
executor = concurrent.futures.ThreadPoolExecutor(max_workers=100)

try:
    fillCollection()
    event_loop.run_until_complete(
        run(executor)
    )
finally:
    event_loop.close()


# fillCollection()
# runSync()
