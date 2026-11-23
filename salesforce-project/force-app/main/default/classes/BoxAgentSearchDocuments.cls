/**
 * Agentforce action for the search_documents tool in config/tools.json.
 * Seeded once by scripts/build_agent.py and never overwritten: implement the live Box and
 * Salesforce integration here. Until then it reports that the live adapter is missing,
 * so the agent cannot claim success.
 */
public with sharing class BoxAgentSearchDocuments {
    public class Request {
        @InvocableVariable(label='record_id' required=true)
        public String record_id;
        @InvocableVariable(label='document_type' required=true)
        public String document_type;
    }

    public class Response {
        @InvocableVariable(label='Result' description='JSON result matching the tool output schema, or an error object')
        public String result;
    }

    @InvocableMethod(label='Search documents' description='Find synthetic documents by metadata within the record folder. Never searches across records.')
    public static List<Response> run(List<Request> requests) {
        List<Response> responses = new List<Response>();
        for (Request request : requests) {
            Response response = new Response();
            response.result = JSON.serialize(new Map<String, Object>{
                'error' => 'live_adapter_not_implemented',
                'tool' => 'search_documents',
                'message' => 'This action is not connected to Box and Salesforce yet. No data was read or changed.'
            });
            responses.add(response);
        }
        return responses;
    }
}
