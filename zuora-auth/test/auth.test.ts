import { AuthService } from "./AuthService";


async function testAuth(){
    const service = new AuthService();
    const loginResult = await service.login(
        'martini-accountant',
        'Martini!383940'
    )
    console.log(loginResult);
    // console.log(loginResult.getSignInUserSession().getIdToken().getJwtToken());
    //const credentials = await service.generateTemporaryCredentials(loginResult);
    //console.log(credentials);
    //const buckets = await listBuckets(credentials);
    //console.log(buckets);
}

testAuth();