# smug-cli
Smugmug cli

This is a CLI written for some specific tasks, not general purpose. It is intended to be easy to add commands to. It runs on Linux, OSX and Windows using WSL. 

The smugmug API reference is [here](https://api.smugmug.com/api/v2/doc/index.html). Follow the steps to get an API key, and put it a file named ~/.smugcli/config.json, in the following format:

```
{
        "api_key": "<api-key>",
        "api_secret": "<api-secret>"
}
```

Run the authorize command, this will prompt for a browser session, and then put an access token in  ~/.smugcli/access.json, which will allow the rest of the commands to run.   

The commands are kind of a hodge-podge, the  list-albums, create-rename-list and bulk-rename were used for a renaming project for album name consistency.





