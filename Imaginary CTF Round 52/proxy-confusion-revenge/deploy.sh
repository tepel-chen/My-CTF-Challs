mkdir dist
cp -R deno dist/
cp -R flask dist/
cp -R proxy dist/
cp compose.yml dist/
zip -r dist.zip dist 

mkdir admin
cp -R deno admin/
cp -R flask admin/
cp -R proxy admin/
cp compose-admin.yml admin/compose.yml
zip -r admin.zip admin

rm -rf dist
rm -rf admin