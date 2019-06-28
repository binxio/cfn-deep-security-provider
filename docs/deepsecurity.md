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
      ApiKeyParameterName: '/cfn-deep-security-provider/api_key'

    ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-deep-security-provider'
```

## ID lookup support
To create custom security policies in DeepSecurity, you can use existing rules. To ease this process we support lookup references as shown below:

```yaml
ContainerHostPolicy:
  Type: Custom::DeepSecurityPolicy
  Properties:
    Value:
      parentID: !Ref 'BasePolicy'
      name: !Sub '${Environment}ContainerHostPolicy"
      description: Policy for container instances in ${Environment}
      intrusionPrevention:
        state: detect
        ruleIDs:
          - '{{lookup "intrusionPreventionRule" "HTTP Protocol Decoding"}}'
          - '{{lookup "intrusionPreventionRule" "Identified Possible Ransomware File Rename Activity Over Network Share"}}'
          - '{{lookup "intrusionPreventionRule" "Identified Possible Ransomware File Extension Rename Activity Over Network Share"}}'
          - '{{lookup "intrusionPreventionRule" "Identified Usage Of PsExec Command Line Tool"}}'
```

the syntax to lookup an id, is:

```
{{lookup "<type-name>" "name-of-resource"}}
```
The lookup result in exactly one match.
## Supported Types`
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

