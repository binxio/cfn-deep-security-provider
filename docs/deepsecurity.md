# Custom::DeepSecurity resource provider
The `Custom::DeepSecurity` resource provider for the standard resources from the [Deep Security](https://automation.deepsecurity.trendmicro.com/) API.

## Syntax
To create a DeepSecurity resource using your your AWS CloudFormation template, use the following syntax:

```yaml
  Client:
    Type: Custom::DeepSecurity<ResourceType> 
    Properties:
      Value:
        ### value as defined by the [DeepSecurity API](https://automation.deepsecurity.trendmicro.com/article/11_3/api-reference)

      Connection:
        URL: 'https://app.deepsecurity.trendmicro.com/api'
        ApiKeyParameterName: '/cfn-deep-security-provider/api-key'

      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-deep-security-provider'
```

## Supported Types
Supported DeepSecurity resource types are:

## Connection
In order to be able to manage the DeepSecurity resources, you need to obtain create an [API key](https://help.deepsecurity.trendmicro.com/create-api-key.html) and 
store it in the parameter store  under the name specified `ApiKeyParameterName`.

```
aws ssm put-parameter --name /cfn-deep-security-provider/api-key --type SecureString --value="$API_KEY"
```
If you store these credentials in a different location, please specify the correct parameter names.

## Value
You can specify the property for the specified resource:

    `Value` - All the attributes allowed from the [DeepSecurity API](https://auth0.com/docs/api/management/v2)

