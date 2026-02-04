# Beacon v2 Template UI

Beacon PI has been integrated with template UI(https://github.com/EGA-archive/beacon-template-ui) in this own repository. If you just want to deploy the container for beacon template UI or add it to the deployment of Beacon PI, please execute this command:

```bash
docker compose up -d --build templateUI
```

If you want to configure the UI edit the file [config.json](https://github.com/EGA-archive/beacon2-pi-api/tree/main/template-ui/src/config/config.json) or if you want to add credentials for log in, add an env file in the template-ui folder following [example](https://github.com/EGA-archive/beacon2-pi-api/tree/main/template-ui/env_example.txt).

Please, check the template UI repo for further details