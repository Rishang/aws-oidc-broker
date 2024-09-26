## Creating Client

- Download the client config file [here](../assets/aws-oidc-keycloak.json "download"){target=_blank}

- Open Keycloak Admin Console

- Go to Clients tab. Create new client

- On Client Creation page, import the downloaded config.

![keycloak config](../assets/keycloak-config.gif)


## Configuration

The Client will be created with default url `http://localhost:5000/login` for Valid Redirect URIs, Base URL, and Web Origins

Update this to your actual domain url e.g `https://aws.example.com/login`

## AWS Config

- Go to AWS IAM Console and add an Identity Provider

- Use following configuration

    - **Provider Type:** OpenID Connect
    - **Provider URL:** OIDC Provider URL, must be a internet accessible TLS secured enpoint (e.g `https://auth.example.com/realms/master` for Keycloak)
    - **Audience:** Client ID issued by OIDC Provider (e.g `aws-oidc` Keycloak Client )

    !!! info

            Ensure you add Provider URL without any Trailing slash `/`

- Get Thumbprint once `Provider URL` is set. and Click `Add provider`

### Setup AWS using Cloudformation

We can use CloudFormation IaC tool for setup everything on the AWS side. This template will create OIDC provider based on inputs and two IAM roles - `keycloak-admin` and `keycloak-readonly` - which will be used as a identities for users login thru KeyCloak.

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: OIDC for KeyCloak

Parameters:
  KeycloakProviderUrl:
    Description: URL of KeyCloak OIDC provider without trailing slash and https://
    Type: String
    Default: "auth.example.com/realms/master"

  KeycloakClientId:
    Description: Client ID from KeyCloak
    Type: String
    Default: "aws-oidc"

  KeycloakThumbprint:
    Description: Thumbprint of keycloak TLS certificate
    Type: String

  SSOSessionTimeout:
    Description: Expiration of session tokens in seconds. Default is 4 hours.
    Type: Number
    Default: 14400

Resources:

  OidcProvider:
    Type: AWS::IAM::OIDCProvider
    Properties:
      ClientIdList:
        - !Ref KeycloakClientId
      ThumbprintList:
        - !Ref KeycloakThumbprint
      Url: !Sub "https://${KeycloakProviderUrl}"
    
  FederationRoleForAdminAccess:
    Type: AWS::IAM::Role
    Properties:
      Path: /
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AdministratorAccess
      MaxSessionDuration: !Ref SSOSessionTimeout
      RoleName: "keycloak-admin"
      Description: 'IAM role for full access thru keycloak'
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Condition:
              StringEquals:
                !Sub "${KeycloakProviderUrl}:aud: ${KeycloakClientId}"
            Action: sts:AssumeRoleWithWebIdentity
            Effect: Allow
            Principal:
              Federated: !Ref OidcProvider

  FederationRoleForReadOnlyAccess:
    Type: AWS::IAM::Role
    Properties:
      Path: /
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/ReadOnlyAccess
      MaxSessionDuration: !Ref SSOSessionTimeout
      RoleName: "keycloak-readonly"
      Description: 'IAM role for read only access thru keycloak'
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Condition:
              StringEquals:
                !Sub "${KeycloakProviderUrl}:aud: ${KeycloakClientId}"
            Action: sts:AssumeRoleWithWebIdentity
            Effect: Allow
            Principal:
              Federated: !Ref OidcProvider

Outputs:
  AdminAccessRoleArn:
    Value: !GetAtt FederationRoleForAdminAccess.Arn
  ReadOnlyRoleArn:
    Value: !GetAtt FederationRoleForReadOnlyAccess.Arn
```