import { SSMClient, GetParameterCommand } from '@aws-sdk/client-ssm';

const ssmClient = new SSMClient({
  region: 'ap-northeast-2',
});

export function getParameterStore(parameterName) {
  console.log(`Fetching parameter: ${parameterName}`);
  const command = new GetParameterCommand({
    Name: parameterName,
    WithDecryption: true,
  });

  try {
    const response = ssmClient.send(command);
    console.log('Parameter fetched successfully:', response.Parameter.Value);
    console.log(response);
    return response;
  } catch (error) {
    console.error('Error fetching parameter:', error.message);
    console.error('Full error:', JSON.stringify(error, null, 2));
    return null;
  }
}
