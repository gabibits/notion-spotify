## setup
- notion
  - go to https://www.notion.so/my-integrations
  - create an integration and obtain NOTION_TOKEN
  - database template: https://gabibits.notion.site/e413ef0faa954dc0b2239cba2de9ea9a?v=bed5c9b0e1a948e4b2b9b6c99ec2a9d9
    - NOTION_DATABASE_ID is the first part between /? -> e.g., e413ef0faa954dc0b2239cba2de9ea9a

- spotify
  - go to https://developer.spotify.com/
  - create an integration and obtain SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET


## run the script
```bash
#clone the repository
git clone https://github.com/gabibits/notion-spotify.git

# install dependencies
pip install -r requirements.txt

# fill the variables in .env

# run the script
python main.py
```

- to add entries in Notion, the script must be running
  
https://github.com/gabibits/notion-spotify/assets/78867705/b2a178fb-d9c2-4780-a8ae-5b5107bb2d49
