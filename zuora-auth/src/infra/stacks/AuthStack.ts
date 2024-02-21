import {CfnOutput, Stack, StackProps } from 'aws-cdk-lib'
import { UserPool, UserPoolClient, CfnUserPoolGroup } from 'aws-cdk-lib/aws-cognito';
import { Role } from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

export class AuthStack extends Stack {

    public userPool: UserPool;
    private userPoolClient: UserPoolClient;
    private adminRole: Role;
    
    constructor(scope: Construct, id: string, props?: StackProps) {
        super(scope, id, props);

        this.createUserPool();
        this.createUserPoolClient();
        this.createAdminsGroup();
    }

    private createUserPool(){
        this.userPool = new UserPool(this, 'ZuoraUserPool', {
            selfSignUpEnabled: true,
            signInAliases: {
                username: true,
                email: true
            }
        });

        new CfnOutput(this, 'ZuoraUserPoolId', {
            value: this.userPool.userPoolId
        })
    }
    private createUserPoolClient(){
        this.userPoolClient = this.userPool.addClient('ZuoraUserPoolClient', {
            authFlows: {
                adminUserPassword: true,
                custom: true,
                userPassword: true,
                userSrp: true // Default values
            }
        });
        new CfnOutput(this, 'ZuoraUserPoolClientId', {
            value: this.userPoolClient.userPoolClientId
        })
    }

    
    private createAdminsGroup(){
        new CfnUserPoolGroup(this, 'ZuoraAdmins', {
            userPoolId: this.userPool.userPoolId,
            groupName: 'admins',
            // roleArn: this.adminRole.roleArn
        })
    }
}