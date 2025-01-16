rm dist.zip
rm admin.zip

zip dist.zip compose.yml
zip dist.zip src/app.js
zip dist.zip src/package*
zip dist.zip src/index.html
zip dist.zip src/Dockerfile
zip dist.zip src/fake-flag.txt
printf "@ src/fake-flag.txt\n@=src/flag.txt\n" | zipnote -w dist.zip

zip admin.zip compose.yml
zip admin.zip src/app.js
zip admin.zip src/package*
zip admin.zip src/index.html
zip admin.zip src/Dockerfile
zip admin.zip src/flag.txt