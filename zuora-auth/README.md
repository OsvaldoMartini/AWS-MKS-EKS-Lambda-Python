#  TS-Node Package
```bash
  node -r ts-node/register .\test\auth.test.ts
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
