rm dist.zip
rm admin.zip

zip dist.zip docker-compose.yml
zip dist.zip src/Dockerfile
zip dist.zip src/index.js
zip dist.zip src/package*
zip dist.zip src/run.sh
zip dist.zip src/fake-flag.txt
printf "@ src/fake-flag.txt\n@=src/flag.txt\n" | zipnote -w dist.zip

zip admin.zip docker-compose.yml
zip admin.zip src/Dockerfile
zip admin.zip src/index.js
zip admin.zip src/package*
zip admin.zip src/run.sh
zip admin.zip src/flag.txt