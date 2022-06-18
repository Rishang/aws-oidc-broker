### KEYCLOAK_CLIENT_ID *

- Default: ""
- Description:  OIDC App Client ID

### KEYCLOAK_CLIENT_SECRET *

- Default: ""
- Description: OIDC App Client Secret

### KEYCLOAK_ISSUER *

- Default: ""
- Description: Its the base url for the .well-known path. Usually all providers service their .well-known paths at `<issuer-url>/.well-known`
- Example:
    - Keycloak Quarkus: https://localhost:8080/realms/master
       

### APP_SECRET

- Defalt: "!apppasswd"
- Description: Optional env variable to set encrytion secret

## TITLE

- Defalt: "Example"
- Description: Title of the Broker Page