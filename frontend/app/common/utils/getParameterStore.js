import { SSMClient, GetParameterCommand } from '@aws-sdk/client-ssm';
import { fromContainerMetadata } from '@aws-sdk/credential-providers';

const client = new SSMClient({
  region: process.env.AWS_REGION || 'ap-northeast-2',
  credentials: fromContainerMetadata({
    maxRetries: 3, // Optional
    timeout: 0, // Optional
  }),
});

export async function getParameterStore(parameterName) {
  console.log(`Fetching parameter: ${parameterName}`);
  const command = new GetParameterCommand({
    Name: parameterName,
    WithDecryption: true,
  });

  try {
    const response = await client.send(command);
    console.log('Full response:', JSON.stringify(response, null, 2)); // 응답 로그 추가
    if (response.Parameter && response.Parameter.Value) {
      console.log('Parameter fetched successfully:', response.Parameter.Value);
      return response.Parameter.Value;
    } else {
      throw new Error('No value found for the parameter');
    }
  } catch (error) {
    console.error('Error fetching parameter:', error.message);
    console.error('Full error:', JSON.stringify(error, null, 2));
    return null;
  }
}
