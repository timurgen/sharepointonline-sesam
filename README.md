# sharepointonline-sesam
Sharepoint online source+sink for Sesam.io

system setup
```json
{
  "_id": "sharepoint-sink",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "SP_PASSWORD": "$SECRET(sp-password)",
      "SP_URL": "$ENV(sp-url)",
      "SP_USERNAME": "$ENV(sp-username)"
    },
    "image": "<docker image name>",
    "port": 5000
  }
}

```

pipe setup
```json
{
  "_id": "<pipe id>",
  "type": "pipe",
  "source": {
    "type": "dataset",
    "dataset": "<source dataset>"
  },
  "transform": [{
    "type": "dtl",
    "rules": {
      "default": [
        ["add", "::Key1", "_S.<source property key>"],
        ["add", "::Key2", "_S.<sourceproperty key>"],
        ["add", "::ListName", "<SharePointListName>"],
        ["add", "::ListItemEntityTypeFullName", "SP.Data.<SharePoint List Item>"],
        ["add", "::Keys",
          ["list", "Key1", "Key2"] <-- which attributes are we gonna send (we don't need to send all, SP will return error on unrecognized fields)
        ]
      ]
    }
  },
    {
    "type": "http",
    "system": "sharepoint-sink",
    "url": "/send-to-list"
  }],
  "pump": {
    "schedule_interval": 15
  }
}
```
