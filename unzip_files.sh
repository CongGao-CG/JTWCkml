#!/usr/bin/env bash
# extract every .zip in the zip directory into that singleTC folder
for z in zip/*.zip; do
    unzip -q "$z" -d singleTC
done
