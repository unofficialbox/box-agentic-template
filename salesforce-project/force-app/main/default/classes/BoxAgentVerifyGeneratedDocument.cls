/**
 * Agentforce action for the verify_generated_document tool in config/tools.json.
 * Seeded once by scripts/build_agent.py and never overwritten: implement the live Box and
 * Salesforce integration here. Until then it reports that the live adapter is missing,
 * so the agent cannot claim success.
 */
public with sharing class BoxAgentVerifyGeneratedDocument {
    public class Request {
        @InvocableVariable(label='record_id' required=true)
        public String record_id;
        @InvocableVariable(label='file_id' required=true)
        public String file_id;
        @InvocableVariable(label='job_id' required=true)
        public String job_id;
    }

    public class Response {
        @InvocableVariable(label='Result' description='JSON result matching the tool output schema, or an error object')
        public String result;
    }

    @InvocableMethod(label='Verify generated document' description='Verify the exact synthetic output ID and generation job for signature readiness; no signature action is implemented.')
    public static List<Response> run(List<Request> requests) {
        List<Response> responses = new List<Response>();
        for (Request request : requests) {
            Response response = new Response();
            response.result = JSON.serialize(new Map<String, Object>{
                'error' => 'live_adapter_not_implemented',
                'tool' => 'verify_generated_document',
                'message' => 'This action is not connected to Box and Salesforce yet. No data was read or changed.'
            });
            responses.add(response);
        }
        return responses;
    }
}
