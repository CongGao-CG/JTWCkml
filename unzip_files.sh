#!/usr/bin/env bash
# extract every .zip in the zip directory into that singleTC folder
for z in zip/*.zip; do
    echo $z
    unzip -q "$z" -d singleTC
done
