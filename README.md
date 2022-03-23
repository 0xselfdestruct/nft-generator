# NFT Generator


## requirements
-   python (for generator)
-   node.js (for updating metadata files and uploading to ipfs)
-   ipfs client (for uploading assets)


## how to use
- drop your layer files into assets folder.
- open config.py and set options according to your collection.
- run **`python3 generate.py`** to generate collection.
- run **`npx yarn run update-metadata`** to generate CID and upload it all to ipfs.
