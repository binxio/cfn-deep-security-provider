# Custom::DeepSecurityAWSCloudAccount resource provider
The `Custom::DeepSecurityAWSCloudAccount` resource provider for the AWS Cloud Account resource
from the [Deep Security](https://automation.deepsecurity.trendmicro.com/legacy-rest/11_3/index.html?env=dsaas#aws_accounts) 
Legacy API.

## Syntax
To create a DeepSecurity resource using your your AWS CloudFormation template, use the following syntax:

```yaml
  Client:
    Type: Custom::DeepSecurityAWSCloudAccount
    Properties:
      AWSAccountRequest:
        ### value as defined by the DeepSecurity Legacy API (AddAwsAccountRequest)(https://automation.deepsecurity.trendmicro.com/legacy-rest/11_3/index.html?env=dsaas#create_aws_account) 
        ### or (UpdateAwsAccountRequest)(https://automation.deepsecurity.trendmicro.com/legacy-rest/11_3/index.html?env=dsaas#modify_aws_account)
        crossAccountRole:
          roleArn: String
          externalId: String
        "workspacesEnabled": Boolean
      }

      Connection:
        URL: 'https://app.deepsecurity.trendmicro.com/rest'
        UserParameterName: '/cfn-deep-security-provider/user'
        PasswordParameterName: '/cfn-deep-security-provider/password'
        TenantParameterName: '/cfn-deep-security-provider/tenant'

      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-deep-security-provider'
```

## Connection
In order to be able to manage the DeepSecurity resources, you need to [add an user] (https://help.deepsecurity.trendmicro.com/user-management.html?cshid=administration_users#Create_new_users_) and and store the username, password and tenant name in the parameter store.

```
aws ssm put-parameter --name /cfn-deep-security-provider/user --type SecureString --value="$USERNAME"
aws ssm put-parameter --name /cfn-deep-security-provider/password --type SecureString --value="$PASSWORD"
aws ssm put-parameter --name /cfn-deep-security-provider/tenant --type SecureString --value="$TENANT"
```
If you store these credentials in a different parameter, please specify the correct parameter names.

## AWSAccountRequest
You can specify the properties as defined by the DeepSecurity Legacy API
[AddAwsAccountRequest](https://automation.deepsecurity.trendmicro.com/legacy-rest/11_3/index.html?env=dsaas#create_aws_account) or 
[UpdateAwsAccountRequest](https://automation.deepsecurity.trendmicro.com/legacy-rest/11_3/index.html?env=dsaas#modify_aws_account).

We recommend the crossAccountRole configuration to avoid hardcoded access keys in your 
CloudFormation template, as shown in the template snippet below. Note that this snippet depends on
the [Custom::Secret](https://github.com/binxio/cfn-secret-provider) provider.

```
DeepSecurityAWSCloudAccount:
  Type: Custom::DeepSecurityAWSCloudAccount
  DependsOn:
    - CFNDeepSecurityProvider
  Properties:
    AWSAccountRequest:
      crossAccountRole:
        roleArn: !GetAtt 'DeepSecurityRole.Arn'
        externalId: !GetAtt 'StsExternalId.Secret'
    ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-deep-security-provider'

StsExternalId:
  Type: Custom::Secret
  Properties:
    Name: /cfn-deep-security-provider/sts-external-id
    Description: deep security STS external id
    Alphabet: '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    Length: 32
    RefreshOnUpdate: false
    ReturnSecret: true
    ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:binxio-cfn-secret-provider'

DeepSecurityRole:
  Type: AWS::IAM::Role
  Properties:
    RoleName: DeepSecurity
    ManagedPolicyArns:
      - !Ref 'DeepSecurityPolicy'
    AssumeRolePolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Principal:
            AWS: arn:aws:iam::147995105371:root
          Action:
            - sts:AssumeRole
          Condition:
            StringEquals:
              sts:ExternalId:
                - !GetAtt 'StsExternalId.Secret'

DeepSecurityPolicy:
  Type: AWS::IAM::ManagedPolicy
  Properties:
    ManagedPolicyName: DeepSecurityPolicy
    Description: TrendMicro DeepSecurity access policy
    PolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Sid: '1'
          Effect: Allow
          Action:
            - ec2:DescribeRegions
            - ec2:DescribeImages
            - ec2:DescribeInstances
            - ec2:DescribeTags
            - ec2:DescribeAvailabilityZones
            - ec2:DescribeSecurityGroups
            - ec2:DescribeSubnets
            - ec2:DescribeVpcs
            - iam:ListAccountAliases
          Resource:
            - '*'
        - Sid: '2'
          Effect: Allow
          Action:
            - iam:GetRole
            - iam:GetRolePolicy
          Resource:
            - arn:aws:iam::*:role/DeepSecurity*
        - Sid: '3'
          Effect: Allow
          Action:
            - workspaces:DescribeWorkspaces
            - workspaces:DescribeWorkspaceDirectories
            - workspaces:DescribeWorkspaceBundles
            - workspaces:DescribeTags
          Resource:
            - '*'
```
