import { SSMClient, GetParameterCommand } from '@aws-sdk/client-ssm';

export async function getParameterStore(parameterName) {
  const client = new SSMClient({
    region: process.env.AWS_REGION | 'ap-northeast-2', // Ensure the region is correctly set in your environment
  });

  try {
    const command = new GetParameterCommand({
      Name: parameterName,
      WithDecryption: true,
    });

    const response = await client.send(command);

    return response.Parameter?.Value || '';
  } catch (error) {
    console.error(`Error fetching parameter "${parameterName}":`, error);
    throw error;
  }
}
