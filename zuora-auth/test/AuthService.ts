import {type CognitoUser} from '@aws-amplify/auth';
import {Amplify , Auth } from 'aws-amplify';

const awsRegion = 'us-east-1';
Amplify.configure({
  Aurh:{
    region:awsRegion,
    userPoolId: 'us-east-1_YK8w3RX35',
    userPoolWebClientId: '2ics6vsmjkp4qbdmha9gmsga3g',
    authenticationFlowType: 'USER_PASSWORD_AUTH'
  }
})

export class AuthService{

  public async login(userName: string, password: string){
    const result = await Auth.signIn(userName, password) as CognitoUser;
    return result;
  }
}