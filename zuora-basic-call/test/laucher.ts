import {main} from '../src/services/zuoraCallOut';

const ticketNumber = process.env.TICKET_PARAMETER ?? '';
console.log("ticketNumber: ", process.env.AWS_REGION);

main({} as any, {} as any)