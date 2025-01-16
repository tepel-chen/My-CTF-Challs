#!/bin/bash

while true; do
  deno run --allow-net --allow-env server.ts
  sleep 1
done