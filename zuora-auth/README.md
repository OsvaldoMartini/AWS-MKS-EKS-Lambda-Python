#  TS-Node Package
```bash
  node -r ts-node/register .\test\auth.test.ts
```

Cognito AWS CLI
ACTIVADE USER
``bash
 aws cognito-idp admin-set-user-password --user-pool-id us-east-1_YK8w3RX35 --username martini-accountant --password "Martini!383940" --permanent

  aws cognito-idp admin-set-user-password --user-pool-id us-east-1_VNsJaaFiq --username martini-accountant --password "Martini!383940" --permanent
```


# APIGatewayProxyEvent
 this Event contains all the information about this reques, including even including the cognito groups
 Let's Parse it

 Supposition only Admin can Delete Items
```typescript
  .... authorizer?.claims['cognito:groups']; 
```

# The snipped code
 ```typescript
export function hasAdminGroup(event: APIGatewayProxyEvent){
    const groups = event.requestContext.authorizer?.claims['cognito:groups'];
    if (groups) {
        return (groups as string).includes('admins');
    }
    return false;
}
```
