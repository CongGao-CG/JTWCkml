#!/usr/bin/env bash
# extract every .zip in the zip directory, flattening all files into singleTC
for z in zip/*.zip; do
    echo $z
    unzip -joq "$z" -d singleTC
done

# Normalize all extracted file permissions.
find singleTC -type f -exec chmod 644 {} +
