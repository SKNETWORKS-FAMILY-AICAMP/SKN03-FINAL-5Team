import { SSMClient, GetParameterCommand } from '@aws-sdk/client-ssm';

/**
 * Fetches a parameter value from AWS SSM Parameter Store.
 *
 * @param {string} parameterName - The name of the parameter to fetch.
 * @returns {Promise<string>} - The value of the parameter.
 */
export async function getParameterValue(parameterName) {
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
