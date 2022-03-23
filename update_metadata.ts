import { readFile, writeFile } from "fs/promises";
import { create, globSource } from "ipfs-http-client";

const main = async () => {
  try {
    const client = create({
      url: "http://127.0.0.1:5001/",
    });

    for await (const file of client.addAll(globSource("./OUT_PNG", "**/*"), {
      wrapWithDirectory: true,
    })) {
      const jsonFileName = String(file.path).replace(".png", "");
      if (jsonFileName.length <= 0 || isNaN(Number(jsonFileName))) {
        return;
      }
      const jsonFile = await readFile(`./OUT_JSON/${jsonFileName}`, "utf-8");
      let jsonFileParsed = JSON.parse(jsonFile);
      jsonFileParsed.image = `ipfs://${file.cid.toString()}`;
      console.log(jsonFileParsed);
      await writeFile(
        `./OUT_JSON/${jsonFileName}`,
        JSON.stringify(jsonFileParsed)
      );
    }

  } catch (error) {
    console.log(error);
  }
};

main();
